import streamlit as st
import pandas as pd
import io

from database import (
    init_db, add_topic, get_topics, clear_topics,
    mark_topic_known, mark_all_known, reset_knowledge,
    save_study_plan, get_saved_plans, delete_saved_plan
)
from analyzer import analyze_topics
from planner import generate_schedule
from pdf_parser import extract_topics_from_pdf
from export_pdf import create_pdf

st.set_page_config(
    page_title="StudyOS — AI Planner",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    box-sizing: border-box;
}
.stApp { background: #05070F; }
.block-container { padding: 2rem 3rem 5rem !important; max-width: 1300px !important; }
#MainMenu, footer, header { visibility: hidden; }

.hero-wrap { padding: 1.2rem 0 1rem; border-bottom: 1px solid #0D1220; margin-bottom: 1.6rem; }
.hero-title {
    font-size: 2.8rem; font-weight: 800; letter-spacing: -0.04em; line-height: 1;
    background: linear-gradient(90deg, #00F5FF 0%, #BF5AF2 50%, #FF6B6B 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub {
    color: #3D4F6B; font-size: 0.78rem; margin-top: 0.4rem;
    letter-spacing: 0.14em; text-transform: uppercase; font-family: 'DM Mono', monospace !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 3px; background: #080C18 !important; border-radius: 14px;
    padding: 5px; border: 1.5px solid #0D1220; margin-bottom: 1.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 10px !important;
    color: #3D4F6B !important; font-weight: 700 !important;
    font-size: 0.9rem !important; padding: 10px 28px !important;
}
.stTabs [aria-selected="true"] {
    background: #0D1527 !important; color: #C8D8F0 !important;
}

.sec-label {
    font-size: 0.66rem; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: #3D4F6B; margin-bottom: 0.6rem;
    font-family: 'DM Mono', monospace !important;
}

.stTextInput > div > div > input {
    background: #080C18 !important; border: 1.5px solid #0D1220 !important;
    border-radius: 12px !important; color: #C8D8F0 !important;
    font-size: 0.92rem !important; padding: 0.6rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00F5FF !important; box-shadow: 0 0 0 3px rgba(0,245,255,0.08) !important;
}
.stTextInput > div > div > input::placeholder { color: #1E2D45 !important; }
.stTextInput label { display: none !important; }

.stNumberInput > div > div > input {
    background: #080C18 !important; border: 1.5px solid #0D1220 !important;
    border-radius: 12px !important; color: #C8D8F0 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #00C6FF 0%, #7B2FFF 100%) !important;
    color: #fff !important; border: none !important; border-radius: 12px !important;
    font-weight: 700 !important; font-size: 0.86rem !important;
    padding: 0.55rem 1.3rem !important;
    box-shadow: 0 4px 20px rgba(0,198,255,0.15) !important;
    transition: opacity 0.15s, transform 0.1s !important;
}
.stButton > button:hover {
    opacity: 0.85 !important; transform: translateY(-1px) !important;
}
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #FF6B6B 0%, #BF5AF2 50%, #00C6FF 100%) !important;
    color: #fff !important; border: none !important; border-radius: 14px !important;
    font-weight: 800 !important; font-size: 1rem !important; padding: 0.8rem 2rem !important;
    box-shadow: 0 6px 30px rgba(191,90,242,0.3) !important;
}

.badge {
    display: inline-block; font-size: 0.62rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; padding: 2px 9px;
    border-radius: 30px; font-family: 'DM Mono', monospace !important; vertical-align: middle;
}
.badge-Easy   { background:rgba(0,255,136,0.1);  color:#00FF88; border:1px solid rgba(0,255,136,0.25); }
.badge-Medium { background:rgba(255,170,0,0.1);  color:#FFAA00; border:1px solid rgba(255,170,0,0.3); }
.badge-Hard   { background:rgba(255,60,120,0.1); color:#FF3C78; border:1px solid rgba(255,60,120,0.3); }
.badge-Revise { background:rgba(0,245,255,0.08); color:#00F5FF; border:1px solid rgba(0,245,255,0.25); }
.badge-Known  { background:rgba(30,45,69,0.4);   color:#3D4F6B; border:1px solid #0D1220; }
.badge-Crash  { background:rgba(255,107,107,0.12);color:#FF6B6B;border:1px solid rgba(255,107,107,0.3);}

.stat-card {
    background: #080C18; border: 1.5px solid #0D1220; border-radius: 16px;
    padding: 1rem; text-align: center; position: relative; overflow: hidden;
}
.stat-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: var(--accent, #00F5FF);
}
.stat-num { font-size:1.8rem; font-weight:800; color:var(--accent,#00F5FF); line-height:1; }
.stat-lbl { font-size:0.65rem; color:#3D4F6B; margin-top:6px; text-transform:uppercase; letter-spacing:0.1em; font-family:'DM Mono',monospace; }

.subject-header {
    font-size: 0.66rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase;
    color: #3D4F6B; margin: 1rem 0 0.4rem; font-family: 'DM Mono', monospace !important;
    display: flex; align-items: center; gap: 10px;
}
.subject-header::after { content:''; flex:1; height:1px; background:#0A0E1A; }

.topic-card {
    background: #080C18; border: 1.5px solid #0D1220; border-radius: 12px;
    padding: 0.75rem 1rem; margin-bottom: 4px; transition: border-color 0.2s;
}
.topic-card:hover { border-color: #162036; }
.topic-card.known { opacity:0.3; border-color:#080C18; }
.topic-name { font-weight:700; font-size:0.88rem; color:#C8D8F0; }
.topic-meta { font-size:0.68rem; color:#3D4F6B; margin-top:3px; font-family:'DM Mono',monospace; }

.day-header {
    display: flex; align-items: center; gap: 12px; margin: 1.4rem 0 0.6rem;
}
.day-dot {
    width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
    background: var(--dc, #00F5FF); box-shadow: 0 0 10px var(--dc, #00F5FF);
}
.day-title {
    font-size: 0.8rem; font-weight: 800; color: #C8D8F0;
    letter-spacing: 0.08em; text-transform: uppercase;
}
.day-sub { font-size: 0.66rem; color: #3D4F6B; font-family: 'DM Mono', monospace; }
.day-line { flex:1; height:1px; background:#0A0E1A; }

.slot {
    display: flex; align-items: center; gap: 14px;
    background: #080C18; border: 1.5px solid #0D1220;
    border-radius: 11px; padding: 0.7rem 1rem; margin-bottom: 4px;
}
.slot.hard   { border-left: 3px solid #FF3C78; }
.slot.medium { border-left: 3px solid #FFAA00; }
.slot.easy   { border-left: 3px solid #00FF88; }
.slot.revise { border-left: 3px solid #00F5FF; background:#05080F; }
.slot.known-row    { border-left: 3px solid #0D1220; opacity:0.25; }
.slot.overflow-row { border-left: 3px solid #FF6B6B; opacity:0.5; }
.slot-num   { font-family:'DM Mono',monospace; font-size:0.66rem; color:#1E2D45; min-width:52px; flex-shrink:0; }
.slot-topic { font-weight:700; font-size:0.88rem; color:#C8D8F0; }
.slot-sub   { font-size:0.68rem; color:#1E2D45; margin-top:2px; }

.info-box {
    background: #080C18; border: 1.5px solid #0D1220; border-radius: 16px;
    padding: 1.2rem 1.4rem; margin-bottom: 1.4rem;
    display: flex; gap: 2rem; flex-wrap: wrap; align-items: center;
}

.warn-box {
    background: rgba(255,107,107,0.08); border: 1.5px solid rgba(255,107,107,0.25);
    border-radius: 12px; padding: 0.8rem 1.2rem; margin-bottom: 1rem;
    font-size: 0.86rem; color: #FF6B6B; font-weight: 600; display:flex; align-items:center; gap:10px;
}
.ok-box {
    background: rgba(0,255,136,0.06); border: 1.5px solid rgba(0,255,136,0.2);
    border-radius: 12px; padding: 0.8rem 1.2rem; margin-bottom: 1rem;
    font-size: 0.86rem; color: #00FF88; font-weight: 600; display:flex; align-items:center; gap:10px;
}

.overflow-head {
    font-size: 0.7rem; font-weight: 700; color: #FF6B6B; letter-spacing: 0.12em;
    text-transform: uppercase; margin: 1.4rem 0 0.4rem; font-family:'DM Mono',monospace;
    display:flex; align-items:center; gap:10px;
}
.overflow-head::after { content:''; flex:1; height:1px; background:rgba(255,107,107,0.15); }

.stSelectbox > div > div {
    background: #080C18 !important; border: 1.5px solid #0D1220 !important;
    border-radius: 10px !important; color: #C8D8F0 !important;
}
.stToggle label { color:#3D4F6B !important; }
[data-testid="stFileUploader"] section {
    background: #080C18 !important; border: 1.5px dashed #12192E !important; border-radius: 14px !important;
}
.stAlert { border-radius: 12px !important; }
hr { border-color: #0A0E1A !important; margin: 1rem 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #05070F; }
::-webkit-scrollbar-thumb { background: #0D1220; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

init_db()

# ── Helpers ──────────────────────────────────────────────────────────────────
def badge(level):
    return f'<span class="badge badge-{level}">{level}</span>'

def day_color(i):
    palette = ["#00F5FF","#BF5AF2","#FF6B6B","#FFAA00","#00FF88","#FF8E53","#5AF2C8","#FF5AF2"]
    return palette[i % len(palette)]

def diff_class(diff):
    return {"Hard": "hard", "Medium": "medium", "Easy": "easy"}.get(diff, "medium")

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">StudyOS</div>
    <div class="hero-sub">AI Study Planner · Hard topics first · Every topic gets its slot</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📚  Topics", "🗺  Study Roadmap", "💾  Saved Plans"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Topics
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # CLEAR ON FIRST LOAD
    if "session_started" not in st.session_state:
        clear_topics()
        st.session_state.session_started = True

    if st.session_state.get("pdf_upload_msg"):
        st.success(st.session_state.pop("pdf_upload_msg"))

    # ── Add manually ─────────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">Add Topic Manually</div>', unsafe_allow_html=True)
    with st.form("add_topic_form", clear_on_submit=True):
        col_s, col_t, col_btn = st.columns([2, 3, 1])
        subject_input = col_s.text_input("s", placeholder="Subject  (e.g. DBMS, Physics)", label_visibility="collapsed")
        topic_input   = col_t.text_input("t", placeholder="Topic  (e.g. Normalization, Gravitation)", label_visibility="collapsed")
        add_submitted = col_btn.form_submit_button("＋ Add", use_container_width=True)

    if add_submitted:
        s, t = subject_input.strip(), topic_input.strip()
        if s and t:
            add_topic(s, t)
            st.session_state.pop("analysis_df", None)
            st.session_state.pop("plan", None)
            st.rerun()
        else:
            st.warning("⚠️ Fill in both Subject and Topic.")

    st.markdown("---")

    # ── PDF Upload ────────────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">Upload Syllabus PDF</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    if uploaded is None:
        st.session_state.pop("last_uploaded_id", None)
        st.session_state.pop("pdf_result", None)

    if uploaded is None:
        st.session_state.pop("last_uploaded_id", None)
        st.session_state.pop("pdf_result", None)

    if uploaded is not None:
        file_id = f"{uploaded.name}_{uploaded.size}"
        if st.session_state.get("last_uploaded_id") != file_id:
            with st.spinner("🔍 Extracting topics from PDF…"):
                try:
                    result = extract_topics_from_pdf(uploaded)
                    st.session_state["last_uploaded_id"] = file_id
                    st.session_state["pdf_result"] = result
                except Exception as e:
                    st.error(f"❌ PDF parse failed: {e}")
                    st.session_state.pop("pdf_result", None)

        result = st.session_state.get("pdf_result")
        if result:
            topics_list  = result["topics"]
            subject_name = result["subject"]
            if topics_list:
                st.info(f"📄 Found **{len(topics_list)} topics** from **{subject_name}**")
                if st.button(f"✅ Add all {len(topics_list)} topics", use_container_width=True):
                    clear_topics()
                    for t in topics_list:
                        add_topic(subject_name, t)
                    st.session_state.pop("analysis_df", None)
                    st.session_state.pop("pdf_result", None)
                    st.session_state.pop("plan", None)
                    st.session_state["pdf_upload_msg"] = f"✅ Added **{len(topics_list)} topics** from **{subject_name}**"
                    st.rerun()
            else:
                st.error("❌ No topics found — add manually.")
                st.session_state.pop("pdf_result", None)

    st.markdown("---")

    # ── Topic list ────────────────────────────────────────────────────────────
    rows = get_topics()

    if not rows:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#1E2D45;font-size:0.9rem">
            No topics yet — add above or upload a PDF ☝️
        </div>""", unsafe_allow_html=True)
    else:
        if "analysis_df" not in st.session_state:
            with st.spinner("Analysing topics…"):
                st.session_state.analysis_df = analyze_topics(rows)

        df = st.session_state.get("analysis_df")
        if df is not None and not df.empty:

            total   = len(df)
            n_easy  = int((df["difficulty"] == "Easy").sum())
            n_med   = int((df["difficulty"] == "Medium").sum())
            n_hard  = int((df["difficulty"] == "Hard").sum())
            n_known = int((df["known"] == 1).sum())
            est_hrs = float(df[df["known"] != 1]["estimated_hours"].sum())

            s_cols = st.columns(6)
            for col, (num, lbl, color) in zip(s_cols, [
                (total,            "Topics",     "#00F5FF"),
                (n_easy,           "Easy",       "#00FF88"),
                (n_med,            "Medium",     "#FFAA00"),
                (n_hard,           "Hard",       "#FF3C78"),
                (n_known,          "Known",      "#3D4F6B"),
                (f"{est_hrs:.1f}h","Study Time", "#BF5AF2"),
            ]):
                col.markdown(f"""
                <div class="stat-card" style="--accent:{color}">
                    <div class="stat-num">{num}</div>
                    <div class="stat-lbl">{lbl}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            fc1, fc2, _ = st.columns([2, 2, 4])
            subjects    = ["All"] + sorted(df["subject"].unique().tolist())
            diff_filter = fc1.selectbox("Difficulty", ["All","Hard","Medium","Easy"], label_visibility="collapsed")
            sub_filter  = fc2.selectbox("Subject", subjects, label_visibility="collapsed")

            fdf = df.copy()
            if diff_filter != "All": fdf = fdf[fdf["difficulty"] == diff_filter]
            if sub_filter  != "All": fdf = fdf[fdf["subject"]    == sub_filter]

            st.markdown(f"""<div style="color:#1E2D45;font-size:0.66rem;font-family:'DM Mono',monospace;
                margin-bottom:0.6rem">SHOWING {len(fdf)} / {len(df)} TOPICS</div>""", unsafe_allow_html=True)

            for subj, group in fdf.groupby("subject"):
                subj_total = len(group)
                subj_known = int((group["known"] == 1).sum())

                st.markdown(f"""
                <div class="subject-header">{subj}
                    <span style="font-size:0.6rem;color:#0D1527">({subj_total} topics · {subj_known} known)</span>
                </div>""", unsafe_allow_html=True)

                k1, k2, _ = st.columns([2, 2, 6])
                with k1:
                    if st.button(f"✅ Know All '{subj}'", key=f"ka_{subj}"):
                        mark_all_known(subj, 1)
                        st.session_state.pop("analysis_df", None)
                        st.session_state.pop("plan", None)
                        st.rerun()
                with k2:
                    if subj_known == subj_total and subj_total > 0:
                        if st.button(f"↩ Unmark '{subj}'", key=f"ku_{subj}"):
                            mark_all_known(subj, 0)
                            st.session_state.pop("analysis_df", None)
                            st.session_state.pop("plan", None)
                            st.rerun()

                for _, row in group.iterrows():
                    is_known   = int(row["known"]) == 1
                    card_class = "topic-card known" if is_known else "topic-card"
                    col_card, col_chk = st.columns([11, 2])

                    with col_card:
                        bar_w = {"Easy":"30%","Medium":"60%","Hard":"95%"}.get(row["difficulty"],"50%")
                        bar_c = {"Easy":"#00FF88","Medium":"#FFAA00","Hard":"#FF3C78"}.get(row["difficulty"],"#3D4F6B")
                        st.markdown(f"""
                        <div class="{card_class}">
                            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                                <span class="topic-name">{row['topic']}</span>
                                {badge(row['difficulty'])}
                            </div>
                            <div class="topic-meta" style="margin-top:5px;display:flex;align-items:center;gap:10px">
                                <span>⏱ ~{row['estimated_hours']}h</span>
                                <span style="color:#0D1220">·</span>
                                <span>priority {row['ai_priority']:.1f}</span>
                                <span style="color:#0D1220">·</span>
                                <div style="display:flex;align-items:center;gap:5px">
                                    <div style="width:80px;height:3px;background:#0D1220;border-radius:3px;overflow:hidden">
                                        <div style="width:{bar_w};height:100%;background:{bar_c};opacity:0.7;border-radius:3px"></div>
                                    </div>
                                    <span style="font-size:0.62rem;color:#1E2D45">{row['difficulty'].upper()} LOAD</span>
                                </div>
                            </div>
                        </div>""", unsafe_allow_html=True)

                    with col_chk:
                        new_known = st.checkbox("Know it", value=is_known, key=f"k_{row['id']}")
                        if new_known != is_known:
                            mark_topic_known(int(row["id"]), 1 if new_known else 0)
                            st.session_state.pop("analysis_df", None)
                            st.session_state.pop("plan", None)
                            st.rerun()

            st.markdown("---")
            bc1, bc2, _ = st.columns([2, 2, 4])
            with bc1:
                if st.button("🔄 Refresh Analysis", use_container_width=True):
                    st.session_state.pop("analysis_df", None)
                    st.rerun()
            with bc2:
                if st.button("🗑 Clear All Topics", use_container_width=True):
                    clear_topics()
                    for k in ["analysis_df","plan","last_uploaded_id","pdf_result"]:
                        st.session_state.pop(k, None)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Roadmap
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    rows = get_topics()

    if not rows and "plan" not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:4rem;color:#1E2D45;font-size:0.9rem">
            Add topics first → then come here 👆
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="sec-label">Configure Your Plan</div>', unsafe_allow_html=True)

        with st.form("planner_form"):
            p1, p2, p3, p4 = st.columns(4)
            days          = p1.number_input("📅 Days left",  min_value=1, max_value=90, value=7)
            hours         = p2.number_input("⏰ Hours/day",  min_value=1, max_value=16, value=4)
            crash_mode    = p3.toggle("🚨 Crash Mode",    help="Skip revision — pack max topics per day")
            show_overflow = p4.toggle("⚠ Show Overflow", value=True,
                                      help="Show topics that didn't fit in your plan")
            generate = st.form_submit_button("🚀  Generate My Study Plan", use_container_width=True)

        if generate:
            with st.spinner("Building your plan…"):
                try:
                    df   = analyze_topics(get_topics())
                    plan = generate_schedule(df.copy(), int(days), int(hours), crash_mode=crash_mode)
                    st.session_state.analysis_df   = df
                    st.session_state.plan          = plan
                    st.session_state.crash_mode    = crash_mode
                    st.session_state.show_overflow = show_overflow
                    st.session_state.plan_days     = int(days)
                    st.session_state.plan_hours    = int(hours)
                except Exception as e:
                    st.error(f"❌ Failed: {e}")

        if "plan" not in st.session_state:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#1E2D45;font-size:0.9rem">
                Set your days & hours above, then hit
                <b style="color:#BF5AF2">Generate My Study Plan</b>
            </div>""", unsafe_allow_html=True)
        else:
            plan          = st.session_state.plan
            crash_mode    = st.session_state.get("crash_mode", False)
            show_overflow = st.session_state.get("show_overflow", True)
            plan_days     = st.session_state.get("plan_days", 7)
            plan_hours    = st.session_state.get("plan_hours", 4)

            study_rows    = plan[plan["Type"] == "Study"]
            rev_rows      = plan[plan["Type"] == "Revision"]
            known_rows    = plan[plan["Type"] == "Known"]
            overflow_rows = plan[plan["Type"] == "Overflow"] if "Overflow" in plan["Type"].values else pd.DataFrame()
            sched         = plan[~plan["Type"].isin(["Known", "Overflow"])]
            u_days        = sched["Day"].nunique()
            overflow_count = len(overflow_rows)

            # ── Status banner ─────────────────────────────────────────────────
            if overflow_count > 0:
                st.markdown(f"""
                <div class="warn-box">
                    ⚠️ <b>{overflow_count} topics won't fit</b> in {plan_days} days × {plan_hours}h/day.
                    Add more days, more hours, or mark some topics as known.
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ok-box">
                    ✅ All <b>{len(study_rows)} topics fit</b> in your {plan_days}-day plan. You've got this!
                </div>""", unsafe_allow_html=True)

            if crash_mode:
                st.markdown("""
                <div class="warn-box">
                    🚨 CRASH MODE — No revision slots. Maximum topics per day.
                </div>""", unsafe_allow_html=True)

            # ── Summary stats ─────────────────────────────────────────────────
            sm_cols = st.columns(4)
            for col, (num, lbl, color) in zip(sm_cols, [
                (len(study_rows), "Topics Planned",  "#BF5AF2"),
                (len(rev_rows),   "Revision Slots",  "#00F5FF"),
                (u_days,          "Days Active",     "#00FF88"),
                (overflow_count,  "Overflow Topics", "#FF6B6B" if overflow_count else "#1E2D45"),
            ]):
                col.markdown(f"""
                <div class="stat-card" style="--accent:{color}">
                    <div class="stat-num">{num}</div>
                    <div class="stat-lbl">{lbl}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Full timeline ─────────────────────────────────────────────────
            st.markdown("""<div style="font-size:1rem;font-weight:800;color:#C8D8F0;margin-bottom:0.2rem">
                🗓 Full Plan</div>""", unsafe_allow_html=True)

            day_order = sorted(
                sched["Day"].unique(),
                key=lambda d: int(d.replace("Day ","")) if d.replace("Day ","").isdigit() else 999
            )

            for i, day in enumerate(day_order):
                items   = sched[sched["Day"] == day]
                s_count = int((items["Type"] == "Study").sum())
                dc      = day_color(i)

                hard_c = int((items[items["Type"]=="Study"]["Difficulty"] == "Hard").sum())
                med_c  = int((items[items["Type"]=="Study"]["Difficulty"] == "Medium").sum())
                easy_c = int((items[items["Type"]=="Study"]["Difficulty"] == "Easy").sum())
                mix_parts = []
                if hard_c: mix_parts.append(f"<span style='color:#FF3C78'>{hard_c}H</span>")
                if med_c:  mix_parts.append(f"<span style='color:#FFAA00'>{med_c}M</span>")
                if easy_c: mix_parts.append(f"<span style='color:#00FF88'>{easy_c}E</span>")
                mix_str = " · ".join(mix_parts)

                today_tag = ' &nbsp;<span style="font-size:0.6rem;background:rgba(0,245,255,0.1);color:#00F5FF;border:1px solid rgba(0,245,255,0.25);border-radius:20px;padding:2px 8px;font-family:\'DM Mono\',monospace">TODAY</span>' if day == "Day 1" else ""

                st.markdown(f"""
                <div class="day-header">
                    <span class="day-dot" style="--dc:{dc}"></span>
                    <span class="day-title">{day}{today_tag}</span>
                    <span class="day-sub">&nbsp;{s_count} topics · {mix_str}</span>
                    <span class="day-line"></span>
                </div>""", unsafe_allow_html=True)

                for _, r in items.iterrows():
                    is_rev = r["Type"] == "Revision"
                    sc  = "revise" if is_rev else diff_class(r.get("Difficulty", "Medium"))
                    em  = "🔁" if is_rev else "📖"
                    db  = badge("Revise") if is_rev else badge(r.get("Difficulty", "Medium"))
                    st.markdown(f"""
                    <div class="slot {sc}">
                        <span class="slot-num">{r['Block']}</span>
                        <div style="flex:1">
                            <div class="slot-topic">{em} {r['Topic']} &nbsp;{db}</div>
                            <div class="slot-sub">{r['Subject']}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

            # ── Overflow ──────────────────────────────────────────────────────
            if show_overflow and not overflow_rows.empty:
                st.markdown(f"""
                <div class="overflow-head">
                    ⚠ {len(overflow_rows)} topics didn't fit — mark some as known to free up space
                </div>""", unsafe_allow_html=True)
                for _, r in overflow_rows.iterrows():
                    st.markdown(f"""
                    <div class="slot overflow-row">
                        <span class="slot-num">—</span>
                        <div style="flex:1">
                            <div class="slot-topic">⚠ {r['Topic']} &nbsp;{badge(r['Difficulty'])}</div>
                            <div class="slot-sub">{r['Subject']}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

            # ── Known ─────────────────────────────────────────────────────────
            if not known_rows.empty:
                st.markdown("""
                <div class="day-header" style="margin-top:1.4rem">
                    <span class="day-dot" style="--dc:#1E2D45;box-shadow:none"></span>
                    <span class="day-title" style="color:#3D4F6B">Already Known — Skipped</span>
                    <span class="day-line"></span>
                </div>""", unsafe_allow_html=True)
                for _, r in known_rows.iterrows():
                    st.markdown(f"""
                    <div class="slot known-row">
                        <span class="slot-num">✓</span>
                        <div style="flex:1">
                            <div class="slot-topic" style="opacity:0.4">{r['Topic']}</div>
                            <div class="slot-sub">{r['Subject']}</div>
                        </div>
                        {badge("Known")}
                    </div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            cc1, cc2 = st.columns(2)
            with cc1:
                pdf_bytes = create_pdf(plan, plan_days, plan_hours, crash_mode)
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_bytes,
                    file_name="Study_Plan.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with cc2:
                with st.form(key="save_plan_form"):
                    sf1, sf2 = st.columns([3, 1])
                    plan_name = sf1.text_input("Name:", value=f"Plan {plan_days} Days", label_visibility="collapsed")
                    save_btn = sf2.form_submit_button("💾 Save")
                if save_btn:
                    try:
                        save_study_plan(plan_name, plan.to_json(orient="records"))
                        st.success("Plan saved successfully! Check 'Saved Plans' tab.")
                    except Exception as e:
                        st.error(f"Failed to save plan: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Saved Plans
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-label">Your Saved Plans</div>', unsafe_allow_html=True)
    try:
        saved_plans = get_saved_plans()
    except Exception as e:
        st.error("Database schema outdated! Please click here or restart to update.")
        saved_plans = []

    if not saved_plans:
        st.markdown("""
        <div style="text-align:center;padding:4rem;color:#1E2D45;font-size:0.9rem">
            No saved plans yet. Generate and save one from the Roadmap tab!
        </div>""", unsafe_allow_html=True)
    else:
        for p in saved_plans:
            p_id, p_name, p_json, p_date = p
            with st.expander(f"📁 **{p_name}**  —  {p_date[:16]}"):
                st.markdown(f"*Created: {p_date}*")
                d1, d2 = st.columns(2)
                if d1.button("👁 Load Plan to Roadmap", key=f"load_{p_id}"):
                    import pandas as pd
                    try:
                        loaded_plan = pd.read_json(io.StringIO(p_json), orient="records")
                        st.session_state.plan = loaded_plan
                        st.success("Loaded successfully! Go to 'Study Roadmap' tab to view.")
                    except Exception as e:
                        st.error("Failed to load this plan.")
                if d2.button("🗑 Delete", key=f"del_{p_id}"):
                    delete_saved_plan(p_id)
                    st.rerun()