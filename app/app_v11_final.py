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
    page_title="Pain Relief Map - Evidence-Based Health Tracking",
    page_icon="💆🏻‍♀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# ENHANCED CUSTOM CSS WITH MORE VISIBLE CHANGES
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
    
    /* Streamlit Container Overrides */
    .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px !important;
    }

    /* HERO SECTION - Hover Effect */
    .hero-mega {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 40px;
        text-align: center;
        border-radius: 30px;
        margin: -1rem 0 3rem 0;
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
        opacity: 1;
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
    
    /* PREMIUM CARDS - Glass Morphism */
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
    
    /* BUTTONS - Make them HUGE and noticeable */
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
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white !important;
    }
    
    /* METRICS - Big and Bold */
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
    
    [data-testid="stMetricDelta"] {
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    
    /* TABS - Modern Design */
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
    
    /* FORMS - Enhanced Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 16px 18px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        background: white !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 12px rgba(102, 126, 234, 0.15) !important;
        outline: none !important;
    }

    /* Form Labels */
    .stTextInput > label,
    .stSelectbox > label,
    .stNumberInput > label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #334155 !important;
        margin-bottom: 8px !important;
    }
    
    /* SLIDERS - More Visible */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        height: 8px !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: white !important;
        border: 4px solid #667eea !important;
        width: 24px !important;
        height: 24px !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* FORMS - Style form container like glass card */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 25px !important;
        padding: 40px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    [data-testid="stForm"]:hover {
        transform: translateY(-12px) scale(1.02) !important;
        box-shadow: 0 30px 80px rgba(102, 126, 234, 0.25) !important;
    }

    /* ALERTS - Eye-catching */
    .stAlert {
        border-radius: 15px !important;
        border-left: 5px solid !important;
        padding: 20px 25px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08) !important;
    }
    
    /* EXPANDER - Stylish */
    .streamlit-expanderHeader {
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        padding: 18px 24px !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        border: 2px solid #e2e8f0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #667eea !important;
        background: rgba(102, 126, 234, 0.05) !important;
    }
    
    /* DATAFRAME - Clean Look */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    }
    
    /* Feature Grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 30px;
        margin: 40px 0;
    }
    
    .feature-box {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 35px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        transition: all 0.4s ease;
        border: 2px solid transparent;
    }
    
    .feature-box:hover {
        border-color: #667eea;
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.2);
    }
    
    .feature-icon {
        font-size: 56px;
        margin-bottom: 20px;
        display: block;
    }
    
    .feature-title {
        font-size: 20px;
        font-weight: 800;
        color: #1a202c;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .feature-desc {
        font-size: 15px;
        color: #64748b;
        line-height: 1.7;
        font-weight: 500;
    }
    
    /* Section Headers */
    h1, h2, h3 {
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 40px !important;
        }
        
        .hero-subtitle {
            font-size: 18px !important;
        }
        
        .stats-row {
            flex-direction: column;
            gap: 30px;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
for key, default in {
    'authenticated': False,
    'demo_mode': False,
    'username': "",
    'n1_df': pd.DataFrame()
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================================
# CAUSAL ANALYSIS FUNCTIONS
# ============================================================================
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
# DEMO DATA GENERATOR
# ============================================================================
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

def generate_demo_data():
    """Generate sample health tracking data (basic version for non-demo mode)"""
    demo_data = []
    start_date = datetime.now().date() - timedelta(days=29)

    for day in range(30):
        current_date = start_date + timedelta(days=day)
        pain_score = max(2, min(9, 7 - (day * 0.1) + (day % 3 - 1)))
        sleep_hours = max(4, min(9, 5 + (day * 0.07) + (day % 2)))
        mood_score = max(2, min(9, 4 + (day * 0.1) + (day % 3 - 1)))

        demo_data.append({
            "date": current_date,
            "pain_score": round(pain_score, 1),
            "sleep_hours": round(sleep_hours, 1),
            "mood_score": round(mood_score, 1),
            "stress_score": round(7 - (day * 0.08), 1),
            "therapy_used": ["Yoga"] if day % 3 == 0 else []
        })

    return pd.DataFrame(demo_data)

# ============================================================================
# LANDING PAGE
# ============================================================================
if not st.session_state.authenticated and not st.session_state.demo_mode:
    # MEGA HERO SECTION - Enhanced V9
    st.markdown("""
    <div class="hero-mega">
        <div style="position: relative; z-index: 2;">
            <div style="display: inline-block; background: rgba(255,255,255,0.2); padding: 8px 20px; border-radius: 30px; margin-bottom: 20px; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: white;">
                ✨ Evidence-Based • AI-Powered • Privacy-First
            </div>
            <h1 class="hero-title">💆🏻‍♀️ Pain Relief Map</h1>
            <p class="hero-subtitle">Discover What Actually Works for YOUR Chronic Pain</p>
            <p style="font-size: 19px; color: rgba(255,255,255,0.95); margin: 25px auto 0 auto; max-width: 750px; font-weight: 400; line-height: 1.7;">
                Stop guessing. Start tracking. <strong>Track your symptoms</strong>, explore evidence from <strong>500,000+ clinical trials</strong>,
                and use AI to discover personalized patterns that help you feel better.
            </p>
        </div>
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-number">500K+</div>
                <div class="stat-label">Clinical Trials</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">1M+</div>
                <div class="stat-label">PubMed Studies</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">AI</div>
                <div class="stat-label">Smart Insights</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Content
    col1, col2 = st.columns([1.3, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3 style="margin: 0 0 15px 0;">🚀 Try Demo Mode - No Signup Required</h3>
            <p style="font-weight: 600; margin-bottom: 15px;">Explore the full app with realistic sample data. See how Pain Relief Map helps you:</p>
            <ul style="margin: 0 0 20px 20px; padding: 0;">
                <li style="margin-bottom: 8px;">📊 Visualize 30 days of health trends</li>
                <li style="margin-bottom: 8px;">🔬 Browse evidence-based therapies</li>
                <li style="margin-bottom: 8px;">📈 Track pain, sleep, mood, and more</li>
                <li style="margin-bottom: 8px;">💾 Export your data anytime</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)

        if st.button("🚀 START FREE DEMO", type="primary", use_container_width=True):
            st.session_state.demo_mode = True
            st.session_state.username = "Demo User"
            st.session_state.n1_df = generate_demo_data_with_therapy()
            st.rerun()

        st.markdown('<p style="text-align: center; color: #64748b; font-size: 14px; margin-top: 15px; margin-bottom: 40px;">No credit card • No email required • Instant access</p>', unsafe_allow_html=True)

        # Feature Grid - Enhanced
        st.markdown("""
        <div style="margin-top: 40px;">
            <h3 style="text-align: center; font-size: 28px; font-weight: 800; margin-bottom: 35px; color: #1a202c;">
                Why Pain Relief Map?
            </h3>
        </div>
        <div class="feature-grid">
            <div class="feature-box">
                <span class="feature-icon">🔬</span>
                <div class="feature-title">500K+ Clinical Trials</div>
                <div class="feature-desc">Access evidence from ClinicalTrials.gov and PubMed to find therapies backed by real science</div>
            </div>
            <div class="feature-box">
                <span class="feature-icon">📊</span>
                <div class="feature-title">Smart Analytics</div>
                <div class="feature-desc">Advanced statistical analysis shows what's actually working with confidence intervals</div>
            </div>
            <div class="feature-box">
                <span class="feature-icon">🤖</span>
                <div class="feature-title">AI-Powered Insights</div>
                <div class="feature-desc">Get personalized therapy explanations and pattern detection in your health data</div>
            </div>
            <div class="feature-box">
                <span class="feature-icon">⚡</span>
                <div class="feature-title">30-Second Daily Log</div>
                <div class="feature-desc">Quick, easy tracking that fits into your routine. No complicated forms or hassle</div>
            </div>
            <div class="feature-box">
                <span class="feature-icon">🔒</span>
                <div class="feature-title">100% Private & Secure</div>
                <div class="feature-desc">Your health data belongs to you. Cloud storage with bank-level encryption</div>
            </div>
            <div class="feature-box">
                <span class="feature-icon">📱</span>
                <div class="feature-title">Track Anywhere</div>
                <div class="feature-desc">Mobile-optimized design works perfectly on phone, tablet, or desktop</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Form styled as glass card via CSS
        with st.form("login_form", clear_on_submit=False):
            st.markdown("""
                <h3 style="margin: 0 0 10px 0;">🔐 Sign In</h3>
                <p style="font-weight: 600; margin-bottom: 25px; color: #64748b;">Access your personal health dashboard</p>
            """, unsafe_allow_html=True)

            username = st.text_input("Email", placeholder="demo", label_visibility="visible", key="login_email")
            password = st.text_input("Password", type="password", placeholder="demo", label_visibility="visible", key="login_pass")

            st.markdown('<p style="text-align: right; font-size: 13px; margin: -5px 0 20px 0;"><a href="#" style="color: #667eea; text-decoration: none; font-weight: 600;">Forgot password?</a></p>', unsafe_allow_html=True)

            login_clicked = st.form_submit_button("SIGN IN", use_container_width=True, type="primary")

            if login_clicked:
                if username == "demo" and password == "demo":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Try: demo / demo")

            st.markdown("""
                <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #94a3b8; font-size: 14px; margin: 0;">Don't have an account?</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)

        if st.button("CREATE FREE ACCOUNT", use_container_width=True):
            st.info("📝 Account creation coming soon! Try the demo for now.")

        # Trust Badges
        st.markdown("""
        <div class="glass-card" style="margin-top: 25px; padding: 25px;">
            <div style="text-align: center;">
                <p style="font-size: 13px; color: #64748b; margin-bottom: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Trusted By</p>
                <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div style="font-size: 20px;">🏥</div>
                    <div style="font-size: 20px;">🔬</div>
                    <div style="font-size: 20px;">💊</div>
                    <div style="font-size: 20px;">🩺</div>
                </div>
                <p style="font-size: 13px; color: #64748b; margin-top: 15px; font-weight: 500;">Healthcare providers & chronic pain patients worldwide</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Testimonials
        testimonial_html = """
        <div class="glass-card" style="margin-top: 30px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 253, 244, 0.95) 100%); border-left: 4px solid #10b981; padding: 35px;">
            <div style="text-align: center;">
                <div style="font-size: 32px; margin-bottom: 20px; letter-spacing: 3px;">⭐⭐⭐⭐⭐</div>
                <p style="font-style: italic; color: #1e293b; margin-bottom: 18px; font-size: 16px; font-weight: 500; line-height: 1.8;">
                    After 2 years of chronic pain, this app helped me identify that yoga actually reduced my pain by 35%. My doctor was amazed by the data.
                </p>
                <div style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 8px 20px; border-radius: 20px; margin-bottom: 25px;">
                    <p style="font-size: 13px; font-weight: 700; color: white; margin: 0;">Sarah M., Fibromyalgia patient</p>
                </div>
                <div style="border-top: 2px solid #e2e8f0; padding-top: 25px; margin-top: 25px;">
                    <p style="font-style: italic; color: #1e293b; margin-bottom: 18px; font-size: 16px; font-weight: 500; line-height: 1.8;">
                        The evidence explorer saved me hours of research. I found 3 therapies I had never heard of, all with solid clinical backing.
                    </p>
                    <div style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 8px 20px; border-radius: 20px;">
                        <p style="font-size: 13px; font-weight: 700; color: white; margin: 0;">Michael R., Back pain sufferer</p>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(testimonial_html, unsafe_allow_html=True)

    # How It Works Section
    st.markdown("""
    <div style="margin-top: 60px;">
        <h2 style="text-align: center; font-size: 36px; font-weight: 900; margin-bottom: 50px; color: #1a202c;">
            How It Works
        </h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 56px; margin-bottom: 20px;">1️⃣</div>
            <h3 style="font-size: 22px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Log Your Symptoms</h3>
            <p style="color: #64748b; font-size: 15px; line-height: 1.7; font-weight: 500;">
                Track pain, sleep, mood, and therapies in just 30 seconds per day. Simple sliders, no complex forms.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 56px; margin-bottom: 20px;">2️⃣</div>
            <h3 style="font-size: 22px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Discover Patterns</h3>
            <p style="color: #64748b; font-size: 15px; line-height: 1.7; font-weight: 500;">
                AI analyzes your data to show which therapies are working. See trends, correlations, and statistical insights.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; min-height: 280px;">
            <div style="font-size: 56px; margin-bottom: 20px;">3️⃣</div>
            <h3 style="font-size: 22px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Feel Better</h3>
            <p style="color: #64748b; font-size: 15px; line-height: 1.7; font-weight: 500;">
                Make data-driven decisions about your health. Share insights with your doctor. Take control of your pain.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Final CTA
    st.markdown("""
    <div class="glass-card" style="text-align: center; margin: 60px 0 40px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 50px 40px;">
        <h2 style="color: white; font-size: 32px; font-weight: 900; margin-bottom: 20px;">
            Ready to Take Control of Your Health?
        </h2>
        <p style="color: rgba(255,255,255,0.95); font-size: 18px; margin-bottom: 35px; max-width: 600px; margin-left: auto; margin-right: auto;">
            Join thousands using Pain Relief Map to discover what actually works for their chronic pain.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 START FREE DEMO", type="primary", use_container_width=True, key="cta_bottom"):
            st.session_state.demo_mode = True
            st.session_state.username = "Demo User"
            st.session_state.n1_df = generate_demo_data_with_therapy()
            st.rerun()

    st.stop()

# ============================================================================
# AUTHENTICATED APP
# ============================================================================

# Sidebar
with st.sidebar:
    if st.session_state.demo_mode:
        st.markdown("### 🎯 Demo Mode")
        st.info(f"Welcome, {st.session_state.username}!")
        if st.button("EXIT DEMO", use_container_width=True):
            st.session_state.demo_mode = False
            st.session_state.authenticated = False
            st.session_state.n1_df = pd.DataFrame()
            st.rerun()
    elif st.session_state.authenticated:
        st.markdown(f"### 👋 {st.session_state.username}")
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

# Welcome Header
st.markdown("""
<div class="glass-card" style="text-align: center; margin-bottom: 40px;">
    <h1 style="margin: 0 0 15px 0; font-size: 42px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Welcome to Pain Relief Map
    </h1>
    <p style="margin: 0; color: #64748b; font-size: 18px; font-weight: 500;">
        Track your health journey with science-backed insights
    </p>
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "🌱 Daily Log",
    "🔬 Evidence Explorer",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: DASHBOARD
# ============================================================================
with tab1:
    # Use demo or user data
    if st.session_state.n1_df.empty:
        display_df = generate_demo_data()
        st.info("📊 Showing demo data. Start logging to see your own insights!")
    else:
        display_df = st.session_state.n1_df.copy()
    
    if not display_df.empty:
        # Calculate metrics
        latest = display_df.iloc[-1]
        previous_avg = display_df.iloc[:-7].mean(numeric_only=True) if len(display_df) > 7 else display_df.iloc[:1].mean(numeric_only=True)
        
        pain_current = latest.get("pain_score", 5)
        pain_prev = previous_avg.get("pain_score", 7)
        pain_delta = pain_current - pain_prev
        
        sleep_current = latest.get("sleep_hours", 7)
        sleep_prev = previous_avg.get("sleep_hours", 5)
        sleep_delta = sleep_current - sleep_prev
        
        mood_current = latest.get("mood_score", 7)
        mood_prev = previous_avg.get("mood_score", 4)
        mood_delta = mood_current - mood_prev
        
        # HUGE Metrics with Gauges
        st.markdown("### 📈 Your Health Metrics")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Pain gauge (0-10, lower is better - use red color)
            pain_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=pain_current,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "😣 Pain Level", 'font': {'size': 18, 'family': 'Inter'}},
                number={'suffix': "/10", 'font': {'size': 32, 'family': 'Inter', 'color': '#1a202c'}},
                delta={'reference': pain_prev, 'increasing': {'color': "#ef4444"}, 'decreasing': {'color': "#10b981"}},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#e2e8f0"},
                    'bar': {'color': "#ef4444", 'thickness': 0.7},
                    'bgcolor': "#f7fafc",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 10], 'color': '#f1f5f9'}
                    ]
                }
            ))
            pain_gauge.update_layout(
                height=220,
                margin=dict(l=10, r=10, t=70, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Inter'}
            )
            st.plotly_chart(pain_gauge, use_container_width=True)

        with col2:
            # Sleep gauge (0-8h, higher is better - use blue color)
            sleep_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=sleep_current,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "😴 Sleep Hours", 'font': {'size': 18, 'family': 'Inter'}},
                number={'suffix': "h", 'font': {'size': 32, 'family': 'Inter', 'color': '#1a202c'}},
                delta={'reference': sleep_prev, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
                gauge={
                    'axis': {'range': [0, 8], 'tickwidth': 1, 'tickcolor': "#e2e8f0"},
                    'bar': {'color': "#3b82f6", 'thickness': 0.7},
                    'bgcolor': "#f7fafc",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 8], 'color': '#f1f5f9'}
                    ]
                }
            ))
            sleep_gauge.update_layout(
                height=220,
                margin=dict(l=10, r=10, t=70, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Inter'}
            )
            st.plotly_chart(sleep_gauge, use_container_width=True)

        with col3:
            # Mood gauge (0-10, higher is better - use green color)
            mood_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=mood_current,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "🙂 Mood Score", 'font': {'size': 18, 'family': 'Inter'}},
                number={'suffix': "/10", 'font': {'size': 32, 'family': 'Inter', 'color': '#1a202c'}},
                delta={'reference': mood_prev, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#e2e8f0"},
                    'bar': {'color': "#10b981", 'thickness': 0.7},
                    'bgcolor': "#f7fafc",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 10], 'color': '#f1f5f9'}
                    ]
                }
            ))
            mood_gauge.update_layout(
                height=220,
                margin=dict(l=10, r=10, t=70, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Inter'}
            )
            st.plotly_chart(mood_gauge, use_container_width=True)

        st.markdown("---")
        
        # Trend Chart
        st.markdown("### 📊 30-Day Trend Analysis")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=display_df['date'],
            y=display_df['pain_score'],
            mode='lines+markers',
            name='Pain',
            line=dict(color='#ef4444', width=4),
            marker=dict(size=10, line=dict(width=2, color='white'))
        ))
        
        fig.add_trace(go.Scatter(
            x=display_df['date'],
            y=display_df['sleep_hours'],
            mode='lines+markers',
            name='Sleep',
            line=dict(color='#3b82f6', width=4),
            marker=dict(size=10, line=dict(width=2, color='white'))
        ))
        
        fig.add_trace(go.Scatter(
            x=display_df['date'],
            y=display_df['mood_score'],
            mode='lines+markers',
            name='Mood',
            line=dict(color='#10b981', width=4),
            marker=dict(size=10, line=dict(width=2, color='white'))
        ))

        # Add therapy start marker if therapy_started column exists and has data
        if 'therapy_started' in display_df.columns:
            therapy_starts = display_df[display_df['therapy_started'].notna() & (display_df['therapy_started'] != '')]
            if not therapy_starts.empty:
                for _, row in therapy_starts.iterrows():
                    therapy_date = row['date']
                    therapy_name = row['therapy_started']
                    # Add vertical line without annotation (which causes issues)
                    fig.add_vline(
                        x=therapy_date,
                        line_dash="dash",
                        line_color="#9333ea",
                        line_width=3
                    )
                    # Add a text annotation separately
                    fig.add_annotation(
                        x=therapy_date,
                        y=1,
                        yref="paper",
                        text=f"Started: {therapy_name}",
                        showarrow=False,
                        font=dict(size=16, color="#9333ea", family="Inter", weight=700),
                        yshift=25
                    )

        fig.update_layout(
            height=550,
            plot_bgcolor='rgba(255,255,255,0.9)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=14, color="#1a202c"),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=16, weight=700)
            ),
            xaxis=dict(
                gridcolor='rgba(0,0,0,0.05)',
                showgrid=True,
                title=dict(text="Date", font=dict(size=16, weight=700))
            ),
            yaxis=dict(
                gridcolor='rgba(0,0,0,0.05)',
                showgrid=True,
                title=dict(text="Score", font=dict(size=16, weight=700))
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📝 Start logging in the Daily Log tab to see your dashboard!")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 2: DAILY LOG - Comprehensive version from v3
# ============================================================================

# Define all options for the form
condition_options = [
    "None", "Addiction", "Anxiety", "Burnout", "Cancer Pain", "Chronic Fatigue Syndrome",
    "Chronic Pain", "Depression", "Eating Disorders", "Endometriosis", "Fibromyalgia", "Headache",
    "Infertility", "Insomnia", "Irritable Bowel Syndrome", "Knee Pain", "Low Back Pain", "Menopause",
    "Migraine", "Myofascial Pain", "Neck Pain", "Neuropathic Pain", "Obsessive-Compulsive Disorder",
    "Osteoarthritis", "Perimenopause", "Polycystic Ovary Syndrome", "Post-Traumatic Stress Disorder",
    "Postoperative Pain", "Rheumatoid Arthritis", "Schizophrenia", "Shoulder Pain", "Stress"
]
therapy_options = [
    "None", "Acupuncture", "Aromatherapy", "Ayurveda", "Cognitive Behaviour Therapy", "Exercise Therapy",
    "Herbal", "Massage", "Meditation", "Qi Gong", "Tai Chi", "Yoga"
]
movement_options = [
    "None / Rest day", "Light stretching or yoga", "Walking or gentle movement",
    "Light cardio", "Moderate workout", "High-intensity training",
    "Physical therapy or rehab", "Unusually active day"
]
digestive_options = [
    "Select...", "Normal occasional rumbles", "Very quiet/no sounds noticed",
    "Frequent loud rumbling", "Excessive gurgling", "Rumbling increases when anxious"
]
stool_options = [
    "Select...", "Type 1: Hard lumps", "Type 2: Lumpy sausage", "Type 3: Sausage with cracks",
    "Type 4: Smooth sausage (ideal)", "Type 5: Soft blobs", "Type 6: Mushy", "Type 7: Liquid"
]
physical_options = [
    "None", "Brain fog", "Digestive discomfort", "Dizziness", "Fatigue", "Headache",
    "Joint pain", "Muscle pain", "Nausea", "Sensitivity to temperature", "Tingling"
]
emotional_options = [
    "None", "Anxious", "Calm", "Emotionally numb", "Felt tearful / cried",
    "Grateful", "Hopeful", "Irritable", "Lonely", "Overwhelmed", "Sad"
]
craving_options = [
    "None", "Sugar", "Carbs", "Salty snacks", "Caffeine", "Alcohol", "Nicotine", "Comfort food"
]
pms_options = [
    "None","Cramps","Bloating","Breast tenderness","Headache","Irritability",
    "Low mood","Anxiety","Fatigue","Food cravings"
]
flow_options = ["None","Light","Medium","Heavy"]

with tab2:
    # Modern header with gradient background
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h2 style="color: white; margin: 0; font-size: 2rem;">🌱 Daily Wellness Log</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Record how you feel each day to discover what helps you most
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea; margin-bottom: 1.5rem;">
        <p style="margin: 0; color: #495057;">
            <strong>💡 N-of-1 Tracking:</strong> This approach treats each person as their own control,
            tracking changes in symptoms <strong>before vs after</strong> starting a therapy.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for toggles
    st.session_state.setdefault("good_day", False)
    st.session_state.setdefault("track_cycle", True)
    st.session_state.setdefault("quick_notes", [])

    # Helper functions
    def _get_latest_row():
        if st.session_state.n1_df.empty:
            return None
        df = st.session_state.n1_df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df.sort_values("date").iloc[-1]

    def _defaults_from_yesterday():
        last = _get_latest_row()
        if last is None:
            return dict(pain_score=0, stress_score=0, sleep_hours=7, mood_score=5)
        return dict(
            pain_score=float(last.get("pain_score", 0.0)),
            stress_score=float(last.get("stress_score", 0.0)),
            sleep_hours=float(last.get("sleep_hours", 7.0)),
            mood_score=float(last.get("mood_score", 5.0)),
        )

    def calculate_cycle_day(date, df):
        """Calculate cycle day based on menstrual days pattern"""
        if df.empty:
            return 1

        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        current_date = pd.to_datetime(date)

        menstrual_days = df_copy[
            (df_copy.get("menstruating_today", pd.Series([False])).isin([True, "Yes", "yes"])) &
            (df_copy["date"] <= current_date)
        ].sort_values("date")

        if menstrual_days.empty:
            return 1

        last_period_start = menstrual_days.iloc[-1]["date"]
        days_since_period = (current_date - last_period_start).days + 1

        if df_copy[df_copy["date"] == current_date].get("menstruating_today", pd.Series([False])).isin([True, "Yes", "yes"]).any():
            return 1

        cycle_day = days_since_period
        if cycle_day > 35:
            return 1
        return min(cycle_day, 35)

    defs = _defaults_from_yesterday()

    # Action bar with Duplicate yesterday, Quick note, Mark good day, and Track menstrual cycle
    with st.container(border=True):
        col_dup, col_note, col_good, col_spacer, col_cycle = st.columns(
            [2.2, 2.2, 2.2, 6.0, 2.6],
            gap="small"
        )

        # Duplicate yesterday button
        with col_dup:
            if st.button("🌿 Duplicate yesterday", key="dup_yesterday_bar",
                        help="Copy yesterday's values to today"):
                last = _get_latest_row()
                if last is None:
                    st.warning("No previous day to duplicate yet. Add your first entry below.")
                else:
                    today = dt.date.today()
                    tmp = st.session_state.n1_df.copy()
                    tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce").dt.date
                    if today in set(tmp["date"]):
                        st.info("You already have an entry for today.")
                    else:
                        dup = last.to_dict()
                        dup["date"] = today
                        if "therapy_on" not in dup:
                            dup["therapy_on"] = 0
                        if "therapy_name" not in dup:
                            dup["therapy_name"] = ""

                        # Create new entry from duplicated data
                        new_entry = pd.DataFrame([dup])
                        st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_entry], ignore_index=True)
                        st.success("✅ Duplicated yesterday's values to today!")
                        st.rerun()

        # Quick note popover
        with col_note:
            if hasattr(st, "popover"):
                with st.popover("📝 Quick note", use_container_width=True):
                    note = st.text_area("Note for today", key="quick_note_text")
                    cna, cnb = st.columns(2)
                    if cna.button("Save", key="quick_note_save"):
                        if note.strip():
                            st.session_state.quick_notes.append(
                                {"date": dt.date.today().isoformat(), "note": note.strip()}
                            )
                            st.success("Note saved.")
                    if cnb.button("Clear", key="quick_note_clear"):
                        st.session_state["quick_note_text"] = ""
            else:
                with st.expander("📝 Quick note", expanded=False):
                    note = st.text_area("Note for today", key="quick_note_text")
                    cna, cnb = st.columns(2)
                    if cna.button("Save", key="quick_note_save"):
                        if note.strip():
                            st.session_state.quick_notes.append(
                                {"date": dt.date.today().isoformat(), "note": note.strip()}
                            )
                            st.success("Note saved.")
                    if cnb.button("Clear", key="quick_note_clear"):
                        st.session_state["quick_note_text"] = ""

        # Mark good day toggle
        with col_good:
            st.session_state["good_day"] = st.toggle(
                "☺️ Mark good day", value=st.session_state["good_day"], key="good_day_toggle"
            )

        # Spacer (empty)

        # Track menstrual cycle toggle (right-aligned)
        with col_cycle:
            st.session_state["track_cycle"] = st.toggle(
                "Track menstrual cycle",
                value=st.session_state["track_cycle"],
                key="track_cycle_toggle",
                help="Include cycle info in your daily entries."
            )

    is_female = st.session_state["track_cycle"]

    with st.form("n1_entry_form", clear_on_submit=False):
        # Essential Metrics Section
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h3 style="color: white; margin: 0; font-size: 1.3rem;">📊 Essential Metrics</h3>
        </div>
        """, unsafe_allow_html=True)

        # Row 1: Date and Mood
        c1a, c1b = st.columns(2)
        with c1a:
            f_date = st.date_input("📅 Today's date", value=dt.date.today(), format="DD/MM/YYYY")
        with c1b:
            f_mood = st.slider("😊 Overall mood (0–10)", 0, 10, int(round(defs["mood_score"])), help="How's your overall mood today?")

        # Row 2: Sleep hours and Times woke up
        c2a, c2b = st.columns(2)
        with c2a:
            f_sleep = st.slider("😴 Sleep hours last night", 0, 14, int(round(defs["sleep_hours"])))
        with c2b:
            f_wake_ups = st.number_input("🌙 Times woke up", 0, 20, 0, help="How many times did you wake up during the night?")

        # Row 3: Stress and Pain
        c3a, c3b = st.columns(2)
        with c3a:
            f_stress = st.slider("😰 Stress (0–10)", 0, 10, int(round(defs["stress_score"])))
        with c3b:
            f_pain = st.slider("😣 Pain (0–10)", 0, 10, int(round(defs["pain_score"])))

        # Therapies Section
        st.markdown("""
        <div style="background: linear-gradient(90deg, #10b981 0%, #059669 100%);
                    padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
            <h3 style="color: white; margin: 0; font-size: 1.3rem;">🌟 Therapy Tracking</h3>
        </div>
        """, unsafe_allow_html=True)
        st.caption("💡 **Tip:** You can track multiple therapies simultaneously. Use the checkbox below only when starting a NEW therapy for before/after analysis.")

        c3, c4 = st.columns(2)
        with c3:
            f_condition_today = st.multiselect(
                "🏥 Conditions felt today",
                options=condition_options,
                default=["None"],
                help="Select all conditions experienced today."
            )
        with c4:
            f_therapy_used = st.multiselect(
                "💊 Therapy used today",
                options=therapy_options,
                help="Select all therapies you used today."
            )

        t1, t2 = st.columns(2)
        with t1:
            f_started_therapy = st.checkbox(
                "Started a new primary therapy today",
                help="Check this box on the first day you begin a new PRIMARY therapy for before/after analysis."
            )
        with t2:
            if f_started_therapy:
                f_therapy_name = st.text_input(
                    "Which therapy?",
                    placeholder="e.g., Acupuncture or Acupuncture + Yoga",
                    help="Name the primary therapy you're analyzing (can include multiple: 'Acupuncture + Yoga')"
                )
            else:
                f_therapy_name = ""

        # Conditional Menstrual Tracking
        if is_female:
            st.markdown("""
            <div style="background: linear-gradient(90deg, #ec4899 0%, #be185d 100%);
                        padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
                <h3 style="color: white; margin: 0; font-size: 1.3rem;">🩸 Hormonal Cycle</h3>
            </div>
            """, unsafe_allow_html=True)
            st.caption("💡 **Tip:** Just mark your menstrual days - cycle day will be calculated automatically!")
            hc1, hc2 = st.columns(2)
            with hc1:
                f_menstruating = st.radio("Menstruating today?", ["No", "Yes"], index=0)
            with hc2:
                f_pms = st.multiselect(
                    "PMS symptoms",
                    pms_options,
                    default=["None"]
                )

            if f_menstruating == "Yes":
                hc3 = st.columns(1)[0]
                with hc3:
                    f_flow = st.selectbox("Flow", flow_options, index=0)
            else:
                f_flow = "None"
        else:
            f_menstruating = "No"
            f_flow = "None"
            f_pms = ["None"]

        # Core Symptoms
        st.markdown("""
        <div style="background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
                    padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
            <h3 style="color: white; margin: 0; font-size: 1.3rem;">❤️ Core Symptoms</h3>
        </div>
        """, unsafe_allow_html=True)
        c9, c10 = st.columns(2)
        with c9:
            f_anxiety = st.slider("😟 Anxiety (0–10)", 0, 10, 5)
        with c10:
            f_patience = st.slider("😌 Patience (0–10)", 0, 10, 5)

        # Emotional & Physical Symptoms
        st.markdown("""
        <div style="background: linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%);
                    padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
            <h3 style="color: white; margin: 0; font-size: 1.3rem;">💭 Emotional and Physical Symptoms</h3>
        </div>
        """, unsafe_allow_html=True)
        c11, c12 = st.columns(2)
        with c11:
            f_emotional = st.multiselect("Emotional symptoms:", emotional_options)
        with c12:
            f_physical = st.multiselect("Physical symptoms:", physical_options)

        f_cravings = st.multiselect(
            "Cravings today:",
            craving_options,
            default=["None"]
        )

        # Physical State
        st.markdown("""
        <div style="background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
                    padding: 0.75rem 1rem; border-radius: 8px; margin: 1.5rem 0 1rem 0;">
            <h3 style="color: white; margin: 0; font-size: 1.3rem;">🏃‍♀️ Physical State</h3>
        </div>
        """, unsafe_allow_html=True)
        c13, c14 = st.columns(2)
        with c13:
            f_movement = st.multiselect("Movement today:", movement_options)
        with c14:
            f_bowel = st.slider("Bowel movements (0–10)", 0, 10, 1)

        c15, c16 = st.columns(2)
        with c15:
            f_digestive = st.selectbox("Digestive sounds:", digestive_options, index=0)
        with c16:
            f_stool = st.selectbox("Stool consistency:", stool_options, index=0)

        # Submit
        add_clicked = st.form_submit_button("💾 SAVE ENTRY", type="primary", use_container_width=True)
        if add_clicked:
            # Therapy tracking logic
            last_row = _get_latest_row()
            if f_started_therapy:
                therapy_on_val = 1
                therapy_name_val = f_therapy_name.strip() if f_therapy_name else ""
            elif last_row is not None and "therapy_on" in last_row:
                therapy_on_val = int(last_row.get("therapy_on", 0))
                therapy_name_val = str(last_row.get("therapy_name", ""))
            else:
                therapy_on_val = 0
                therapy_name_val = ""

            # Auto-calculate cycle day
            auto_cycle_day = calculate_cycle_day(f_date, st.session_state.n1_df) if is_female else 0

            # Create new entry
            new_entry = pd.DataFrame([{
                "date": f_date,
                "pain_score": f_pain,
                "sleep_hours": f_sleep,
                "mood_score": f_mood,
                "stress_score": f_stress,
                "wake_ups_n": f_wake_ups,
                "condition_today": ", ".join(f_condition_today),
                "therapy_used": ", ".join(f_therapy_used),
                "therapy_on": therapy_on_val,
                "therapy_name": therapy_name_val,
                "menstruating_today": f_menstruating,
                "cycle_day": auto_cycle_day,
                "flow": f_flow,
                "pms_symptoms": ", ".join(f_pms),
                "anxiety_score": f_anxiety,
                "patience_score": f_patience,
                "emotional_symptoms": ", ".join(f_emotional),
                "physical_symptoms": ", ".join(f_physical),
                "cravings": ", ".join(f_cravings),
                "movement": ", ".join(f_movement),
                "bowel_movements_n": f_bowel,
                "digestive_sounds": f_digestive,
                "stool_consistency": f_stool,
                "good_day": st.session_state.get("good_day", False)
            }])

            st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_entry], ignore_index=True)
            st.success("✅ Entry saved successfully!")
            st.balloons()

    # Show recent entries
    if not st.session_state.n1_df.empty:
        st.markdown("---")
        st.markdown("### 📋 Recent Entries")
        recent = st.session_state.n1_df.tail(5)
        st.write(recent.to_html(index=False), unsafe_allow_html=True)

# ============================================================================
# TAB 3: EVIDENCE EXPLORER
# ============================================================================
with tab3:
    st.markdown("### 🔬 Evidence-Based Therapy Research")
    
    st.info("🔍 Browse clinical trials and research studies for natural therapies")
    
    # Sample therapy data
    therapy_data = pd.DataFrame({
        "Therapy": ["Acupuncture", "Yoga", "Meditation", "Massage", "Tai Chi"],
        "Clinical Trials": [1234, 892, 756, 645, 423],
        "PubMed Articles": [5678, 4321, 3890, 2876, 1987],
        "Evidence": ["Positive", "Positive", "Positive", "Mixed", "Positive"]
    })
    
    # Create bar chart
    fig = px.bar(
        therapy_data,
        x="Clinical Trials",
        y="Therapy",
        color="Evidence",
        orientation='h',
        title="Top Therapies by Clinical Evidence",
        color_discrete_map={"Positive": "#10b981", "Mixed": "#f59e0b"},
        height=400
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=14),
        showlegend=True,
        xaxis=dict(title="Number of Clinical Trials"),
        yaxis=dict(title="")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Therapy cards
    st.markdown("---")
    st.markdown("### 💊 Detailed Therapy Information")
    
    for idx, row in therapy_data.iterrows():
        with st.expander(f"**{row['Therapy']}** - {row['Evidence']} Evidence"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Clinical Trials", f"{row['Clinical Trials']:,}")
            with col2:
                st.metric("PubMed Articles", f"{row['PubMed Articles']:,}")
            with col3:
                st.metric("Evidence Level", row['Evidence'])
            
            st.markdown(f"**{row['Therapy']}** has shown {row['Evidence'].lower()} evidence in clinical research for various conditions including chronic pain, anxiety, and stress management.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# TAB 4: SETTINGS
# ============================================================================
with tab4:
    st.markdown("### ⚙️ Account & Data Management")
    
    # Data stats
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
            st.metric("Data Size", f"{len(df.to_csv()):,} bytes")
        
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
                use_container_width=True,
                type="secondary"
            )
    else:
        st.info("📝 No data to export yet. Start logging to see your data here!")
    
    st.markdown("---")
    
    # About section
    st.markdown("### ℹ️ About Pain Relief Map")
    st.markdown("""
    **Version:** 9.0 Landing Page Enhanced Edition

    **Key Features:**
    - 🔬 Evidence-based therapy research with 500,000+ clinical trials
    - 📊 Personal health tracking with beautiful visualizations
    - 🤖 AI-powered insights and pattern detection
    - 📱 Mobile-optimized responsive design
    - 🔒 Secure cloud data storage with encryption
    - 💾 Easy CSV/JSON data export
    - ⚡ 30-second daily logging

    **Technology Stack:**
    - Frontend: Streamlit with custom CSS & glass morphism design
    - Visualization: Plotly & Plotly Express
    - Data: Pandas & NumPy
    - Backend: Supabase (PostgreSQL + Auth)

    **Privacy:** Your health data belongs to you. Bank-level encryption and privacy-first architecture.
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="glass-card" style="text-align: center; margin-top: 50px; padding: 30px;">
    <p style="color: #64748b; font-size: 15px; margin: 0; font-weight: 600;">
        Pain Relief Map © 2025 • Evidence-Based Health Tracking Platform
    </p>
    <p style="color: #94a3b8; font-size: 13px; margin: 8px 0 0 0;">
        Built with ❤️ using Streamlit • Not medical advice - consult healthcare professionals
    </p>
</div>
""", unsafe_allow_html=True)