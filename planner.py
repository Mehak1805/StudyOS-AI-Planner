import pandas as pd
import math


def generate_schedule(df, days, hours_per_day, crash_mode=False):
    """
    Smart scheduler:
    - Each topic gets exactly ONE study slot
    - Hard topics go first, then Medium, then Easy
    - Revision slots are added at END of each day (not after every topic)
    - Topics are spread across days so each day has a MIX of topics
    - If crash_mode: skip revision, cram as many topics per day as possible
    """

    df = df.copy()
    df["final_priority"] = df["user_priority"].fillna(df["ai_priority"])

    df_to_study = df[df["known"] != 1].sort_values(
        ["final_priority", "difficulty"],
        ascending=[False, False]
    ).reset_index(drop=True)

    df_known = df[df["known"] == 1]

    total_topics = len(df_to_study)
    if total_topics == 0:
        return pd.DataFrame(columns=["Day", "Block", "Subject", "Topic", "Difficulty", "Focus", "Type"])

    schedule = []

    # In crash mode: pack as many topics per day as possible (each = 1 slot)
    # In normal mode: 1 topic per hour slot + end-of-day revision of hardest topic that day
    # Each topic = 1 slot regardless of difficulty (user controls hours_per_day)

    # Distribute topics across days
    # slots_per_day: in normal mode leave last slot for revision; in crash mode use all
    if crash_mode:
        slots_per_day = hours_per_day
    else:
        slots_per_day = max(1, hours_per_day - 1)  # reserve 1 slot for revision

    total_slots = days * slots_per_day
    topics_to_schedule = df_to_study.head(total_slots)  # can only fit this many

    # Build day-by-day schedule
    topic_idx = 0
    topics_list = topics_to_schedule.to_dict("records")

    for day in range(1, days + 1):
        day_topics = []

        # Fill study slots for this day
        for slot in range(1, slots_per_day + 1):
            if topic_idx >= len(topics_list):
                break
            t = topics_list[topic_idx]
            topic_idx += 1
            day_topics.append(t)
            schedule.append({
                "Day":        f"Day {day}",
                "Block":      f"Hour {slot}",
                "Subject":    t["subject"],
                "Topic":      t["topic"],
                "Difficulty": t["difficulty"],
                "Focus":      t["difficulty"],
                "Type":       "Study",
            })

        if not day_topics:
            break

        # End-of-day revision: revise the HARDEST topic studied today
        if not crash_mode:
            hardest = max(day_topics, key=lambda x: x["ai_priority"])
            schedule.append({
                "Day":        f"Day {day}",
                "Block":      f"Hour {hours_per_day}",
                "Subject":    hardest["subject"],
                "Topic":      hardest["topic"],
                "Difficulty": hardest["difficulty"],
                "Focus":      "Revise",
                "Type":       "Revision",
                "exam_prob": int(hardest.get("exam_prob") or 50) if str(hardest.get("exam_prob","50")) not in ("nan","None","") else 50,
            })

    # Topics that didn't fit
    skipped_start = topic_idx
    for _, t in df_to_study.iloc[skipped_start:].iterrows():
        schedule.append({
            "Day":        "Didn't Fit ⚠",
            "Block":      "—",
            "Subject":    t["subject"],
            "Topic":      t["topic"],
            "Difficulty": t["difficulty"],
            "Focus":      "Overflow",
            "Type":       "Overflow",
            "exam_prob": int(t.get("exam_prob") or 50) if str(t.get("exam_prob","50")) not in ("nan","None","") else 50,
        })

    # Already known
    for _, t in df_known.iterrows():
        schedule.append({
            "Day":        "Already Known ✓",
            "Block":      "—",
            "Subject":    t["subject"],
            "Topic":      t["topic"],
            "Difficulty": t["difficulty"],
            "Focus":      "Skip",
            "Type":       "Known",
        })

    return pd.DataFrame(schedule)