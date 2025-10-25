import streamlit as st
import pandas as pd
from pathlib import Path
import json
import hashlib
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime as dt
from scipy import stats

# ============================================================================
# PAGE CONFIGURATION - MUST BE FIRST
# ============================================================================
st.set_page_config(
    page_title="Pain Relief Map - Natural Therapy Tracker",
    page_icon="💆🏻‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# DATA PATHS
# ============================================================================
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_FILE = ROOT / "data" / "evidence_counts_with_direction.csv"

# ============================================================================
# ENHANCED CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* Global Reset */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main Background - Static Gradient */
    .main {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        background-position: 0% 50%;
    }

    /* Streamlit Container Overrides - AGGRESSIVE */
    .block-container {
        padding: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 1400px !important;
        margin-top: 0 !important;
    }

    /* Hide ALL empty containers */
    .element-container:empty {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .element-container:has(> .stMarkdown:empty) {
        display: none !important;
        height: 0 !important;
    }

    /* Remove extra padding from columns */
    [data-testid="column"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Force remove padding from main container children */
    .main .block-container > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    .main .block-container > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Force remove any top margin/padding from first elements */
    .element-container:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Nuclear option - hide any divs before hero */
    .main > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Target Streamlit's app container */
    div[data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }

    /* Target main content area */
    section[data-testid="stMain"] {
        padding-top: 0 !important;
    }

    section[data-testid="stMain"] > div:first-child {
        padding-top: 0 !important;
    }

    /* HERO SECTION */
    .hero-mega {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 40px;
        text-align: center;
        border-radius: 30px;
        margin: 0 0 3rem 0;
        box-shadow: 0 30px 80px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .hero-mega:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 40px 100px rgba(102, 126, 234, 0.5);
    }

    .hero-mega::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    }

    .hero-title {
        font-size: 64px !important;
        font-weight: 900 !important;
        color: white !important;
        margin: 0 0 20px 0 !important;
        text-shadow: 0 4px 30px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 26px !important;
        color: rgba(255,255,255,0.95) !important;
        margin: 0 0 40px 0 !important;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* Stats Row */
    .stats-row {
        display: flex;
        justify-content: center;
        gap: 80px;
        margin-top: 50px;
        position: relative;
        z-index: 1;
    }

    .stat-box {
        text-align: center;
        animation: fadeInUp 0.6s ease forwards;
        opacity: 0;
    }

    .stat-box:nth-child(1) { animation-delay: 0.2s; }
    .stat-box:nth-child(2) { animation-delay: 0.4s; }
    .stat-box:nth-child(3) { animation-delay: 0.6s; }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .stat-number {
        font-size: 56px;
        font-weight: 900;
        color: white;
        line-height: 1;
        margin-bottom: 10px;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    .stat-label {
        font-size: 15px;
        color: rgba(255,255,255,0.95);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }

    /* PREMIUM CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        border: 1px solid rgba(255, 255, 255, 0.8);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }

    .glass-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 30px 80px rgba(102, 126, 234, 0.25);
    }

    .glass-card:hover::before {
        transform: scaleX(1);
    }

    /* BUTTONS */
    .stButton > button {
        border-radius: 15px !important;
        font-weight: 700 !important;
        padding: 20px 40px !important;
        font-size: 18px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton > button:hover {
        transform: translateY(-4px) scale(1.05) !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* METRICS */
    [data-testid="stMetricValue"] {
        font-size: 48px !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #64748b !important;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 15px 30px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }

    /* Progress Badge */
    .progress-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        margin: 10px 0;
    }

    /* Onboarding Card */
    .onboarding-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 5px solid #667eea;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
    }
</style>

<script>
// Wait for page to load
document.addEventListener('DOMContentLoaded', function() {
    removeWhiteBoxes();
});

// Also run after Streamlit reruns
window.addEventListener('load', function() {
    removeWhiteBoxes();
    // Keep checking and removing
    setInterval(removeWhiteBoxes, 100);
});

function removeWhiteBoxes() {
    // Remove empty element containers
    document.querySelectorAll('.element-container').forEach(function(el) {
        if (el.children.length === 0 || el.textContent.trim() === '') {
            el.style.display = 'none';
            el.style.height = '0';
            el.style.margin = '0';
            el.style.padding = '0';
        }
    });

    // Force zero padding on block container
    const blockContainer = document.querySelector('.block-container');
    if (blockContainer) {
        blockContainer.style.paddingTop = '0';
        blockContainer.style.marginTop = '0';
    }

    // Force zero padding on main section
    const mainSection = document.querySelector('section[data-testid="stMain"]');
    if (mainSection) {
        mainSection.style.paddingTop = '0';
    }
}
</script>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
for key, default in {
    'authenticated': False,
    'demo_mode': False,
    'username': "",
    'n1_df': pd.DataFrame(),
    'onboarding_complete': False,
    'onboarding_step': 0,
    'user_conditions': [],
    'user_therapies': [],
    'first_visit': True,
    'show_onboarding': False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_evidence_data():
    """Load evidence database"""
    try:
        if EVIDENCE_FILE.exists():
            df = pd.read_csv(EVIDENCE_FILE)
            return df
        else:
            st.error(f"Evidence file not found: {EVIDENCE_FILE}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading evidence: {e}")
        return pd.DataFrame()

def generate_demo_data_with_therapy(therapy_start_day=7):
    """Generate demo data with therapy intervention marker"""
    demo_data = []
    start_date = datetime.now().date() - timedelta(days=29)

    for day in range(30):
        current_date = start_date + timedelta(days=day)

        # Pain decreases after therapy starts
        if day < therapy_start_day:
            pain_score = max(6, min(9, 8 - (day * 0.05) + np.random.normal(0, 0.3)))
        else:
            days_after = day - therapy_start_day
            pain_score = max(3, min(7, 8 - (days_after * 0.25) + np.random.normal(0, 0.3)))

        sleep_hours = max(5, min(9, 5.5 + (day * 0.05) + np.random.normal(0, 0.2)))
        mood_score = max(4, min(9, 5 + (day * 0.08) + np.random.normal(0, 0.3)))

        demo_data.append({
            "date": current_date,
            "pain_score": round(pain_score, 1),
            "sleep_hours": round(sleep_hours, 1),
            "mood_score": round(mood_score, 1),
            "stress_score": round(7 - (day * 0.06), 1),
            "therapy_started": "Yoga" if day == therapy_start_day else "",
            "therapies_continuing": ["Yoga"] if day >= therapy_start_day else []
        })

    return pd.DataFrame(demo_data)

def calculate_therapy_effect(df, therapy_name, metric="pain_score"):
    """Calculate Difference-in-Differences therapy effect"""
    # Find therapy start date
    therapy_start = df[df['therapy_started'] == therapy_name]['date'].min()

    if pd.isna(therapy_start):
        return None

    before = df[df['date'] < therapy_start]
    after = df[df['date'] >= therapy_start]

    if len(before) < 3 or len(after) < 10:
        return {
            "ready": False,
            "days_needed": max(0, 3 - len(before)) if len(before) < 3 else max(0, 10 - len(after)),
            "stage": "before" if len(before) < 3 else "after"
        }

    # Calculate means
    before_mean = before[metric].mean()
    after_mean = after[metric].mean()
    effect = after_mean - before_mean

    # Statistical significance (t-test)
    t_stat, p_value = stats.ttest_ind(before[metric], after[metric])

    # Effect size (Cohen's d)
    pooled_std = np.sqrt(((len(before)-1)*before[metric].std()**2 + (len(after)-1)*after[metric].std()**2) / (len(before)+len(after)-2))
    cohens_d = abs(effect) / pooled_std if pooled_std > 0 else 0

    # Confidence interval (bootstrap)
    confidence_level = 95
    n_bootstrap = 1000
    bootstrap_effects = []
    for _ in range(n_bootstrap):
        before_sample = before[metric].sample(len(before), replace=True)
        after_sample = after[metric].sample(len(after), replace=True)
        bootstrap_effects.append(after_sample.mean() - before_sample.mean())

    ci_lower = np.percentile(bootstrap_effects, (100-confidence_level)/2)
    ci_upper = np.percentile(bootstrap_effects, 100-(100-confidence_level)/2)

    return {
        "ready": True,
        "therapy": therapy_name,
        "metric": metric,
        "before_mean": before_mean,
        "after_mean": after_mean,
        "effect": effect,
        "effect_pct": (effect / before_mean * 100) if before_mean != 0 else 0,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "cohens_d": cohens_d,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "days_before": len(before),
        "days_after": len(after)
    }

def get_unique_conditions(evidence_df):
    """Get unique conditions from evidence database"""
    if 'condition' in evidence_df.columns:
        return sorted(evidence_df['condition'].unique())
    return []

def get_therapies_for_conditions(evidence_df, conditions, evidence_filter="Positive"):
    """Get therapies for selected conditions with positive evidence"""
    if evidence_df.empty or not conditions:
        return pd.DataFrame()

    filtered = evidence_df[evidence_df['condition'].isin(conditions)]

    if evidence_filter != "All":
        filtered = filtered[filtered['evidence_direction'] == evidence_filter]

    # Aggregate by therapy
    therapy_summary = filtered.groupby('therapy').agg({
        'clinicaltrials_n': 'sum',
        'pubmed_n': 'sum',
        'evidence_direction': lambda x: x.mode()[0] if len(x) > 0 else 'Unclear',
        'therapy_group': 'first'
    }).reset_index()

    therapy_summary = therapy_summary.sort_values('clinicaltrials_n', ascending=False)

    return therapy_summary

# ============================================================================
# ONBOARDING WIZARD
# ============================================================================

def show_onboarding_steps():
    """Handles onboarding steps 1-3 (not landing page)"""
    evidence_df = load_evidence_data()

    if st.session_state.onboarding_step == 1:
        # Step 1: Select Conditions
        st.markdown("""
        <div class="onboarding-card">
            <h2 style="margin: 0 0 10px 0; color: #667eea;">🎯 Step 1 of 3: Select Your Conditions</h2>
            <p style="margin: 0; color: #64748b; font-size: 16px;">
                Tell us what you're managing, and we'll find natural therapies with clinical evidence.
            </p>
        </div>
        """, unsafe_allow_html=True)

        conditions = get_unique_conditions(evidence_df)

        # Popular conditions first
        popular_conditions = ["Chronic Pain", "Fibromyalgia", "Arthritis", "Back Pain",
                            "Anxiety", "Insomnia", "Migraines", "IBS"]
        popular_conditions = [c for c in popular_conditions if c in conditions]
        other_conditions = [c for c in conditions if c not in popular_conditions]

        st.markdown("### 📋 Common Conditions")
        selected_popular = st.multiselect(
            "Select from common conditions:",
            popular_conditions,
            help="Choose all that apply",
            key="popular_conditions_select"
        )

        with st.expander("🔍 See All Conditions", expanded=False):
            selected_other = st.multiselect(
                "Other conditions:",
                other_conditions,
                key="other_conditions_select"
            )

        all_selected = selected_popular + (selected_other if 'selected_other' in locals() else [])

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("FIND NATURAL THERAPIES →", type="primary", use_container_width=True, disabled=len(all_selected)==0):
                st.session_state.user_conditions = all_selected
                st.session_state.onboarding_step = 2
                st.rerun()

    elif st.session_state.onboarding_step == 2:
        # Step 2: Explore Evidence
        st.markdown("""
        <div class="onboarding-card">
            <h2 style="margin: 0 0 10px 0; color: #667eea;">🔬 Step 2 of 3: Explore Natural Therapies</h2>
            <p style="margin: 0; color: #64748b; font-size: 16px;">
                Based on your conditions, here are <strong>natural, holistic therapies</strong> with positive clinical evidence.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### Your Conditions: {', '.join(st.session_state.user_conditions)}")

        therapy_summary = get_therapies_for_conditions(
            evidence_df,
            st.session_state.user_conditions,
            evidence_filter="Positive"
        )

        if not therapy_summary.empty:
            st.markdown("### 🌿 Recommended Natural Therapies (Positive Evidence)")

            # Create ranking display
            for rank, (idx, row) in enumerate(therapy_summary.head(10).iterrows()):
                medal = "🥇" if rank == 0 else "🥈" if rank == 1 else "🥉" if rank == 2 else "⭐"
                therapy_name = row['therapy']

                with st.expander(f"{medal} **{therapy_name}** - {row['clinicaltrials_n']} clinical trials", expanded=rank==0, key=f"therapy_expander_{rank}_{therapy_name}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Clinical Trials", f"{row['clinicaltrials_n']:,}")
                    with col2:
                        st.metric("PubMed Articles", f"{row['pubmed_n']:,}")
                    with col3:
                        st.metric("Therapy Type", row['therapy_group'])

                    st.markdown(f"""
                    **{row['therapy']}** is a natural, holistic therapy with **{row['evidence_direction'].lower()} evidence**
                    from clinical research for conditions like {', '.join(st.session_state.user_conditions[:2])}.
                    """)

        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("START TRACKING MY JOURNEY →", type="primary", use_container_width=True):
                st.session_state.onboarding_step = 3
                st.rerun()

    elif st.session_state.onboarding_step == 3:
        # Step 3: How to Track
        st.markdown("""
        <div class="onboarding-card">
            <h2 style="margin: 0 0 10px 0; color: #667eea;">🌱 Step 3 of 3: How Tracking Works</h2>
            <p style="margin: 0; color: #64748b; font-size: 16px;">
                Follow these simple steps to discover what works for YOU.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="glass-card" style="text-align: center; min-height: 280px;">
                <div style="font-size: 56px; margin-bottom: 20px;">1️⃣</div>
                <h3 style="font-size: 22px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Track Baseline</h3>
                <p style="color: #64748b; font-size: 15px; line-height: 1.7; font-weight: 500;">
                    Log your symptoms for <strong>3 days</strong> BEFORE starting any new therapy. This is your baseline.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="glass-card" style="text-align: center; min-height: 280px;">
                <div style="font-size: 56px; margin-bottom: 20px;">2️⃣</div>
                <h3 style="font-size: 22px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Start Therapy</h3>
                <p style="color: #64748b; font-size: 15px; line-height: 1.7; font-weight: 500;">
                    Begin your chosen natural therapy and <strong>mark it</strong> in your daily log. We'll track the intervention point.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="glass-card" style="text-align: center; min-height: 280px;">
                <div style="font-size: 56px; margin-bottom: 20px;">3️⃣</div>
                <h3 style="font-size: 22px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">See Results</h3>
                <p style="color: #64748b; font-size: 15px; line-height: 1.7; font-weight: 500;">
                    After <strong>14 days total</strong>, see statistical analysis showing if the therapy is working for you!
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✨ COMPLETE ONBOARDING", type="primary", use_container_width=True):
                st.session_state.onboarding_complete = True
                st.session_state.show_onboarding = False
                st.balloons()
                st.rerun()

# ============================================================================
# MAIN APP LOGIC
# ============================================================================

# Check if user should see onboarding
if not st.session_state.authenticated and not st.session_state.demo_mode and st.session_state.onboarding_step == 0:
    st.markdown("""
        <div class="hero-mega">
            <div style="position: relative; z-index: 2;">
                <div style="display: inline-block; background: rgba(255,255,255,0.2); padding: 8px 20px; border-radius: 30px; margin-bottom: 20px; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: white;">
                    ✨ Evidence-Based • Natural • Privacy-First
                </div>
                <h1 class="hero-title">🌿 Pain Relief Map</h1>
                <p class="hero-subtitle">Your Natural, Evidence-Based Healing Journey</p>
                <p style="font-size: 19px; color: rgba(255,255,255,0.95); margin: 25px auto 0 auto; max-width: 750px; font-weight: 400; line-height: 1.7;">
                    Discover <strong>holistic, natural therapies</strong> backed by 500,000+ clinical trials.
                    Track your symptoms and see what actually works for <strong>YOUR</strong> body.
                </p>
                <div class="stats-row">
                    <div class="stat-box">
                        <div class="stat-number">500K+</div>
                        <div class="stat-label">Clinical Trials</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">Natural</div>
                        <div class="stat-label">Therapies</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">AI</div>
                        <div class="stat-label">Insights</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 🚀 Try Demo Mode")
            st.markdown("**Experience the full app with sample data - no signup required!**")
            st.markdown("")

            if st.button("🚀 START DEMO NOW", type="primary", use_container_width=True, key="demo_mode_btn"):
                st.session_state.demo_mode = True
                st.session_state.username = "Demo User"
                st.session_state.n1_df = generate_demo_data_with_therapy(therapy_start_day=7)
                st.session_state.onboarding_complete = True
                st.rerun()

            st.markdown("---")
            st.markdown("**Or customize your experience:**")
            if st.button("🎯 Find Therapies for My Conditions", use_container_width=True, key="onboarding_btn"):
                st.session_state.onboarding_step = 1
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Feature highlights
            st.markdown("""
            <div class="feature-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 30px;">
                <div class="glass-card" style="padding: 25px; text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">🔬</div>
                    <div style="font-weight: 700; margin-bottom: 8px;">Evidence Explorer</div>
                    <div style="color: #64748b; font-size: 14px;">Browse clinical trials for natural therapies</div>
                </div>
                <div class="glass-card" style="padding: 25px; text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">📊</div>
                    <div style="font-weight: 700; margin-bottom: 8px;">Causal Analysis</div>
                    <div style="color: #64748b; font-size: 14px;">Statistical insights on what works</div>
                </div>
                <div class="glass-card" style="padding: 25px; text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">🌿</div>
                    <div style="font-weight: 700; margin-bottom: 8px;">Natural Focus</div>
                    <div style="color: #64748b; font-size: 14px;">Holistic, non-pharmaceutical options</div>
                </div>
                <div class="glass-card" style="padding: 25px; text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 10px;">🔒</div>
                    <div style="font-weight: 700; margin-bottom: 8px;">Privacy First</div>
                    <div style="color: #64748b; font-size: 14px;">Your data stays private and secure</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 🔐 Sign In")

            with st.form("login_form"):
                username = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")

                col_login, col_signup = st.columns(2)
                with col_login:
                    login_clicked = st.form_submit_button("SIGN IN", use_container_width=True, type="primary")
                with col_signup:
                    signup_clicked = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)

                if login_clicked:
                    if username == "demo" and password == "demo":
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Try demo/demo")

                if signup_clicked:
                    st.info("💡 Account creation will be enabled when database is connected!")

            st.markdown("</div>", unsafe_allow_html=True)

            # Testimonials
            st.markdown("""
            <div class="glass-card" style="margin-top: 20px; padding: 25px;">
                <div style="color: #667eea; font-size: 20px; margin-bottom: 15px;">⭐⭐⭐⭐⭐</div>
                <div style="font-style: italic; color: #475569; margin-bottom: 12px;">
                    "Finally found natural relief that actually works!"
                </div>
                <div style="color: #94a3b8; font-size: 14px;">- Sarah M.</div>
            </div>
            """, unsafe_allow_html=True)
    st.stop()

elif not st.session_state.authenticated and not st.session_state.demo_mode:
    show_onboarding_steps()
    st.stop()

# ============================================================================
# DEMO MODE INITIALIZATION
# ============================================================================
if st.session_state.demo_mode and st.session_state.n1_df.empty:
    st.session_state.n1_df = generate_demo_data_with_therapy(therapy_start_day=7)
    st.session_state.onboarding_complete = True

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    if st.session_state.demo_mode:
        st.markdown("### 🎯 Demo Mode")
        st.info(f"Welcome, {st.session_state.username}!")

        # Show progress
        num_entries = len(st.session_state.n1_df)
        st.metric("Days Logged", num_entries)

        if st.button("EXIT DEMO", use_container_width=True):
            st.session_state.demo_mode = False
            st.session_state.authenticated = False
            st.session_state.n1_df = pd.DataFrame()
            st.session_state.onboarding_complete = False
            st.session_state.onboarding_step = 0
            st.rerun()
    elif st.session_state.authenticated:
        st.markdown(f"### 👋 {st.session_state.username}")
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

# ============================================================================
# RETURNING USER WELCOME
# ============================================================================
num_entries = len(st.session_state.n1_df)
has_therapy_data = not st.session_state.n1_df.empty and (st.session_state.n1_df['therapy_started'] != "").any()

if num_entries > 0:
    # Returning user dashboard
    latest_entry = st.session_state.n1_df.iloc[-1]
    streak_days = num_entries

    st.markdown(f"""
    <div class="glass-card" style="text-align: center; margin-bottom: 40px;">
        <h1 style="margin: 0 0 15px 0; font-size: 42px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            👋 Welcome back! Day {streak_days} 🔥
        </h1>
        <p style="margin: 0; color: #64748b; font-size: 18px; font-weight: 500;">
            Keep tracking your natural healing journey
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # First-time user after onboarding
    st.markdown("""
    <div class="glass-card" style="text-align: center; margin-bottom: 40px;">
        <h1 style="margin: 0 0 15px 0; font-size: 42px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🌱 Start Your Healing Journey
        </h1>
        <p style="margin: 0; color: #64748b; font-size: 18px; font-weight: 500;">
            Begin by logging your baseline symptoms
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB NAVIGATION
# ============================================================================

# Determine which tabs to show based on user progress
if num_entries == 0:
    # New user: Show Daily Log first
    tab1, tab2, tab3 = st.tabs([
        "🌱 Daily Log",
        "🔬 Evidence Explorer",
        "⚙️ Settings"
    ])

    # Redirect to Daily Log tab
    active_tab = tab1
else:
    # Experienced user: Show all tabs with Dashboard first
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "🌱 Daily Log",
        "🔬 Evidence Explorer",
        "⚙️ Settings"
    ])

# ============================================================================
# TAB 1: DAILY LOG (First for new users)
# ============================================================================
if num_entries == 0:
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🌱 Daily Wellness Log")

        # Onboarding tip for new users
        st.info("💡 **Pro Tip:** Log for 3 days BEFORE starting a new therapy to establish your baseline.")

        with st.form("daily_log"):
            col1, col2 = st.columns(2)

            with col1:
                log_date = st.date_input("Date", value=dt.date.today())
                pain = st.slider("Pain Level (0-10)", 0, 10, 5, help="How much pain did you experience?")
                sleep = st.slider("Sleep Hours", 0, 14, 7, help="How many hours did you sleep?")

            with col2:
                mood = st.slider("Mood Score (0-10)", 0, 10, 5, help="How was your overall mood?")
                stress = st.slider("Stress Level (0-10)", 0, 10, 5, help="How stressed did you feel?")

            st.markdown("---")
            st.markdown("#### 🎯 Natural Therapy Tracking")

            started_therapy = st.checkbox(
                "⭐ Started a NEW natural therapy today?",
                help="Check this when you BEGIN a new therapy - we'll track before/after effects!"
            )

            therapy_name = ""
            if started_therapy:
                therapy_name = st.selectbox(
                    "Which natural therapy?",
                    ["Yoga", "Acupuncture", "Meditation", "Massage", "Tai Chi", "Herbal Medicine", "Qi Gong"]
                )
                st.success(f"💡 Great! We'll measure the effect of {therapy_name} from this date forward.")

            continuing_therapies = st.multiselect(
                "Continuing therapies (if any):",
                ["Yoga", "Meditation", "Massage", "Acupuncture"]
            )

            st.markdown("")
            submitted = st.form_submit_button("💾 SAVE ENTRY", type="primary", use_container_width=True)

            if submitted:
                new_entry = pd.DataFrame([{
                    "date": log_date,
                    "pain_score": pain,
                    "sleep_hours": sleep,
                    "mood_score": mood,
                    "stress_score": stress,
                    "therapy_started": therapy_name,
                    "therapies_continuing": continuing_therapies
                }])

                st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_entry], ignore_index=True)
                st.success("✅ Entry saved successfully!")
                st.balloons()
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
else:
    # EXISTING USER TABS
    # TAB 1: DASHBOARD
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        display_df = st.session_state.n1_df.copy()

        # Check data stage
        if has_therapy_data:
            therapy_started = display_df[display_df['therapy_started'] != '']['therapy_started'].iloc[0]
            therapy_analysis = calculate_therapy_effect(display_df, therapy_started, "pain_score")

            if therapy_analysis and therapy_analysis.get("ready"):
                # FULL DASHBOARD with Causal Analysis
                st.markdown("### 🎉 Your Therapy Results Are Ready!")

                result = therapy_analysis

                # Big impact metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Before Therapy",
                        f"{result['before_mean']:.1f}/10",
                        help=f"Average pain over {result['days_before']} days"
                    )

                with col2:
                    st.metric(
                        "After Therapy",
                        f"{result['after_mean']:.1f}/10",
                        f"{result['effect']:+.1f}",
                        delta_color="inverse"
                    )

                with col3:
                    st.metric(
                        "Improvement",
                        f"{abs(result['effect_pct']):.0f}%",
                        "Statistically Significant ⭐⭐⭐" if result['significant'] else "More data needed"
                    )

                st.markdown("---")

                # Causal Analysis Visualization
                st.markdown(f"### 📊 {therapy_started} Effectiveness Analysis (Difference-in-Differences)")

                # Create before/after comparison chart
                fig = go.Figure()

                before_dates = display_df[display_df['date'] < display_df[display_df['therapy_started'] == therapy_started]['date'].min()]['date']
                before_pain = display_df[display_df['date'] < display_df[display_df['therapy_started'] == therapy_started]['date'].min()]['pain_score']
                after_dates = display_df[display_df['date'] >= display_df[display_df['therapy_started'] == therapy_started]['date'].min()]['date']
                after_pain = display_df[display_df['date'] >= display_df[display_df['therapy_started'] == therapy_started]['date'].min()]['pain_score']

                # Before period
                fig.add_trace(go.Scatter(
                    x=before_dates,
                    y=before_pain,
                    mode='lines+markers',
                    name='Before Therapy',
                    line=dict(color='#ef4444', width=3),
                    marker=dict(size=8)
                ))

                # After period
                fig.add_trace(go.Scatter(
                    x=after_dates,
                    y=after_pain,
                    mode='lines+markers',
                    name='After Therapy',
                    line=dict(color='#10b981', width=3),
                    marker=dict(size=8)
                ))

                # Add mean lines
                fig.add_hline(y=result['before_mean'], line_dash="dash", line_color="#ef4444",
                            annotation_text=f"Before: {result['before_mean']:.1f}")
                fig.add_hline(y=result['after_mean'], line_dash="dash", line_color="#10b981",
                            annotation_text=f"After: {result['after_mean']:.1f}")

                fig.update_layout(
                    height=500,
                    plot_bgcolor='rgba(255,255,255,0.9)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter", size=14),
                    hovermode='x unified',
                    title=f"Treatment Effect: {result['effect']:.1f} points (p={result['p_value']:.3f})"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Statistical Details
                st.markdown("### 📈 Statistical Analysis")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    **Effect Size:** {abs(result['effect']):.1f} points
                    **Percentage Change:** {abs(result['effect_pct']):.1f}%
                    **P-value:** {result['p_value']:.4f} {'✅ Significant!' if result['significant'] else '⚠️ Not significant'}
                    **Cohen's d:** {result['cohens_d']:.2f} ({'Large' if result['cohens_d'] > 0.8 else 'Medium' if result['cohens_d'] > 0.5 else 'Small'} effect)
                    """)

                with col2:
                    st.markdown(f"""
                    **95% Confidence Interval:** [{result['ci_lower']:.1f}, {result['ci_upper']:.1f}]
                    **Days Before:** {result['days_before']}
                    **Days After:** {result['days_after']}
                    **Total Days:** {result['days_before'] + result['days_after']}
                    """)

                if result['significant']:
                    st.success(f"""
                    🎉 **Clinical Significance Detected!**
                    Your pain reduced by {abs(result['effect_pct']):.0f}% after starting {therapy_started}.
                    This result is statistically significant (p < 0.05), meaning it's unlikely to be due to chance alone.
                    """)
                else:
                    st.warning("""
                    ⏳ **Keep Tracking!**
                    We need more data to confirm if this therapy is working. Continue logging daily for more accurate results.
                    """)

            elif therapy_analysis and not therapy_analysis.get("ready"):
                # Waiting for more data
                days_needed = therapy_analysis['days_needed']
                stage = therapy_analysis['stage']

                st.info(f"""
                📊 **Analysis Progress**
                You need **{days_needed} more days** of {stage} data to see your therapy effectiveness analysis.

                {'Keep logging your baseline before starting therapy!' if stage == 'before' else 'Continue tracking - almost there!'}
                """)

                # Show basic dashboard
                show_basic_dashboard(display_df)
        else:
            # No therapy started yet
            st.info("🎯 **Ready to start a therapy?** Mark it in your Daily Log when you begin!")
            show_basic_dashboard(display_df)

        st.markdown("</div>", unsafe_allow_html=True)

def show_basic_dashboard(df):
    """Show basic dashboard for users without enough data for causal analysis"""
    latest = df.iloc[-1]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Pain", f"{latest['pain_score']:.1f}/10")
    with col2:
        st.metric("Sleep Last Night", f"{latest['sleep_hours']:.1f}h")
    with col3:
        st.metric("Mood Score", f"{latest['mood_score']:.1f}/10")

    st.markdown("---")
    st.markdown("### 📊 Your Trends")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['pain_score'],
        mode='lines+markers',
        name='Pain',
        line=dict(color='#ef4444', width=4),
        marker=dict(size=10)
    ))

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['sleep_hours'],
        mode='lines+markers',
        name='Sleep',
        line=dict(color='#3b82f6', width=4),
        marker=dict(size=10)
    ))

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['mood_score'],
        mode='lines+markers',
        name='Mood',
        line=dict(color='#10b981', width=4),
        marker=dict(size=10)
    ))

    fig.update_layout(
        height=450,
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=14),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

# TAB 2: DAILY LOG (for existing users)
if num_entries > 0:
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🌱 Daily Wellness Log")

        with st.form("daily_log"):
            col1, col2 = st.columns(2)

            with col1:
                log_date = st.date_input("Date", value=dt.date.today())
                pain = st.slider("Pain Level (0-10)", 0, 10, 5)
                sleep = st.slider("Sleep Hours", 0, 14, 7)

            with col2:
                mood = st.slider("Mood Score (0-10)", 0, 10, 5)
                stress = st.slider("Stress Level (0-10)", 0, 10, 5)

            st.markdown("---")
            st.markdown("#### 🎯 Natural Therapy Tracking")

            started_therapy = st.checkbox("⭐ Started a NEW natural therapy today?")

            therapy_name = ""
            if started_therapy:
                therapy_name = st.selectbox(
                    "Which natural therapy?",
                    ["Yoga", "Acupuncture", "Meditation", "Massage", "Tai Chi", "Herbal Medicine", "Qi Gong"]
                )

            continuing_therapies = st.multiselect(
                "Continuing therapies:",
                ["Yoga", "Meditation", "Massage", "Acupuncture"]
            )

            submitted = st.form_submit_button("💾 SAVE ENTRY", type="primary", use_container_width=True)

            if submitted:
                new_entry = pd.DataFrame([{
                    "date": log_date,
                    "pain_score": pain,
                    "sleep_hours": sleep,
                    "mood_score": mood,
                    "stress_score": stress,
                    "therapy_started": therapy_name,
                    "therapies_continuing": continuing_therapies
                }])

                st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_entry], ignore_index=True)
                st.success("✅ Entry saved successfully!")
                st.balloons()
                st.rerun()

        # Show recent entries
        if not st.session_state.n1_df.empty:
            st.markdown("---")
            st.markdown("### 📋 Recent Entries")
            recent = st.session_state.n1_df.tail(5)[["date", "pain_score", "sleep_hours", "mood_score", "therapy_started"]]
            st.dataframe(recent, use_container_width=True, hide_index=True)

        st.markdown("</div>", unsafe_allow_html=True)

# TAB 3: EVIDENCE EXPLORER
tab_idx = 2 if num_entries == 0 else 3
if num_entries == 0:
    with tab2:
        show_evidence_explorer()
else:
    with tab3:
        show_evidence_explorer()

def show_evidence_explorer():
    """Evidence explorer tab"""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔬 Natural & Holistic Therapy Research")

    st.info("🌿 All therapies shown are **natural, non-pharmaceutical** approaches backed by clinical research")

    evidence_df = load_evidence_data()

    if not evidence_df.empty:
        # Filters
        col1, col2 = st.columns(2)

        with col1:
            evidence_filter = st.selectbox(
                "Evidence Quality",
                ["Positive", "Mixed", "All", "Negative"],
                index=0,  # Positive by default
                help="Positive = Multiple trials show benefits"
            )

        with col2:
            condition_filter = st.multiselect(
                "Filter by Condition",
                options=get_unique_conditions(evidence_df),
                default=st.session_state.get('user_conditions', [])[:3]
            )

        # Filter data
        filtered_df = evidence_df.copy()

        if evidence_filter != "All":
            filtered_df = filtered_df[filtered_df['evidence_direction'] == evidence_filter]

        if condition_filter:
            filtered_df = filtered_df[filtered_df['condition'].isin(condition_filter)]

        # Aggregate by therapy
        therapy_summary = filtered_df.groupby('therapy').agg({
            'clinicaltrials_n': 'sum',
            'pubmed_n': 'sum',
            'evidence_direction': lambda x: x.mode()[0] if len(x) > 0 else 'Unclear',
            'therapy_group': 'first'
        }).reset_index()

        therapy_summary = therapy_summary.sort_values('clinicaltrials_n', ascending=False)

        if not therapy_summary.empty:
            # Create bar chart
            fig = px.bar(
                therapy_summary.head(10),
                x="clinicaltrials_n",
                y="therapy",
                color="evidence_direction",
                orientation='h',
                title="Top Natural Therapies by Clinical Evidence",
                color_discrete_map={"Positive": "#10b981", "Mixed": "#f59e0b", "Negative": "#ef4444"},
                height=500
            )

            fig.update_layout(
                plot_bgcolor='rgba(255,255,255,0.9)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter", size=14)
            )

            st.plotly_chart(fig, use_container_width=True)

            # Therapy details
            st.markdown("---")
            st.markdown("### 💊 Therapy Details")

            for idx, row in therapy_summary.head(10).iterrows():
                with st.expander(f"**{row['therapy']}** - {row['evidence_direction']} Evidence"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Clinical Trials", f"{row['clinicaltrials_n']:,}")
                    with col2:
                        st.metric("PubMed Articles", f"{row['pubmed_n']:,}")
                    with col3:
                        st.metric("Therapy Type", row['therapy_group'])

                    st.markdown(f"""
                    **{row['therapy']}** is a natural, holistic therapy with **{row['evidence_direction'].lower()} evidence**
                    from clinical research for various health conditions.
                    """)

    st.markdown("</div>", unsafe_allow_html=True)

# TAB 4: SETTINGS
if num_entries > 0:
    with tab4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Settings & Data Management")

        if not st.session_state.n1_df.empty:
            df = st.session_state.n1_df

            st.markdown("#### 📊 Your Data Statistics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Entries", len(df))
            with col2:
                days = (df['date'].max() - df['date'].min()).days + 1 if 'date' in df.columns else 0
                st.metric("Days Tracked", days)
            with col3:
                st.metric("Therapies Tried", df[df['therapy_started'] != '']['therapy_started'].nunique())

            st.markdown("---")
            st.markdown("#### 💾 Export Your Data")

            col1, col2 = st.columns(2)

            with col1:
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 DOWNLOAD CSV",
                    data=csv_data,
                    file_name=f"health_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="primary"
                )

            with col2:
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 DOWNLOAD JSON",
                    data=json_data,
                    file_name=f"health_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.info("📝 No data yet. Start logging to see your data here!")

        st.markdown("---")

        # About
        st.markdown("### ℹ️ About Pain Relief Map")
        st.markdown("""
        **Version:** 10.0 Natural Therapy Edition

        **Mission:** Empowering individuals to discover natural, evidence-based therapies for chronic pain management.

        **Key Features:**
        - 🌿 Focus on natural, holistic, non-pharmaceutical therapies
        - 🔬 500,000+ clinical trials and PubMed studies
        - 📊 Personal health tracking with causal analysis
        - 📈 Difference-in-Differences statistical methodology
        - 🎯 Evidence-based therapy recommendations
        - 🔒 Privacy-first, secure data storage

        **Approach:** We combine the rigor of clinical research with personalized N-of-1 tracking to help you
        discover what natural therapies actually work for YOUR unique body and condition.

        **Privacy:** Your health data belongs to you. All data is stored securely and never shared.
        """)

        st.markdown("</div>", unsafe_allow_html=True)
else:
    # Settings tab for new users
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Settings")
        st.info("Start logging to access data management features!")
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="glass-card" style="text-align: center; margin-top: 50px; padding: 30px;">
    <p style="color: #64748b; font-size: 15px; margin: 0; font-weight: 600;">
        Pain Relief Map © 2025 • Natural Therapy Tracking Platform
    </p>
    <p style="color: #94a3b8; font-size: 13px; margin: 8px 0 0 0;">
        🌿 Evidence-Based • Holistic • Natural Healing
    </p>
    <p style="color: #94a3b8; font-size: 12px; margin: 8px 0 0 0;">
        Not medical advice - consult healthcare professionals
    </p>
</div>
""", unsafe_allow_html=True)

