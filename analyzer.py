import pandas as pd
from database import get_knowledge


def detect_from_kb(subject, topic, kb):
    t = topic.lower()
    s = subject.lower()

    # 1. Try exact subject match first
    subject_matches = kb[kb["subject"] == s]
    for _, row in subject_matches.iterrows():
        if row["keyword"] in t:
            return row["difficulty"], row["score"], f"Matched '{row['keyword']}' in {s}"

    # 2. Try general keywords (catch-all regardless of subject)
    general = kb[kb["subject"] == "general"]
    for _, row in general.iterrows():
        if row["keyword"] in t:
            return row["difficulty"], row["score"], f"General keyword '{row['keyword']}'"

    # 3. Fuzzy: try any subject's keywords (cross-subject knowledge)
    for _, row in kb.iterrows():
        if row["keyword"] in t and len(row["keyword"]) > 4:
            return row["difficulty"], row["score"], f"Cross-subject match '{row['keyword']}' from {row['subject']}"

    return None, None, "Fallback used"


def fallback_rule(topic):
    words = topic.split()
    n = len(words)

    # Heuristic: longer topic names tend to be more specific/complex
    if n <= 2:
        return "Easy", 1
    elif n <= 5:
        return "Medium", 2
    else:
        return "Hard", 3


def analyze_topics(rows):
    # rows = [(id, subject, topic, known), ...]
    df = pd.DataFrame(rows, columns=["id", "subject", "topic", "known"])

    kb = pd.DataFrame(get_knowledge(), columns=["subject", "keyword", "difficulty", "score", "exam_prob"])

    diffs = []
    explanations = []

    for _, r in df.iterrows():
        d, s, exp = detect_from_kb(r["subject"], r["topic"], kb)

        if d is None:
            d, s = fallback_rule(r["topic"])
            exp = f"Fallback heuristic ({len(r['topic'].split())} words)"

        diffs.append((d, s))
        explanations.append(exp)

    df["difficulty"] = [d[0] for d in diffs]
    df["difficulty_score"] = [d[1] for d in diffs]

    weights = df["subject"].value_counts(normalize=True)
    df["subject_weight"] = df["subject"].map(weights)

    df["ai_priority"] = (
        df["difficulty_score"] * 0.6 +
        df["subject_weight"] * 3
    )

    df["estimated_hours"] = (
        df["difficulty_score"] * 2 +
        df["subject_weight"] * 4
    ).round(1)

    # Minimum 0.5 hours so division doesn't blow up
    df["estimated_hours"] = df["estimated_hours"].clip(lower=0.5)

    df["explanation"] = explanations
    df["user_priority"] = None
    df["today_priority"] = df["ai_priority"] + (1 / df["estimated_hours"])

    return df