# Pain Relief Map V5 - Modern Design with Complete Functionality
import streamlit as st

# Page config MUST be the very first Streamlit command
st.set_page_config(
    page_title="Pain Relief Map",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from pathlib import Path
import sys
import datetime as dt
import os

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import re

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# Root for relative paths
ROOT = Path(__file__).resolve().parents[1]

# Ensure local imports resolve if needed
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# -----------------------------------------------------------------------------
# Authentication Setup
# -----------------------------------------------------------------------------
try:
    from src.auth import AuthManager, init_session_state
    from src.login_ui import require_authentication, show_user_menu
    from src.db_operations import DatabaseManager
    
    # Initialize managers
    auth_manager = AuthManager()
    db_manager = DatabaseManager()
    
    # Initialize session state for authentication
    init_session_state()
    
    AUTH_ENABLED = auth_manager.is_enabled()
except ImportError as e:
    st.warning("⚠️ Authentication modules not found. Running in session-only mode.")
    AUTH_ENABLED = False
    auth_manager = None
    db_manager = None

# Check authentication if enabled
if AUTH_ENABLED:
    if not require_authentication(auth_manager):
        st.stop()
    show_user_menu(auth_manager)

# Demo mode check
demo_mode = st.session_state.get("demo_mode", not AUTH_ENABLED)

# -----------------------------------------------------------------------------
# Data loading (supports data/evidence_counts.csv and data/raw/evidence_counts.csv)
# -----------------------------------------------------------------------------

def _locate_evidence_csv() -> Path | None:
    here = ROOT / "data"
    candidates = [
        here / "evidence_counts.csv",
        here / "raw" / "evidence_counts.csv",
        ROOT / "evidence_counts.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

@st.cache_data
def load_evidence() -> pd.DataFrame:
    csv_path = _locate_evidence_csv()
    if csv_path is None:
        st.error("❌ Could not find evidence_counts.csv. Please ensure the data file exists.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"❌ Error loading evidence data: {e}")
        return pd.DataFrame()

# Load evidence data
evidence = load_evidence()

# Helper functions
def _contains_any(df, col, selected):
    if not selected:
        return pd.Series([True] * len(df), index=df.index)
    pattern = "|".join(re.escape(str(s)) for s in selected)
    return df[col].fillna("").astype(str).str.contains(pattern, regex=True)

_def_num = lambda s: pd.to_numeric(s, errors="coerce")

# Defaults - use comprehensive condition list
cond_options = [
    "Addiction", "Anxiety", "Burnout", "Cancer Pain", "Chronic Fatigue Syndrome", 
    "Chronic Pain", "Depression", "Eating Disorders", "Endometriosis", "Fibromyalgia", "Headache", 
    "Infertility", "Insomnia", "Irritable Bowel Syndrome", "Knee Pain", "Low Back Pain", "Menopause", 
    "Migraine", "Myofascial Pain", "Neck Pain", "Neuropathic Pain", "Obsessive-Compulsive Disorder", 
    "Osteoarthritis", "Perimenopause", "Polycystic Ovary Syndrome", "Post-Traumatic Stress Disorder", 
    "Postoperative Pain", "Rheumatoid Arthritis", "Schizophrenia", "Shoulder Pain", "Stress"
]
default_condition = "Anxiety"

# --- safer year bounds ---
if "year_min" in evidence:
    ymins = pd.to_numeric(evidence["year_min"], errors="coerce")
    year_lo = int(np.nanmin(ymins)) if not ymins.dropna().empty else 1990
else:
    year_lo = 1990

if "year_max" in evidence:
    ymaxs = pd.to_numeric(evidence["year_max"], errors="coerce")
    year_hi = int(np.nanmax(ymaxs)) if not ymaxs.dropna().empty else dt.date.today().year
else:
    year_hi = dt.date.today().year

# Default to last 15 years from current year
current_year = dt.date.today().year
default_lo = max(year_lo, current_year - 15)

# Evidence direction: provide all options with Positive selected by default
evdir_opts = ["Positive", "Mixed", "Negative", "Unclear"]
default_evdir = ["Positive"]

# Smart UX: Track first vs returning users
if AUTH_ENABLED and not demo_mode:
    user = st.session_state.get("user")
    if user and hasattr(user, 'id'):
        # Check if this is first time seeing this user in this session
        if "user_welcome_shown" not in st.session_state:
            st.session_state.user_welcome_shown = True
            # Check if user has any logs
            user_df = db_manager.get_user_logs(user.id)
            st.session_state.is_first_time_user = user_df.empty

# Custom CSS for modern dashboard design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Demo Banner */
    .demo-banner {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #93c5fd;
        padding: 12px 24px;
        margin: 0 0 1rem 0;
        border-radius: 12px;
    }
    
    .demo-banner p {
        margin: 0;
        font-size: 14px;
        color: #1e40af;
        font-weight: 500;
    }
    
    /* Header Styles */
    .header-container {
        background: white;
        border-bottom: 1px solid #e2e8f0;
        padding: 24px 0;
        margin: 0 -1rem;
    }
    
    .app-title {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        text-align: center;
        display: block;
    }
    
    .app-subtitle {
        font-size: 14px;
        color: #64748b;
        margin: 4px 0 0 0;
        text-align: center;
    }
    
    /* Tab Styles */
    .tab-container {
        display: flex;
        gap: 32px;
        border-top: 1px solid #e2e8f0;
        padding-top: 16px;
        margin-top: 24px;
    }
    
    .tab-button {
        background: none;
        border: none;
        padding: 8px 0;
        font-size: 14px;
        font-weight: 500;
        color: #64748b;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .tab-button:hover {
        color: #0f172a;
    }
    
    .tab-button.active {
        color: #2563eb;
        border-bottom-color: #2563eb;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .metric-card.pain {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    }
    
    .metric-card.sleep {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    }
    
    .metric-card.mood {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
    
    .metric-emoji {
        font-size: 32px;
        margin-bottom: 16px;
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    
    .metric-unit {
        font-size: 18px;
        color: #64748b;
        margin-left: 4px;
    }
    
    .metric-label {
        font-size: 12px;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .trend-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    .trend-badge.up {
        background: #dcfce7;
        color: #166534;
    }
    
    .trend-badge.down {
        background: #fee2e2;
        color: #dc2626;
    }
    
    .metric-change {
        font-size: 14px;
        font-weight: 600;
        margin-top: 8px;
    }
    
    .metric-change.positive {
        color: #16a34a;
    }
    
    .metric-change.negative {
        color: #dc2626;
    }
    
    /* Insight Box */
    .insight-box {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 32px;
    }
    
    .insight-title {
        font-size: 16px;
        font-weight: 600;
        color: #0f172a;
        margin: 0 0 8px 0;
    }
    
    .insight-text {
        font-size: 14px;
        color: #374151;
        margin: 0;
        line-height: 1.5;
    }
    
    .insight-highlight {
        font-weight: 700;
        color: #059669;
    }
    
    /* Sidebar */
    .sidebar-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        position: sticky;
        top: 24px;
    }
    
    .sidebar-title {
        font-size: 16px;
        font-weight: 600;
        color: #0f172a;
        margin: 0 0 16px 0;
    }
    
    .feature-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    .feature-icon {
        font-size: 16px;
        color: #2563eb;
    }
    
    .feature-title {
        font-size: 14px;
        font-weight: 500;
        color: #0f172a;
        margin: 0 0 4px 0;
    }
    
    .feature-desc {
        font-size: 12px;
        color: #64748b;
        margin: 0;
        line-height: 1.4;
    }
    
    /* Chart Container */
    .chart-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin: 48px 0;
    }
    
    .chart-title {
        font-size: 18px;
        font-weight: 600;
        color: #0f172a;
        margin: 0 0 24px 0;
    }
    
    /* Therapy Badge */
    .therapy-badge {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        display: inline-block;
        margin-bottom: 32px;
    }
    
    .therapy-label {
        font-size: 14px;
        color: #64748b;
    }
    
    .therapy-name {
        font-size: 14px;
        font-weight: 600;
        color: #0f172a;
        margin-left: 8px;
    }
    
    /* Progress Bars */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: rgba(148, 163, 184, 0.2);
        border-radius: 4px;
        overflow: hidden;
        margin-top: 16px;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .progress-fill.pain {
        background: linear-gradient(90deg, #f87171, #ef4444);
    }
    
    .progress-fill.sleep {
        background: linear-gradient(90deg, #60a5fa, #3b82f6);
    }
    
    .progress-fill.mood {
        background: linear-gradient(90deg, #34d399, #10b981);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .app-title {
            font-size: 24px;
        }
        
        .metric-card {
            padding: 16px;
        }
        
        .metric-value {
            font-size: 28px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'dashboard'

# Demo mode banner (only show when in demo mode)
if demo_mode:
    st.markdown("""
    <div class="demo-banner">
        <p><strong>Demo Mode:</strong> Your data is temporary. Login or create an account to save permanently.</p>
    </div>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 24px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 class="app-title">💆🏻‍♀️ Pain Relief Map</h1>
            <p class="app-subtitle">Track your health journey with science-backed insights</p>
        </div>
    </div>
</div>

""", unsafe_allow_html=True)

# Check if user has any data
has_data = not st.session_state.n1_df.empty if "n1_df" in st.session_state else False

# Demo data toggle (will be used in Dashboard and Calendar)
show_demo = demo_mode or (not has_data)

# Load display data (either demo or user data)
if show_demo:
    # Load demo data
    demo_path = ROOT / "data" / "templates" / "n_of_1_demo.csv"
    if demo_path.exists():
        display_df = pd.read_csv(demo_path)
        display_df["date"] = pd.to_datetime(display_df["date"])
    else:
        display_df = pd.DataFrame()
elif has_data:
    display_df = st.session_state.n1_df.copy()
    display_df["date"] = pd.to_datetime(display_df["date"], errors="coerce")
else:
    display_df = pd.DataFrame()

# Tab selection using Streamlit's native tabs (5 tabs total)
# Dashboard first in demo mode, Daily Log first for authenticated users
if demo_mode:
    # Demo mode: Dashboard first to showcase the app
    tab_dashboard, tab_analysis, tab_calendar, tab_evidence, tab_settings = st.tabs([
        "🏠 Dashboard",
        "🌱 Daily Log",
        "📅 Calendar",
        "🔬 Evidence Explorer",
        "⚙️ Settings"
    ])
else:
    # Authenticated: Daily Log first for quick access
    tab_analysis, tab_dashboard, tab_calendar, tab_evidence, tab_settings = st.tabs([
        "🌱 Daily Log",
        "🏠 Dashboard",
        "📅 Calendar",
        "🔬 Evidence Explorer",
        "⚙️ Settings"
    ])

# Sample data for demo
metrics_data = {
    'pain': {
        'current': 3,
        'previous': 7.4,
        'change': -4.0,
        'change_percent': -54,
        'trend': 'down',
        'emoji': '😣',
        'unit': '/10'
    },
    'sleep': {
        'current': 8.0,
        'previous': 5.7,
        'change': 2.3,
        'change_percent': 40,
        'trend': 'up',
        'emoji': '😴',
        'unit': 'h'
    },
    'mood': {
        'current': 7,
        'previous': 3.6,
        'change': 3.4,
        'change_percent': 94,
        'trend': 'up',
        'emoji': '😊',
        'unit': '/10'
    }
}

# Generate trend data
dates = pd.date_range(start='2025-09-27', end='2025-10-10', freq='D')
trend_data = []

for i, date in enumerate(dates):
    day_num = i
    if day_num < 5:  # Before therapy
        pain = 8 - (day_num * 0.1) + np.random.normal(0, 0.3)
        sleep = 4.5 + (day_num * 0.1) + np.random.normal(0, 0.2)
        mood = 3 + (day_num * 0.1) + np.random.normal(0, 0.2)
    else:  # After therapy starts
        days_since_therapy = day_num - 5
        pain = 6.8 - (days_since_therapy * 0.4) + np.random.normal(0, 0.2)
        sleep = 6 + (days_since_therapy * 0.3) + np.random.normal(0, 0.2)
        mood = 5 + (days_since_therapy * 0.3) + np.random.normal(0, 0.2)
    
    trend_data.append({
        'date': date.strftime('%b %d'),
        'pain': max(0, min(10, pain)),
        'sleep': max(0, min(12, sleep)),
        'mood': max(0, min(10, mood))
    })

trend_df = pd.DataFrame(trend_data)

# Dashboard Tab
with tab_dashboard:
    # Main layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("""
        <div class="sidebar-card">
            <h3 class="sidebar-title">Your Personal Health Dashboard</h3>
            <div class="feature-item">
                <span class="feature-icon">📊</span>
                <div>
                    <p class="feature-title">Trend Charts</p>
                    <p class="feature-desc">Track your pain, sleep, mood, and stress over time</p>
                </div>
            </div>
            <div class="feature-item">
                <span class="feature-icon">🔍</span>
                <div>
                    <p class="feature-title">Therapy Analysis</p>
                    <p class="feature-desc">See if treatments are working with statistical confidence</p>
                </div>
            </div>
            <div class="feature-item">
                <span class="feature-icon">🎯</span>
                <div>
                    <p class="feature-title">Pattern Recognition</p>
                    <p class="feature-desc">Discover what helps you most</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Key Insight
        st.markdown("""
        <div class="insight-box">
            <p class="insight-title">✨ Excellent progress with Acupuncture!</p>
            <p class="insight-text">
                Since starting therapy on Oct 2, your pain decreased by <span class="insight-highlight">54%</span>, 
                sleep improved by <span class="insight-highlight">2.3 hours</span>, and mood boosted by 
                <span class="insight-highlight">96%</span>. Keep up the treatment! 🎉
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Therapy Info
        st.markdown("""
        <div class="therapy-badge">
            <span class="therapy-label">Current Therapy:</span>
            <span class="therapy-name">Acupuncture</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics Section
        st.markdown("### Latest Metrics — Oct 10, 2025")
        
        # Create three columns for metrics
        metric_cols = st.columns(3)
        
        for i, (metric_name, data) in enumerate(metrics_data.items()):
            with metric_cols[i]:
                trend_class = "up" if data['trend'] == 'up' else "down"
                change_class = "positive" if data['change'] > 0 else "negative"
                change_symbol = "+" if data['change'] > 0 else "−"
                
                st.markdown(f"""
                <div class="metric-card {metric_name}">
                    <div class="metric-emoji">{data['emoji']}</div>
                    <div class="trend-badge {trend_class}">
                        {'📈' if trend_class == 'up' else '📉'} {abs(data['change_percent'])}%
                    </div>
                    <div class="metric-label">{metric_name.title()}</div>
                    <div class="metric-value">
                        {data['current']}<span class="metric-unit">{data['unit']}</span>
                    </div>
                    <div class="metric-change {change_class}">
                        {change_symbol}{abs(data['change']):.1f}{data['unit']}
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill {metric_name}" style="width: {(data['current']/10)*100}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Trend Chart
        st.markdown("""
        <div class="chart-container">
            <h2 class="chart-title">14-Day Trend — Pain, Sleep & Mood</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Create the trend chart
        fig = go.Figure()
        
        # Add lines for each metric
        fig.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['pain'],
            mode='lines',
            name='Pain',
            line=dict(color='#ef4444', width=3),
            hovertemplate='<b>%{x}</b><br>Pain: %{y:.1f}/10<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['sleep'],
            mode='lines',
            name='Sleep (hours)',
            line=dict(color='#3b82f6', width=3),
            hovertemplate='<b>%{x}</b><br>Sleep: %{y:.1f}h<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_df['date'],
            y=trend_df['mood'],
            mode='lines',
            name='Mood',
            line=dict(color='#10b981', width=3),
            hovertemplate='<b>%{x}</b><br>Mood: %{y:.1f}/10<extra></extra>'
        ))
        
        # Add therapy start reference line
        fig.add_shape(
            type="line",
            x0='Oct 02', x1='Oct 02',
            y0=0, y1=1,
            yref="paper",
            line=dict(
                color="#f59e0b",
                width=2,
                dash="dash"
            )
        )
        
        # Add annotation for therapy start
        fig.add_annotation(
            x='Oct 02',
            y=0.95,
            yref="paper",
            text="Therapy Started →",
            showarrow=False,
            font=dict(
                size=12,
                color="#d97706",
                family="Inter"
            ),
            xanchor="left"
        )
        
        # Update layout
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_family='Inter',
            font_size=12,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified',
            xaxis=dict(
                gridcolor='#e2e8f0',
                gridwidth=1,
                showgrid=True,
                color='#94a3b8'
            ),
            yaxis=dict(
                gridcolor='#e2e8f0',
                gridwidth=1,
                showgrid=True,
                color='#94a3b8'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Chart note
        st.markdown("""
        <div style="background: #dbeafe; border: 1px solid #93c5fd; border-radius: 8px; padding: 16px; margin-top: 24px;">
            <p style="font-size: 12px; color: #1e40af; margin: 0;">
                <strong>📌 Therapy Started:</strong> Acupuncture began on Oct 2. Notice the clear improvement trajectory after treatment began.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Daily Log Tab
with tab_analysis:
    st.markdown("## 🌱 Daily Wellness Log")
    
    # Welcome message for first-time users (demo mode only)
    if st.session_state.get("is_first_time_user", False) and demo_mode:
        st.success("👋 **Welcome to Pain Relief Map!** Explore the tabs:\n- **🌱 Daily Log** (this tab) - Start tracking your symptoms\n- **🏠 Dashboard** - View your trends and analysis\n- **🔬 Evidence Explorer** - Browse clinical trials")

    # First-time user onboarding (demo mode only)
    if st.session_state.get("is_first_time_user", False) and demo_mode:
        st.success("🎯 **Your First Entry** (takes 30 seconds)")
        st.markdown("""
        **Start simple!** Just track these essentials:
        1. **Rate your pain today** (0-10)
        2. **How many hours did you sleep?**
        3. **How's your mood?** (0-10)
        4. **Any therapy you tried?**
        
        💡 **Don't worry about getting everything perfect - just start!**
        """)
        st.markdown("---")
    
    st.markdown("""
    Record how you feel each day — pain, sleep, stress, movement, digestion, and therapy use — to discover what helps you most.
    """)
    st.caption("N-of-1 Tracking: this approach treats each person as their own control, tracking changes in symptoms **before vs after** starting a therapy.")
    st.write("")

    # Initialize dataframe
    DEFAULT_COLS = [
        "date", "sex_at_birth", "condition_today", "therapy_used",
        "pain_score", "sleep_hours", "stress_score", "mood_score",
        "movement", "digestive_sounds", "bowel_movements_n", "stool_consistency",
        "physical_symptoms", "emotional_symptoms",
        "patience_score", "anxiety_score", "cravings",
        "menstruating_today", "cycle_day", "flow", "pms_symptoms",
        "good_day", "therapy_on", "therapy_name", "wake_ups_n",
    ]

    # Load data from database or initialize empty dataframe
    if "n1_df" not in st.session_state:
        if AUTH_ENABLED and not demo_mode:
            # Load from database
            user = st.session_state.get("user")
            if user and hasattr(user, 'id'):
                user_df = db_manager.get_user_logs(user.id)
                if not user_df.empty:
                    st.session_state.n1_df = user_df
                else:
                    st.session_state.n1_df = pd.DataFrame(columns=DEFAULT_COLS)
            else:
                st.session_state.n1_df = pd.DataFrame(columns=DEFAULT_COLS)
        else:
            # Demo mode or no auth
            st.session_state.n1_df = pd.DataFrame(columns=DEFAULT_COLS)

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

    def _append_row(row: dict):
        rec = {
            "date": pd.to_datetime(row["date"]),
            "sex_at_birth": row.get("sex_at_birth"),
            "condition_today": ", ".join(row.get("condition_today", [])),
            "therapy_used": ", ".join(row.get("therapy_used", [])),
            "pain_score": float(row["pain_score"]),
            "sleep_hours": float(row["sleep_hours"]),
            "stress_score": float(row["stress_score"]),
            "mood_score": float(row["mood_score"]),
            "movement": ", ".join(row.get("movement", [])),
            "digestive_sounds": row.get("digestive_sounds"),
            "bowel_movements_n": int(row.get("bowel_movements_n", 0)),
            "stool_consistency": row.get("stool_consistency"),
            "physical_symptoms": ", ".join(row.get("physical_symptoms", [])),
            "emotional_symptoms": ", ".join(row.get("emotional_symptoms", [])),
            "patience_score": float(row.get("patience_score", 5)),
            "anxiety_score": float(row.get("anxiety_score", 5)),
            "cravings": ", ".join(row.get("cravings", [])),
            "menstruating_today": (row.get("menstruating_today") in ["Yes", True]),
            "cycle_day": int(row.get("cycle_day") or 0),
            "flow": row.get("flow"),
            "pms_symptoms": ", ".join(row.get("pms_symptoms", [])),
            "good_day": bool(row.get("good_day", False)),
            "therapy_on": int(row.get("therapy_on", 0)),
            "therapy_name": row.get("therapy_name", ""),
        }
        st.session_state.n1_df = pd.concat(
            [st.session_state.n1_df, pd.DataFrame([rec])],
            ignore_index=True
        )
        
        # Save to database if authenticated
        if AUTH_ENABLED and not demo_mode:
            user = st.session_state.get("user")
            if user and hasattr(user, 'id'):
                db_manager.save_log(user.id, rec)

    # Get defaults from yesterday
    defs = _defaults_from_yesterday()

    # Options for multiselects
    condition_options = cond_options + ["None"]
    therapy_options = [
        "Acupuncture", "Aromatherapy", "Ayurveda", "Cognitive Behavioural Therapy", 
        "Exercise Therapy", "Herbal", "Massage", "Meditation", "Qi Gong", "Tai Chi", "Yoga"
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
    flow_options = ["None", "Light", "Medium", "Heavy"]

    # ===== Action Bar (duplicate, note, good day, menstrual cycle toggle) =====
    st.session_state.setdefault("good_day", False)
    st.session_state.setdefault("track_cycle", True)
    st.session_state.setdefault("quick_notes", [])

    with st.container(border=True):
        col_dup, col_note, col_good, col_spacer, col_cycle = st.columns(
            [2.2, 2.2, 2.2, 6.0, 2.6],
            gap="small"
        )

        # 🌿 Duplicate yesterday
        with col_dup:
            if st.button("🌿 Duplicate yesterday", key="dup_yesterday_bar2",
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
                        # Ensure therapy tracking data is copied
                        if "therapy_on" not in dup:
                            dup["therapy_on"] = 0
                        if "therapy_name" not in dup:
                            dup["therapy_name"] = ""
                        _append_row(dup)
                        st.success("Duplicated yesterday's values to today!")

        # 📝 Quick note
        with col_note:
            if hasattr(st, "popover"):
                with st.popover("📝 Quick note", use_container_width=True):
                    note = st.text_area("Note for today", key="quick_note_text2")
                    cna, cnb = st.columns(2)
                    if cna.button("Save", key="quick_note_save2"):
                        if note.strip():
                            st.session_state.quick_notes.append(
                                {"date": dt.date.today().isoformat(), "note": note.strip()}
                            )
                            st.success("Note saved.")
                    if cnb.button("Clear", key="quick_note_clear2"):
                        st.session_state["quick_note_text2"] = ""
            else:
                with st.expander("📝 Quick note", expanded=False):
                    note = st.text_area("Note for today", key="quick_note_text2")
                    cna, cnb = st.columns(2)
                    if cna.button("Save", key="quick_note_save2"):
                        if note.strip():
                            st.session_state.quick_notes.append(
                                {"date": dt.date.today().isoformat(), "note": note.strip()}
                            )
                            st.success("Note saved.")
                    if cnb.button("Clear", key="quick_note_clear2"):
                        st.session_state["quick_note_text2"] = ""

        # ☺️ Mark good day toggle
        with col_good:
            st.session_state["good_day"] = st.toggle(
                "☺️ Mark good day", 
                value=st.session_state["good_day"], 
                key="good_day_toggle2",
                help="Tag days when you feel especially well - helps identify what's working"
            )

        # 🔴 Track menstrual cycle (right-aligned)
        with col_cycle:
            st.session_state["track_cycle"] = st.toggle(
                "Track menstrual cycle",
                value=st.session_state["track_cycle"],
                key="track_cycle_toggle2",
                help="Include cycle info in your daily entries."
            )

    # Set sex_at_birth based on menstrual cycle toggle
    st.session_state.setdefault("sex_at_birth", "Female")
    is_female = st.session_state["track_cycle"]
    st.session_state["sex_at_birth"] = "Female" if is_female else "Male"

    # Function to auto-calculate cycle day based on menstrual days
    def calculate_cycle_day(date, df):
        """Calculate cycle day based on menstrual days pattern"""
        if df.empty:
            return 1
        
        # Convert dates to datetime
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        current_date = pd.to_datetime(date)
        
        # Find all menstrual days (where menstruating_today is True/Yes)
        menstrual_days = df_copy[
            (df_copy["menstruating_today"].isin([True, "Yes", "yes"])) & 
            (df_copy["date"] <= current_date)
        ].sort_values("date")
        
        if menstrual_days.empty:
            return 1
        
        # Find the most recent menstrual start
        last_period_start = menstrual_days.iloc[-1]["date"]
        
        # Calculate days since last period started
        days_since_period = (current_date - last_period_start).days + 1
        
        # If currently menstruating, it's day 1 of cycle
        if df_copy[df_copy["date"] == current_date]["menstruating_today"].isin([True, "Yes", "yes"]).any():
            return 1
        
        # Calculate cycle day (assume 28-day cycle if no pattern established)
        cycle_day = days_since_period
        if cycle_day > 35:  # If more than 35 days, reset to 1
            return 1
        return min(cycle_day, 35)

    with st.form("n1_entry_form", clear_on_submit=False):
        # Row 1: Date and Mood
        c1a, c1b = st.columns(2)
        with c1a:
            f_date = st.date_input("Today's date:", value=dt.date.today(), format="DD/MM/YYYY")
        with c1b:
            f_mood = st.slider("Overall mood (0–10)", 0, 10, int(round(defs["mood_score"])), help="How's your overall mood today?")

        # Row 2: Sleep hours and Times woke up
        c2a, c2b = st.columns(2)
        with c2a:
            f_sleep = st.slider("Sleep hours last night", 0, 14, int(round(defs["sleep_hours"])))
        with c2b:
            f_wake_ups = st.number_input("Times woke up", 0, 20, 0, help="How many times did you wake up during the night?")

        # Row 3: Stress and Pain
        c3a, c3b = st.columns(2)
        with c3a:
            f_stress = st.slider("Stress (0–10)", 0, 10, int(round(defs["stress_score"])))
        with c3b:
            f_pain = st.slider("Pain (0–10)", 0, 10, int(round(defs["pain_score"])))

        # Therapies Section
        st.markdown("#### 🌟 Therapy Tracking")
        st.caption("💡 **Tip:** You can track multiple therapies simultaneously in 'Therapy used today' below. Use the checkbox only when starting a NEW therapy for before/after analysis.")
        
        # Conditions and Therapies
        c3, c4 = st.columns(2)
        with c3:
            f_condition_today = st.multiselect(
                "Conditions felt today",
                options=condition_options,
                default=[],
                help="Select all conditions experienced today.",
                placeholder="Choose an option"
            )
            # Auto-deselect "None" if other options are selected
            if len(f_condition_today) > 1 and "None" in f_condition_today:
                f_condition_today = [c for c in f_condition_today if c != "None"]
        with c4:
            f_therapy_used = st.multiselect(
                "Therapy used today",
                options=therapy_options,
                help="Select all therapies you used today."
            )
        
        # Started new therapy tracking
        f_started_therapy = st.checkbox(
            "Started a new primary therapy today",
            help="Check this box on the first day you begin a new PRIMARY therapy for before/after analysis."
        )
        if f_started_therapy:
            f_therapy_name = st.text_input(
                "Which therapy?",
                placeholder="e.g., Acupuncture or Acupuncture + Yoga",
                help="Name the primary therapy you're analyzing (can include multiple: 'Acupuncture + Yoga')"
            )
        else:
            f_therapy_name = ""

        # ---- Conditional Menstrual Tracking (only if Female) ----
        if is_female:
            st.markdown("### 🩸 Hormonal Cycle")
            st.caption("💡 **Tip:** Just mark your menstrual days - cycle day will be calculated automatically!")
            hc1, hc2 = st.columns(2)
            with hc1:
                f_menstruating = st.radio("Menstruating today?", ["No", "Yes"], index=0)
            with hc2:
                f_pms = st.multiselect(
                    "PMS symptoms",
                    ["None", "Cramps", "Bloating", "Breast tenderness", "Headache", "Irritability", "Low mood", "Anxiety", "Fatigue", "Food cravings"],
                    default=["None"]
                )
                # Auto-deselect "None" if other options are selected
                if len(f_pms) > 1 and "None" in f_pms:
                    f_pms = [p for p in f_pms if p != "None"]
            
            # Only show flow field if menstruating today is "Yes"
            if f_menstruating == "Yes":
                hc3 = st.columns(1)[0]
                with hc3:
                    f_flow = st.selectbox("Flow", ["None", "Light", "Medium", "Heavy"], index=0)
            else:
                f_flow = "None"  # Clear flow data when not menstruating
        else:
            f_menstruating = "No"
            f_flow = "None"
            f_pms = ["None"]

        # ---- Core Symptoms ----
        st.markdown("### ❤️ Core Symptoms")
        c5, c6 = st.columns(2)
        with c5:
            f_anxiety = st.slider("Anxiety (0–10)", 0, 10, 5)
        with c6:
            f_patience = st.slider("Patience (0–10)", 0, 10, 5)

        # Emotional & Physical Symptoms
        st.markdown("### 💭 Emotional and Physical Symptoms")
        c7, c8 = st.columns(2)
        with c7:
            f_emotional = st.multiselect("Emotional symptoms:", emotional_options)
            # Auto-deselect "None" if other options are selected
            if len(f_emotional) > 1 and "None" in f_emotional:
                f_emotional = [e for e in f_emotional if e != "None"]
        with c8:
            f_physical = st.multiselect("Physical symptoms:", physical_options)
            # Auto-deselect "None" if other options are selected
            if len(f_physical) > 1 and "None" in f_physical:
                f_physical = [p for p in f_physical if p != "None"]

        f_cravings = st.multiselect(
            "Cravings today:",
            craving_options,
            default=[],
            placeholder="Choose an option"
        )
        # Auto-deselect "None" if other options are selected
        if len(f_cravings) > 1 and "None" in f_cravings:
            f_cravings = [c for c in f_cravings if c != "None"]

        # Physical State
        st.markdown("### 🏃‍♀️ Physical State")
        c9, c10 = st.columns(2)
        with c9:
            f_movement = st.multiselect("Movement today:", movement_options)
            # Auto-deselect "None / Rest day" if other options are selected
            if len(f_movement) > 1 and "None / Rest day" in f_movement:
                f_movement = [m for m in f_movement if m != "None / Rest day"]
        with c10:
            f_bowel = st.slider("Bowel movements (0–10)", 0, 10, 1)

        c11, c12 = st.columns(2)
        with c11:
            f_digestive = st.selectbox("Digestive sounds:", digestive_options, index=0)
        with c12:
            f_stool = st.selectbox("Stool consistency:", stool_options, index=0)

        # Submit
        add_clicked = st.form_submit_button("💾 Submit Today's Entry", type="primary")
        if add_clicked:
            # Therapy tracking logic: inherit from last row unless starting new therapy
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
            
            # Auto-calculate cycle day based on menstrual days
            auto_cycle_day = calculate_cycle_day(f_date, st.session_state.n1_df) if is_female else 0
            
            row_data = {
                "date": f_date,
                "sex_at_birth": st.session_state.get("sex_at_birth", "Female"),
                "condition_today": f_condition_today,
                "therapy_used": f_therapy_used,
                "pain_score": f_pain,
                "sleep_hours": f_sleep,
                "stress_score": f_stress,
                "mood_score": f_mood,
                "wake_ups_n": f_wake_ups,
                "movement": f_movement,
                "digestive_sounds": f_digestive,
                "bowel_movements_n": f_bowel,
                "stool_consistency": f_stool,
                "physical_symptoms": f_physical,
                "emotional_symptoms": f_emotional,
                "patience_score": f_patience,
                "anxiety_score": f_anxiety,
                "cravings": f_cravings,
                "menstruating_today": f_menstruating,
                "cycle_day": auto_cycle_day,
                "flow": f_flow,
                "pms_symptoms": f_pms,
                "good_day": st.session_state.get("good_day", False),
                "therapy_on": therapy_on_val,
                "therapy_name": therapy_name_val,
            }
            
            _append_row(row_data)
            st.success("✅ Entry saved! Check the Dashboard tab to see your trends.")
            st.balloons()

    # Show recent entries
    if not st.session_state.n1_df.empty:
        st.markdown("### 📊 Recent Entries")
        recent_df = st.session_state.n1_df.tail(5)[["date", "pain_score", "sleep_hours", "mood_score", "therapy_used"]]
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.info("No entries yet — add your first day above!")

# Calendar Tab
with tab_calendar:
    st.markdown("## 📅 Calendar")
    st.caption("Track your wellness journey with a clean, intuitive calendar view")
    
    # Check if user is female (for menstrual calendar display)
    is_female = st.session_state.get("sex_at_birth", "Female") == "Female"
    
    if (has_data or show_demo) and is_female:
        # Add CSS for Outlook-style calendar
        st.markdown("""
        <style>
        .outlook-calendar {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            background-color: white;
        }
        .month-header {
            font-size: 18px;
            font-weight: 600;
            color: #323130;
            margin: 16px 0 8px 0;
            text-align: center;
        }
        .calendar-table {
            width: 100%;
            border-collapse: collapse;
            margin: 0;
        }
        .calendar-table th {
            background-color: #f3f2f1;
            color: #605e5c;
            font-weight: 600;
            font-size: 12px;
            padding: 8px 4px;
            text-align: center;
            border: 1px solid #d1d5db;
            height: 32px;
        }
        .calendar-table td {
            border: 1px solid #d1d5db;
            padding: 0;
            height: 32px;
            width: 14.28%;
            text-align: center;
            vertical-align: middle;
            background-color: white;
        }
        .calendar-day {
            display: block;
            width: 100%;
            height: 100%;
            line-height: 30px;
            font-size: 14px;
            color: #323130;
            text-decoration: none;
            cursor: pointer;
            border: none;
            background: none;
            font-family: inherit;
        }
        .calendar-day:hover {
            background-color: #f3f2f1;
        }
        .calendar-day.today {
            background-color: #0078d4;
            color: white;
            font-weight: 600;
        }
        .calendar-day.today:hover {
            background-color: #106ebe;
        }
        .calendar-day.other-month {
            color: #a19f9d;
        }
        .calendar-day.selected {
            background-color: #deecf9;
            color: #0078d4;
            font-weight: 600;
        }
        .calendar-day.menstrual {
            background-color: #fce4ec;
            color: #c2185b;
            font-weight: 600;
        }
        .calendar-day.ovulation {
            background-color: #fff3e0;
            color: #f57c00;
            font-weight: 600;
        }
        .calendar-day.pms {
            background-color: #fffde7;
            color: #f9a825;
            font-weight: 600;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get current date for navigation
        current_date = dt.date.today()
        if 'calendar_view_month' not in st.session_state:
            st.session_state.calendar_view_month = current_date.month
        if 'calendar_view_year' not in st.session_state:
            st.session_state.calendar_view_year = current_date.year
        
        # Calendar navigation
        col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
        
        with col_nav1:
            if st.button("◀️", key="cal_view_prev"):
                if st.session_state.calendar_view_month == 1:
                    st.session_state.calendar_view_month = 12
                    st.session_state.calendar_view_year -= 1
                else:
                    st.session_state.calendar_view_month -= 1
                st.rerun()
        
        with col_nav2:
            month_names = ["", "January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
            st.markdown(f"<div class='month-header'>{month_names[st.session_state.calendar_view_month].upper()} {st.session_state.calendar_view_year}</div>", unsafe_allow_html=True)
        
        with col_nav3:
            if st.button("▶️", key="cal_view_next"):
                if st.session_state.calendar_view_month == 12:
                    st.session_state.calendar_view_month = 1
                    st.session_state.calendar_view_year += 1
                else:
                    st.session_state.calendar_view_month += 1
                st.rerun()
        
        # Create calendar data
        import calendar
        
        # Get calendar for the selected month/year
        cal = calendar.monthcalendar(st.session_state.calendar_view_year, st.session_state.calendar_view_month)
        
        # Get data for the month
        month_start = dt.date(st.session_state.calendar_view_year, st.session_state.calendar_view_month, 1)
        if st.session_state.calendar_view_month == 12:
            month_end = dt.date(st.session_state.calendar_view_year + 1, 1, 1) - dt.timedelta(days=1)
        else:
            month_end = dt.date(st.session_state.calendar_view_year, st.session_state.calendar_view_month + 1, 1) - dt.timedelta(days=1)
        
        # Filter data for this month
        if has_data:
            df_cal = display_df.copy()
            df_cal["date"] = pd.to_datetime(df_cal["date"])
            month_data = df_cal[
                (df_cal["date"].dt.date >= month_start) & 
                (df_cal["date"].dt.date <= month_end)
            ]
        else:
            month_data = pd.DataFrame()
        
        # Create Outlook-style calendar using HTML table
        st.markdown('<div class="outlook-calendar">', unsafe_allow_html=True)
        
        # Create HTML table for calendar
        calendar_html = f'''
        <table class="calendar-table">
            <thead>
                <tr>
                    <th>Mon</th>
                    <th>Tue</th>
                    <th>Wed</th>
                    <th>Thu</th>
                    <th>Fri</th>
                    <th>Sat</th>
                    <th>Sun</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        # Add calendar weeks
        for week in cal:
            calendar_html += '<tr>'
            for i, day in enumerate(week):
                if day == 0:
                    calendar_html += '<td></td>'
                else:
                    day_date = dt.date(st.session_state.calendar_view_year, st.session_state.calendar_view_month, day)
                    
                    # Check if we have data for this day
                    day_data = None
                    if not month_data.empty:
                        day_data = month_data[month_data["date"].dt.date == day_date]
                    
                    # Determine day styling
                    day_class = ""
                    if day_date == current_date:
                        day_class = "today"
                    elif day_data is not None and not day_data.empty:
                        day_row = day_data.iloc[0]
                        is_menstruating = day_row.get("menstruating_today") in [True, "Yes", "yes"]
                        has_pms = day_row.get("pms_symptoms") and day_row.get("pms_symptoms") != ["None"]
                        cycle_day = day_row.get("cycle_day", 0)
                        is_ovulation_day = (cycle_day >= 12 and cycle_day <= 16)
                        
                        if is_menstruating:
                            day_class = "menstrual"
                        elif is_ovulation_day:
                            day_class = "ovulation"
                        elif has_pms:
                            day_class = "pms"
                    
                    # Check if day is selected/tracked
                    period_key = f"track_period_{day_date.isoformat()}"
                    if period_key in st.session_state and st.session_state[period_key]:
                        day_class = "selected"
                    
                    calendar_html += f'<td><button class="calendar-day {day_class}" onclick="alert(\'{day_date}\')">{day}</button></td>'
            calendar_html += '</tr>'
        
        calendar_html += '''
            </tbody>
        </table>
        '''
        
        st.markdown(calendar_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Legend
        st.markdown("### Legend")
        legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)
        
        with legend_col1:
            st.markdown("🩸 **Menstruating**")
        with legend_col2:
            st.markdown("🥚 **Ovulation**")
        with legend_col3:
            st.markdown("🟡 **PMS**")
        with legend_col4:
            st.markdown("⚫ **Selected**")
        
        st.caption("💡 Click on any day to track or untrack as a period day")
        
    else:
        st.info("📅 Calendar view is available for female users. Enable demo mode or log in to see your calendar.")

# Evidence Explorer Tab
with tab_evidence:
    # =========================================================================
    # FILTERS AT TOP OF TAB
    # =========================================================================
    st.markdown("## 🔬 Evidence Explorer")
    st.markdown("Find therapies backed by clinical research for your condition")
    
    with st.expander("🔍 **Search Filters** (Select your condition to get started)", expanded=True):
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            # Comprehensive therapy list
            therapy_opts = [
                "Acupuncture", "Aromatherapy", "Ayurveda", "Cognitive Behavioural Therapy", 
                "Exercise Therapy", "Herbal", "Massage", "Meditation", "Qi Gong", "Tai Chi", "Yoga"
            ]
            # Set default to Anxiety if available, otherwise first option
            default_conds = [default_condition] if default_condition in cond_options else (cond_options[:1] if cond_options else [])
            
            tab_conditions = st.multiselect(
                "🏥 Your Condition(s)",
                options=cond_options,
                default=default_conds,
                help="Select one or more conditions to see relevant therapies"
            )
            
            tab_therapies = st.multiselect(
                "💊 Therapies to Compare",
                options=therapy_opts,
                default=therapy_opts,
                help="Choose specific therapies to compare, or leave all selected"
            )
        
        with filter_col2:
            tab_yr = st.slider(
                "📅 Study Years",
                min_value=year_lo,
                max_value=year_hi,
                value=(default_lo, current_year),
                help="Filter studies by publication year range"
            )
            
            tab_sel_evdir = st.multiselect(
                "📊 Evidence Direction",
                options=evdir_opts,
                default=default_evdir,
                help="Filter by type of evidence"
            )
    
    # =========================================================================
    # THERAPY DEFINITIONS SECTION
    # =========================================================================
    with st.expander("📚 **Therapy Definitions** - What each therapy means", expanded=False):
        st.markdown("""
        Learn about the different complementary and alternative therapies available:
        """)
        
        # Therapy definitions dictionary
        therapy_definitions = {
            "Acupuncture": "A traditional Chinese medicine practice involving the insertion of thin needles at specific points on the body to stimulate energy flow and promote healing. Used for pain management, stress reduction, and various health conditions.",
            
            "Aromatherapy": "The therapeutic use of essential oils extracted from plants to promote physical and psychological well-being. Oils can be inhaled, applied topically, or used in baths to reduce stress, improve sleep, and manage pain.",
            
            "Ayurveda": "An ancient Indian holistic healing system that emphasizes balance between mind, body, and spirit through diet, herbal remedies, yoga, meditation, and lifestyle practices tailored to individual constitution types (doshas).",
            
            "Cognitive Behavioural Therapy": "A structured, evidence-based psychotherapy that helps identify and change negative thought patterns and behaviors. Particularly effective for anxiety, depression, PTSD, and chronic pain management.",
            
            "Exercise Therapy": "Structured physical activity programs designed to improve strength, flexibility, endurance, and overall health. Includes aerobic exercise, resistance training, stretching, and functional movement tailored to individual needs.",
            
            "Herbal": "The use of plants and plant extracts for medicinal purposes. Includes teas, tinctures, capsules, and topical preparations. Common herbs include St. John's Wort for depression, ginger for nausea, and turmeric for inflammation.",
            
            "Massage": "Manual manipulation of soft tissues (muscles, tendons, ligaments) to reduce tension, improve circulation, and promote relaxation. Varieties include Swedish, deep tissue, sports, and therapeutic massage.",
            
            "Meditation": "Mental training practices that cultivate awareness, focus, and inner calm. Includes mindfulness meditation, transcendental meditation, loving-kindness meditation, and body scan techniques for stress reduction and mental clarity.",
            
            "Qi Gong": "A Chinese mind-body practice combining gentle movements, breathing techniques, and meditation to cultivate and balance 'qi' (life energy). Used to improve flexibility, reduce stress, and enhance overall vitality.",
            
            "Tai Chi": "An ancient Chinese martial art practiced as a gentle form of exercise involving slow, flowing movements coordinated with deep breathing. Benefits include improved balance, flexibility, strength, and mental calmness.",
            
            "Yoga": "An Indian practice integrating physical postures (asanas), breathing exercises (pranayama), and meditation. Styles range from gentle (Hatha, Yin) to vigorous (Vinyasa, Ashtanga), promoting flexibility, strength, and mental well-being."
        }
        
        # Display definitions in a clean format
        for therapy, definition in therapy_definitions.items():
            st.markdown(f"**{therapy}:**")
            st.markdown(f"> {definition}")
            st.markdown("")  # Add spacing
    
    # Apply filters specific to this tab
    base = evidence.copy()
    
    if "condition" in base.columns and tab_conditions:
        base = base[base["condition"].isin(tab_conditions)]
    if tab_therapies and "therapy" in base.columns:
        base = base[base["therapy"].isin(tab_therapies)]
    
    if "year_min" in base.columns: base["year_min"] = _def_num(base["year_min"])
    if "year_max" in base.columns: base["year_max"] = _def_num(base["year_max"])
    if "year_min" in base.columns or "year_max" in base.columns:
        ymin = base["year_min"].fillna(base["year_max"]).fillna(year_lo)
        ymax = base["year_max"].fillna(base["year_min"]).fillna(year_hi)
        base = base[(ymax >= tab_yr[0]) & (ymin <= tab_yr[1])]
    
    if tab_sel_evdir and "evidence_direction" in base.columns:
        base = base[base["evidence_direction"].isin(tab_sel_evdir)]
    
    plot_df = base.copy()

    # Show helpful message if no condition selected
    if not tab_conditions:
        st.info(
            "👆 **Please select at least one condition** from the filters above to see therapy recommendations.",
            icon="💡"
        )
        # Show a preview of what they can explore
        st.markdown("### 🔬 What you can discover:")
        st.markdown("""
        - **Clinical trials** for your specific condition
        - **Evidence-based therapies** with positive research backing
        - **PubMed articles** supporting each therapy
        - **Direct links** to research sources
        
        **Get started:** Select your condition(s) in the filters above! 👆
        """)
        st.stop()
    
    # If nothing matches filters, show friendly hint
    if plot_df.empty:
        st.warning(
            "No therapies found matching your filters. Try selecting a different condition or broadening your criteria.",
            icon="🔍"
        )
        st.stop()

    # =========================================================================
    # SUMMARY BAR CHART - Visual Overview
    # =========================================================================
    st.markdown("### 📊 Summary: Top Therapies at a Glance")
    
    # Prepare data for bar chart
    chart_df = plot_df.copy()
    chart_df["trials_num"] = pd.to_numeric(chart_df.get("clinicaltrials_n", 0), errors="coerce").fillna(0)
    chart_df["pubmed_num"] = pd.to_numeric(chart_df.get("pubmed_n", 0), errors="coerce").fillna(0)
    chart_df["evidence_score"] = (chart_df["trials_num"] * 10) + chart_df["pubmed_num"]
    
    # Sort and take top 10 for readability
    chart_df_top = chart_df.nlargest(10, "evidence_score")
    
    # Decide what to color by: condition if multiple selected, otherwise evidence direction
    if len(tab_conditions) > 1 and "condition" in chart_df_top.columns:
        color_by = "condition"
        color_map = None  # Let plotly auto-assign colors
        chart_title = f"Top 10 Therapies by Clinical Trial Count (All Conditions)"
    elif "evidence_direction" in chart_df_top.columns:
        color_by = "evidence_direction"
        color_map = {
            "Positive": "#2ecc71",
            "Negative": "#e74c3c",
            "Mixed": "#f1c40f",
            "Unclear": "#95a5a6",
        }
        chart_title = f"Top 10 Therapies by Clinical Trial Count ({', '.join(tab_conditions)})"
    else:
        color_by = None
        color_map = None
        chart_title = f"Top 10 Therapies by Clinical Trial Count"
    
    fig_summary = px.bar(
        chart_df_top.sort_values("evidence_score", ascending=True),  # Ascending for horizontal bar
        y="therapy",
        x="trials_num",
        color=color_by,
        color_discrete_map=color_map if color_map else None,
        orientation='h',
        title=chart_title,
        labels={"trials_num": "Number of Clinical Trials", "therapy": "Therapy", "condition": "Condition"},
        height=400
    )
    fig_summary.update_layout(
        showlegend=True if color_by else False,
        yaxis={'categoryorder':'total ascending'},
        barmode='stack'  # Stack bars when coloring by condition
    )
    st.plotly_chart(fig_summary, use_container_width=True)
    
    st.markdown("---")

    # =========================================================================
    # MAIN HEADER - What works for your condition
    # =========================================================================
    st.markdown("### 💊 Top Therapies for Your Condition(s)")
    
    # Calculate evidence score for sorting (trials worth more)
    plot_df_sorted = plot_df.copy()
    plot_df_sorted["trials_num"] = pd.to_numeric(plot_df_sorted.get("clinicaltrials_n", 0), errors="coerce").fillna(0)
    plot_df_sorted["pubmed_num"] = pd.to_numeric(plot_df_sorted.get("pubmed_n", 0), errors="coerce").fillna(0)
    plot_df_sorted["evidence_score"] = (plot_df_sorted["trials_num"] * 10) + plot_df_sorted["pubmed_num"]  # Weight trials 10x
    
    # Sort by evidence score (high to low)
    plot_df_sorted = plot_df_sorted.sort_values("evidence_score", ascending=False)
    
    # Show count summary
    total_therapies = len(plot_df_sorted)
    positive_count = len(plot_df_sorted[plot_df_sorted.get("evidence_direction") == "Positive"]) if "evidence_direction" in plot_df_sorted.columns else 0
    
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
        📊 Found <strong>{total_therapies} therapies</strong> for your condition(s)
        {f" • <strong style='color: #2ecc71;'>{positive_count} with positive evidence</strong>" if positive_count > 0 else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # SIMPLE THERAPY TABLE - Ordered by Evidence Strength
    # =========================================================================
    
    for idx, (_, row) in enumerate(plot_df_sorted.iterrows()):
        therapy_name = row.get("therapy", "Unknown")
        condition_name = row.get("condition", "")
        category = row.get("therapy_group", "Unknown")
        evidence_dir = row.get("evidence_direction", "Unclear")
        trials_n = int(row.get("trials_num", 0))
        pubmed_n = int(row.get("pubmed_num", 0))
        trials_url = row.get("trials_url", "")
        articles_url = row.get("articles_url", "")
        
        # Evidence badge styling
        if evidence_dir == "Positive":
            badge_html = '<span style="background: #2ecc71; color: white; padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600; margin-left: 0.5rem;">✓ Positive Evidence</span>'
        elif evidence_dir == "Negative":
            badge_html = '<span style="background: #e74c3c; color: white; padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600; margin-left: 0.5rem;">✗ Negative</span>'
        elif evidence_dir == "Mixed":
            badge_html = '<span style="background: #f1c40f; color: white; padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600; margin-left: 0.5rem;">~ Mixed</span>'
        else:
            badge_html = '<span style="background: #95a5a6; color: white; padding: 0.25rem 0.6rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600; margin-left: 0.5rem;">? Unclear</span>'
        
        # Rank number (1st, 2nd, 3rd...)
        rank = idx + 1
        rank_color = "#2ecc71" if rank <= 3 else "#3498db" if rank <= 10 else "#7f8c8d"
        
        # Create therapy card with inline links
        st.markdown(f"""
        <div style="background: white; border: 2px solid #e0e0e0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; 
                    transition: all 0.2s ease; {'border-left: 5px solid #2ecc71;' if evidence_dir == 'Positive' else ''}">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="background: {rank_color}; color: white; width: 36px; height: 36px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1rem;">
                        {rank}
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #2c3e50; font-size: 1.3rem;">{therapy_name}</h3>
                        <p style="margin: 0.25rem 0 0 0; color: #7f8c8d; font-size: 0.9rem;">
                            {badge_html} {category} • {condition_name if condition_name else 'General'}
                        </p>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 2rem; margin-top: 0.75rem; padding-left: 52px;">
                <div>
                    📊 <a href="{trials_url}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: 600;">{trials_n:,} Clinical Trials</a>
                </div>
                <div>
                    📚 <a href="{articles_url}" target="_blank" style="color: #0066cc; text-decoration: none; font-weight: 600;">{pubmed_n:,} PubMed Articles</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # OPTIONAL: Show interpretation guide
    # =========================================================================
    st.markdown("---")
    with st.expander("📖 How to Interpret This Data"):
        st.markdown("""
        **How therapies are ranked:**
        - Ranked by total evidence strength (clinical trials weighted 10x more than articles)
        - Therapies at the top have the most research backing
        
        **Evidence Direction:**
        - 🟢 **✓ Positive Evidence**: Studies show beneficial effects for the condition
        - 🔴 **✗ Negative**: Studies show little to no benefit  
        - 🟡 **~ Mixed**: Studies show conflicting results
        - ⚪ **? Unclear**: Insufficient or inconclusive evidence
        
        **Study Types:**
        - **Clinical Trials**: High-quality, controlled studies from ClinicalTrials.gov
        - **PubMed Articles**: Published research (various study types and quality levels)
        
        **💡 What to do with this information:**
        1. Focus on therapies with positive evidence and high trial counts
        2. Click "View Trials" or "View Articles" to read the research
        3. Discuss promising options with your healthcare provider
        4. Consider starting with top-ranked therapies that fit your lifestyle
        
        **⚠️ Important**: This is for informational purposes only. Always consult your healthcare provider before starting any new therapy.
        """)
    
    # =========================================================================
    # EXPORT OPTION
    # =========================================================================
    st.markdown("---")
    st.markdown("### 💾 Save This List")
    csv_data = plot_df_sorted[["therapy", "therapy_group", "condition", "evidence_direction", 
                                 "clinicaltrials_n", "pubmed_n", "trials_url", "articles_url"]].to_csv(index=False).encode('utf-8')
    condition_name = '-'.join(tab_conditions[:2]) if tab_conditions else 'selected-conditions'
    st.download_button(
        label="📥 Download as CSV to share with your doctor",
        data=csv_data,
        file_name=f"therapies_for_{condition_name}_{dt.date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )

# Settings Tab
with tab_settings:
    st.markdown("## ⚙️ Settings & Data Management")
    
    st.markdown("### 💾 Data Export & Import")
    st.markdown("""
    Your health data belongs to you. Export it to keep a backup, or import previously saved data.
    
    **Privacy:** All data stays on your device unless you choose to export it.
    """)
    
    # Export section
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.markdown("#### 📥 Export Your Data")
        st.info("Export functionality will be available when you have logged data.")
        
    with col_exp2:
        st.markdown("#### 📤 Import Your Data")
        st.info("Import functionality will be available for CSV files.")
    
    st.markdown("### ℹ️ About Pain Relief Map")
    st.markdown("""
    **Version:** 5.0  
    **Purpose:** Help people with health conditions discover which therapies work for them through scientific evidence and personal tracking.
    
    **Features:**
    - 📊 Track daily symptoms (pain, sleep, stress, mood, etc.)
    - 🔬 Explore clinical trials and research evidence
    - 📈 Analyze therapy effects with statistical confidence
    - 💾 Export/import your data (you own it!)
    
    **Data Privacy:**
    - All data stays on your device (local-first)
    - No account required, no data sent to servers
    - You control exports and backups
    
    **Methodology:**
    - N-of-1 trials: You are your own control
    - Pre/post comparison with statistical analysis
    - Modern dashboard with professional design
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px; padding: 24px 0;">
    <p>Pain Relief Map • Track What Works for You</p>
</div>
""", unsafe_allow_html=True)
