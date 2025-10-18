# ===== app/app.py (REPLACE ENTIRE FILE) =====
from pathlib import Path
import sys
import datetime as dt

import streamlit as st
import pandas as pd
import plotly.express as px

# --- Local imports ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from src.causal import compute_pre_post_effect
except Exception:
    compute_pre_post_effect = None

st.set_page_config(page_title="PainReliefMap", layout="wide")

# -------------------------
# Helpers & Data Loaders
# -------------------------
@st.cache_data
def load_evidence() -> pd.DataFrame:
    p = ROOT / "data" / "evidence_counts.csv"
    df = pd.read_csv(p)
    for c in ("condition", "therapy"):
        if c in df:
            df[c] = df[c].astype(str).str.title()
    return df

@st.cache_data
def load_demo_n1() -> pd.DataFrame:
    """30 days of demo tracking with a therapy switch after day 10."""
    # If you later create data/templates/n_of_1_demo.csv, read it here instead.
    start = dt.date.today() - dt.timedelta(days=29)
    rows = []
    for i in range(30):
        d = start + dt.timedelta(days=i)
        therapy_on = 0 if i < 10 else 1
        # Simulate signals
        pain = 7 - max(0, i-10)*0.2 if therapy_on else 7.0
        stress = 6 - max(0, i-10)*0.18 if therapy_on else 6.0
        sleep = 6 + max(0, i-10)*0.05
        rows.append({"date": d, "therapy_on": therapy_on, "pain_score": round(pain, 1),
                     "stress_score": round(stress, 1), "sleep_hours": round(sleep, 1)})
    return pd.DataFrame(rows)

def init_state():
    st.session_state.setdefault("user_id", None)        # replace with real auth later
    st.session_state.setdefault("n1_df", pd.DataFrame())# user’s personal tracking df

def is_new_user() -> bool:
    # “New user” if no personal rows yet.
    return st.session_state.n1_df.empty

def _last7_trend(df: pd.DataFrame) -> pd.DataFrame:
    t = df.copy()
    t["date"] = pd.to_datetime(t["date"]).dt.date
    return t.groupby("date", as_index=False)[["pain_score", "stress_score"]].mean().tail(7)

def _today_row_exists(df: pd.DataFrame) -> bool:
    if df.empty: return False
    d = pd.to_datetime(df["date"], errors="coerce").dt.date
    return dt.date.today() in set(d)

# -------------------------
# UI Components
# -------------------------
def hero_kpi(title: str, value: str, help_text: str = ""):
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.markdown(f"**{value}**")
        if help_text:
            st.caption(help_text)

def card(title: str):
    return st.container(border=True)

def demo_dashboard(evidence: pd.DataFrame):
    st.info("You’re viewing a **Demo Dashboard**. Start logging to see your own insights.")
    demo = load_demo_n1()

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Pain trend (demo)")
        fig = px.line(demo, x="date", y="pain_score", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        if compute_pre_post_effect:
            try:
                res = compute_pre_post_effect(demo, y_col="pain_score")
                hero_kpi("Therapy effect (demo)",
                         f"{res['effect_mean']:.1f} (95% CI {res['ci_low']:.1f}, {res['ci_high']:.1f})",
                         "Mean change in pain after starting therapy.")
            except Exception as e:
                st.warning(f"Causal analysis not available: {e}")
        else:
            st.warning("Causal analysis module not found.")

    # Stress vs pain
    c3, c4 = st.columns([2, 1])
    with c3:
        st.subheader("Stress vs Pain (demo, last 14 days)")
        last14 = demo.tail(14)
        fig2 = px.scatter(last14, x="stress_score", y="pain_score",
                          hover_data=["date"], trendline="ols")
        st.plotly_chart(fig2, use_container_width=True)
    with c4:
        st.subheader("Sleep vs Pain (demo)")
        fig3 = px.scatter(last14, x="sleep_hours", y="pain_score", hover_data=["date"])
        st.plotly_chart(fig3, use_container_width=True)

    # Evidence snapshot
    st.divider()
    st.subheader("Evidence snapshot (example)")
    # Pick a common pair to illustrate
    example = evidence[(evidence["condition"] == "Fibromyalgia") &
                       (evidence["therapy"] == "Acupuncture")]
    if not example.empty:
        row = example.iloc[0]
        c5, c6, c7 = st.columns(3)
        with c5: hero_kpi("Clinical trials", f"{int(row['clinicaltrials_n'])}")
        with c6: hero_kpi("PubMed articles", f"{int(row['pubmed_n'])}")
        with c7: hero_kpi("Condition", "Fibromyalgia")
    st.button("🌱 Start your own Daily Log", type="primary", use_container_width=True)

def personal_dashboard():
    df = st.session_state.n1_df
    if df.empty:
        st.warning("No personal data yet. Switch to **Daily Log** to begin.")
        return

    # Top summary row
    c1, c2, c3 = st.columns(3)
    with c1:
        last = df.sort_values("date").tail(1)
        last_p = float(last["pain_score"].values[0]) if not last.empty else float("nan")
        hero_kpi("Yesterday’s pain", f"{last_p:.1f}" if last_p==last_p else "—")

    with c2:
        trend7 = _last7_trend(df)
        if len(trend7) >= 2:
            delta = trend7["pain_score"].iloc[-1] - trend7["pain_score"].iloc[0]
            label = f"{trend7['pain_score'].iloc[-1]:.1f} ({'+' if delta>0 else ''}{delta:.1f} vs 7d ago)"
        else:
            label = "—"
        hero_kpi("7-day pain trend", label)

    with c3:
        done_today = _today_row_exists(df)
        hero_kpi("Today’s log", "✅ Done" if done_today else "⏳ Pending",
                 "Log once per day for best insights.")

    # Two charts
    colA, colB = st.columns([2, 1])
    with colA:
        st.subheader("Pain & Stress over time")
        d = df.copy()
        d["date"] = pd.to_datetime(d["date"])
        fig = px.line(d, x="date", y=["pain_score", "stress_score"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.subheader("Sleep vs Pain (last 14 days)")
        last14 = d.sort_values("date").tail(14)
        fig2 = px.scatter(last14, x="sleep_hours", y="pain_score", hover_data=["date"])
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    # Causal card (re-run weekly or on demand)
    with card("Causal Analysis (v1): Pre/Post"):
        if compute_pre_post_effect:
            try:
                res = compute_pre_post_effect(df, y_col="pain_score")
                st.markdown(
                    f"**Effect on pain:** {res['effect_mean']:.1f} "
                    f"(95% CI {res['ci_low']:.1f}, {res['ci_high']:.1f})  \n"
                    f"Pre mean: {res['pre_mean']:.1f}, Post mean: {res['post_mean']:.1f}  \n"
                    f"Start date detected: {res['start_date']}"
                )
            except Exception as e:
                st.warning(f"Not enough variation to compute pre/post: {e}")
        else:
            st.warning("Causal module missing.")

def daily_log_ui():
    st.subheader("Daily Wellness Log (N-of-1 Tracking)")
    st.caption("Record pain, stress, sleep, and whether you used a therapy today.")
    df = st.session_state.n1_df.copy()

    with st.form("log_form", clear_on_submit=False):
        date = st.date_input("Date", dt.date.today())
        therapy_on = st.radio("Therapy used today?", options=[0,1], format_func=lambda x: "No" if x==0 else "Yes", horizontal=True)
        pain = st.slider("Pain (0–10)", 0, 10, 5)
        stress = st.slider("Stress (0–10)", 0, 10, 5)
        sleep = st.slider("Sleep hours", 0.0, 12.0, 7.0, 0.5)
        submitted = st.form_submit_button("Save entry", type="primary")

    if submitted:
        new_row = {"date": date, "therapy_on": therapy_on, "pain_score": pain,
                   "stress_score": stress, "sleep_hours": sleep}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.n1_df = df
        st.success("Saved!")

    # Quick actions
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🌿 Duplicate yesterday", use_container_width=True):
            if df.empty:
                st.warning("No previous day to duplicate.")
            else:
                tmp = df.copy()
                tmp["date"] = pd.to_datetime(tmp["date"]).dt.date
                last = tmp.sort_values("date").tail(1).iloc[0].to_dict()
                last["date"] = dt.date.today()
                st.session_state.n1_df = pd.concat([df, pd.DataFrame([last])], ignore_index=True)
                st.success("Duplicated yesterday into today.")
    with c2:
        st.download_button("⬇️ Download CSV", data=st.session_state.n1_df.to_csv(index=False),
                           file_name="n_of_1_log.csv", mime="text/csv", use_container_width=True)

    # Preview table
    if not st.session_state.n1_df.empty:
        st.dataframe(st.session_state.n1_df.sort_values("date"), use_container_width=True, height=280)

def evidence_explorer_ui(evidence: pd.DataFrame):
    st.subheader("Evidence Explorer")
    c1, c2 = st.columns(2)
    with c1:
        cond = st.selectbox("Condition", sorted(evidence["condition"].unique()))
    with c2:
        ther = st.selectbox("Therapy", sorted(evidence["therapy"].unique()))
    filt = evidence[(evidence["condition"] == cond) & (evidence["therapy"] == ther)]
    if filt.empty:
        st.info("No rows for this pair.")
        return
    row = filt.iloc[0]
    k1, k2, k3 = st.columns(3)
    with k1: hero_kpi("Clinical trials", f"{int(row['clinicaltrials_n'])}")
    with k2: hero_kpi("PubMed articles", f"{int(row['pubmed_n'])}")
    with k3: hero_kpi("Last updated", str(row.get("last_updated", "—")))

    # Top studied therapies for the same condition
    st.markdown("### Most-studied therapies for this condition")
    top = (evidence[evidence["condition"] == cond]
           .sort_values("clinicaltrials_n", ascending=False)
           .head(10))
    fig = px.bar(top, x="therapy", y="clinicaltrials_n", text_auto=True,
                 title=f"{cond}: clinical trial counts by therapy")
    st.plotly_chart(fig, use_container_width=True)

def analysis_ui():
    st.subheader("Your Causal Analysis (v1)")
    st.caption("Compares average pain before vs. after you started therapy.")
    df = st.session_state.n1_df
    if df.empty:
        st.info("Add some daily logs then return here.")
        return
    if compute_pre_post_effect:
        try:
            res = compute_pre_post_effect(df, y_col="pain_score")
            st.success(
                f"**Effect on pain**: {res['effect_mean']:.1f} "
                f"(95% CI {res['ci_low']:.1f}, {res['ci_high']:.1f})  \n"
                f"Pre mean: {res['pre_mean']:.1f} • Post mean: {res['post_mean']:.1f}  \n"
                f"Start date detected: {res['start_date']}"
            )
        except Exception as e:
            st.warning(f"Couldn’t compute effect: {e}")
    else:
        st.warning("Causal module not available.")

# -------------------------
# App Entrypoint
# -------------------------
def main():
    init_state()
    evidence = load_evidence()

    st.title("PainReliefMap")
    st.caption("Discover what helps you most — with science and your own data.")

    # Tabs
    t1, t2, t3, t4 = st.tabs(["Dashboard", "Daily Log", "Evidence Explorer", "Analysis"])

    with t1:
        if is_new_user():
            demo_dashboard(evidence)
        else:
            personal_dashboard()

    with t2:
        daily_log_ui()

    with t3:
        evidence_explorer_ui(evidence)

    with t4:
        analysis_ui()

if __name__ == "__main__":
    main()
# ===== end app/app.py =====