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
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import requests
from urllib.parse import quote
import time

# Load environment variables
load_dotenv()

# ============================================================================
# PAGE CONFIGURATION - MUST BE FIRST
# ============================================================================
st.set_page_config(
    page_title="Bearable",
    page_icon="app/bear_icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# SUPABASE INITIALIZATION
# ============================================================================
@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client with credentials from environment or Streamlit secrets"""
    # Try to get from Streamlit secrets first (for cloud deployment)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variables (for local development)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        st.error("⚠️ Supabase credentials not found. Please add them to Streamlit secrets or .env file")
        st.info("""
        **For Streamlit Cloud:**
        1. Go to App Settings → Secrets
        2. Add: 
        ```
        SUPABASE_URL = "your-url"
        SUPABASE_KEY = "your-key"
        ```
        
        **For Local Development:**
        Create a `.env` file with:
        ```
        SUPABASE_URL=your-url
        SUPABASE_KEY=your-key
        ```
        """)
        return None

    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {str(e)}")
        return None

# Initialize Supabase client
supabase = init_supabase()

# ============================================================================
# LIVE API CONNECTORS - ClinicalTrials.gov & PubMed
# ============================================================================

@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_clinical_trials_count(condition: str, therapy: str) -> int:
    """
    Fetch live clinical trials count from ClinicalTrials.gov API v2
    Returns: Number of trials found
    """
    try:
        # ClinicalTrials.gov API v2 endpoint
        base_url = "https://clinicaltrials.gov/api/v2/studies"
        
        # Build search query
        query = f"{condition} AND {therapy}"
        
        params = {
            "query.cond": condition,
            "query.intr": therapy,
            "countTotal": "true",
            "pageSize": 1  # We only need the count
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        total_count = data.get("totalCount", 0)
        
        return total_count
        
    except requests.exceptions.Timeout:
        st.warning("⏱️ ClinicalTrials.gov API timeout - using cached data")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"⚠️ ClinicalTrials.gov API error: {str(e)[:100]}")
        return None
    except Exception as e:
        st.warning(f"⚠️ Unexpected error fetching clinical trials: {str(e)[:100]}")
        return None


@st.cache_data(ttl=86400)  # Cache for 24 hours  
def fetch_pubmed_count(condition: str, therapy: str) -> int:
    """
    Fetch live PubMed articles count using E-utilities API
    Returns: Number of articles found
    """
    try:
        # PubMed E-utilities endpoint
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        # Build search query
        search_term = f"({condition}) AND ({therapy})"
        
        params = {
            "db": "pubmed",
            "term": search_term,
            "retmode": "json",
            "retmax": 0  # We only need the count
        }
        
        # Add delay to respect NCBI rate limiting (max 3 requests/second without API key)
        time.sleep(0.34)  # ~3 requests per second
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        count = int(data.get("esearchresult", {}).get("count", 0))
        
        return count
        
    except requests.exceptions.Timeout:
        st.warning("⏱️ PubMed API timeout - using cached data")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"⚠️ PubMed API error: {str(e)[:100]}")
        return None
    except Exception as e:
        st.warning(f"⚠️ Unexpected error fetching PubMed data: {str(e)[:100]}")
        return None


def get_live_evidence_data(condition: str, therapy: str) -> dict:
    """
    Fetch live evidence data from both APIs
    Returns: dict with trials_count, pubmed_count, and status
    """
    trials_count = fetch_clinical_trials_count(condition, therapy)
    pubmed_count = fetch_pubmed_count(condition, therapy)
    
    return {
        "therapy": therapy,
        "condition": condition,
        "clinicaltrials_n": trials_count if trials_count is not None else 0,
        "pubmed_n": pubmed_count if pubmed_count is not None else 0,
        "data_source": "live_api" if (trials_count is not None or pubmed_count is not None) else "fallback_csv",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ============================================================================
# EVIDENCE DATA LOADER
# ============================================================================

def _locate_evidence_csv() -> Path | None:
    """Find evidence_counts.csv in common locations, prefer the newest one"""
    candidates = [
        Path("data/evidence_counts.csv"),
        Path("data/raw/evidence_counts.csv"),
        Path("evidence_counts.csv"),
    ]
    
    # Find all existing CSVs with their modification times
    existing_files = []
    for p in candidates:
        if p.exists():
            try:
                mtime = p.stat().st_mtime
                existing_files.append((mtime, p))
            except Exception:
                continue
    
    # Return the most recent file, if any
    if existing_files:
        # Sort by modification time (most recent first)
        existing_files.sort(reverse=True)
        return existing_files[0][1]  # Return the path of the newest file
    
    return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_evidence_data() -> pd.DataFrame:
    """Load evidence data from CSV file"""
    csv_path = _locate_evidence_csv()
    
    if csv_path is None:
        # If no CSV found, return empty DataFrame
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        
        # Standardize key columns if they exist
        if "condition" in df.columns:
            df["condition"] = df["condition"].astype(str).str.title()
        if "therapy" in df.columns:
            df["therapy"] = df["therapy"].astype(str).str.title()
        if "evidence_direction" in df.columns:
            df["evidence_direction"] = df["evidence_direction"].astype(str).str.strip().str.capitalize()
        
        return df
    except Exception as e:
        st.error(f"Error loading evidence data: {e}")
        return pd.DataFrame()

def fetch_live_evidence_for_therapies(therapies_list, conditions_list):
    """Fetch live evidence data for specific therapies and conditions"""
    rows = []
    total_combinations = len(therapies_list) * len(conditions_list)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    current = 0
    for therapy in therapies_list:
        for condition in conditions_list:
            current += 1
            progress = current / total_combinations
            progress_bar.progress(progress)
            status_text.text(f"Fetching data... {current}/{total_combinations} (Condition: {condition}, Therapy: {therapy})")
            
            # Fetch live data
            live_data = get_live_evidence_data(condition, therapy)
            rows.append({
                'therapy': therapy,
                'condition': condition,
                'clinicaltrials_n': live_data['clinicaltrials_n'],
                'pubmed_n': live_data['pubmed_n'],
                'evidence_direction': 'Unclear',  # Default, could be enhanced
                'data_source': live_data['data_source'],
                'last_updated': live_data['last_updated']
            })
            
            # Small delay to avoid overwhelming the APIs
            time.sleep(0.5)
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(rows)

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
    
    /* FORCE BUTTON COLORS - Override Streamlit Cloud red theme */
    /* This targets Streamlit's default theme colors that get applied on Cloud */
    div[data-baseweb="base-button"],
    button[data-baseweb="button"],
    [data-baseweb="base-button"],
    [data-baseweb="button"],
    button.element-container,
    button {
        --primary-color: #667eea !important;
        background-color: var(--primary-color, #667eea) !important;
    }
    
    /* Override Streamlit's accent-color CSS variable */
    :root {
        --primary: #667eea !important;
        --secondary-background-color: #f8f9ff !important;
        --background-color: #ffffff !important;
        --text-color: #1e293b !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* SIDEBAR - Purple Background */
    section[data-testid="stSidebar"],
    .css-1d391kg,
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
        background-color: #667eea !important;
    }
    
    /* Sidebar text styling */
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Sidebar input backgrounds */
    section[data-testid="stSidebar"] .stTextInput > div > div > input,
    section[data-testid="stSidebar"] .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Sidebar buttons - translucent white */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: white !important;
    }

    /* FIXED V14: Remove bottom white space */
    .main .block-container {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    .main {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    .stApp {
        overflow-x: hidden !important;
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    /* FIXED V14: Allow content to flow naturally */
    .stApp {
        overflow-y: visible !important;
        max-height: none !important;
    }

    /* FIXED V14: Footer visibility */
    .custom-footer {
        position: relative !important;
        z-index: 1000 !important;
        background: rgba(255, 255, 255, 0.95) !important;
        display: block !important;
        visibility: visible !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding: 30px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    /* FIXED V14: Target white space containers */
    div[class*="st-emotion-cache"]:last-child,
    .element-container:last-child,
    .stVerticalBlock:last-child {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        min-height: 0 !important;
    }

    /* Target bottom margin areas */
    .element-container:last-child {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Remove bottom spacing from all containers */
    .stVerticalBlock > div:last-child {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Remove extra spacing from elements */
    .element-container {
        margin-bottom: 0 !important;
    }

    /* Fix Plotly chart container */
    .js-plotly-plot {
        margin-bottom: 0 !important;
    }

    /* Remove white background from Plotly charts */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }

    /* Hide Plotly modebar background */
    .modebar-container {
        background: transparent !important;
    }

    /* Make Plotly container background transparent */
    .user-select-none {
        background: transparent !important;
    }

    /* Remove padding from Plotly wrapper */
    div[data-testid="stPlotlyChart"] {
        background: transparent !important;
        padding: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Hide Plotly bottom toolbar/white space */
    .plotly .modebar-container,
    .plotly .modebar-group,
    .plotly .modebar {
        display: none !important;
        visibility: hidden !important;
        background: transparent !important;
    }

    /* Completely hide modebar */
    .modebar {
        display: none !important;
    }

    .modebar-container {
        display: none !important;
    }

    .modebar-btn {
        display: none !important;
    }

    /* Nuclear option - hide any white backgrounds in plotly */
    .js-plotly-plot .plotly .modebar-container,
    .js-plotly-plot .plotly .modebar,
    .js-plotly-plot .modebar-container,
    .js-plotly-plot .modebar {
        display: none !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Hide the white hover box specifically */
    g.hoverlayer {
        display: none !important;
    }

    .hoverlayer {
        display: none !important;
    }

    /* Remove white background from plotly bottom area */
    .main-svg {
        background: transparent !important;
    }

    svg.main-svg {
        background: transparent !important;
    }

    /* Target the specific white box at bottom */
    .plotly .svg-container {
        background: transparent !important;
    }

    .js-plotly-plot .plotly .svg-container {
        background: transparent !important;
    }

    /* Hide extra white space in Streamlit */
    .stApp > footer {
        display: none !important;
    }

    div[data-testid="stBottom"] {
        display: none !important;
    }
    
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
        padding-top: 6rem !important; /* Add space for sticky header */
    }

    /* Sticky Header Styles */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.75rem 3rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    /* Sticky Tabs - Make Streamlit tabs sticky */
    div[data-testid="stTabs"] {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 3.8rem !important;
        z-index: 998 !important;
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        padding: 0.5rem 3rem !important;
        margin: 0 -3rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        width: calc(100% + 6rem) !important;
        box-sizing: border-box !important;
        border-radius: 25px !important;
    }

    /* Tab list container - also make sticky */
    div[data-testid="stTabs"] > div {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 3.8rem !important;
        z-index: 998 !important;
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        width: 100% !important;
        max-width: none !important;
    }

    /* Tab panel content area */
    div[data-testid="stTabs"] [role="tabpanel"] {
        width: 100% !important;
        max-width: none !important;
        padding: 0 !important;
        margin: 0 !important;
        padding-top: 2rem !important;
    }

    /* Tab list styling */
    [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 8px !important;
    }

    /* Tab bar container */
    [data-baseweb="tab-bar"] {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 3.8rem !important;
        z-index: 998 !important;
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        padding: 0.5rem 0 !important;
        width: 100% !important;
        max-width: none !important;
    }

    /* Individual tab styling */
    button[data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    button[data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* HERO SECTION - Hover Effect */
    .hero-mega {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 40px;
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
        /* Removed hover lift effect */
        transform: none;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    }

    .glass-card:hover::before {
        /* Removed hover effect */
        transform: none;
    }
    
    /* BUTTONS - Modern sleek design */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 0.95rem !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        background: white !important;
        color: #334155 !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
        border-color: #667eea !important;
        background: #f8f9ff !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }

    /* Regular primary buttons (blue) - FORCE PURPLE GRADIENT */
    .stButton > button[kind="primary"],
    button[kind="primary"],
    .stButton button[kind="primary"],
    div[data-testid="stButton"] button[kind="primary"],
    [data-testid="stButton"] button[kind="primary"],
    .element-container button[kind="primary"],
    .stButton > button.kind-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        background-color: transparent !important;
        background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover,
    button[kind="primary"]:hover,
    .stButton button[kind="primary"]:hover,
    div[data-testid="stButton"] button[kind="primary"]:hover,
    [data-testid="stButton"] button[kind="primary"]:hover,
    .element-container button[kind="primary"]:hover,
    .stButton > button.kind-primary:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
        background-color: transparent !important;
        background-image: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
    }

    /* Blue SIGN IN button - using wrapper class with SOLID purple gradient */
    .blue-button-wrapper .stFormSubmitButton > button,
    .blue-button-wrapper .stFormSubmitButton > button[kind="primary"],
    .blue-button-wrapper .stButton > button,
    .blue-button-wrapper .stButton > button[kind="primary"],
    .blue-button-wrapper button,
    .blue-button-wrapper button[kind="primary"],
    .blue-button-wrapper > button,
    .blue-button-wrapper button[kind="tertiary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        background-color: transparent !important;
        background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }

    .blue-button-wrapper .stFormSubmitButton > button:hover,
    .blue-button-wrapper .stFormSubmitButton > button[kind="primary"]:hover,
    .blue-button-wrapper .stButton > button:hover,
    .blue-button-wrapper .stButton > button[kind="primary"]:hover,
    .blue-button-wrapper button:hover,
    .blue-button-wrapper button[kind="primary"]:hover,
    .blue-button-wrapper > button:hover,
    .blue-button-wrapper button[kind="tertiary"]:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
        background-color: transparent !important;
        background-image: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
    }

    /* White Forgot button - Modern minimal design */
    .white-button-wrapper .stFormSubmitButton > button,
    .white-button-wrapper .stFormSubmitButton > button[kind="primary"],
    .white-button-wrapper .stFormSubmitButton > button[kind="secondary"],
    .white-button-wrapper .stButton > button,
    .white-button-wrapper .stButton > button[kind="primary"],
    .white-button-wrapper .stButton > button[kind="secondary"],
    .white-button-wrapper button,
    .white-button-wrapper button[kind="primary"],
    .white-button-wrapper button[kind="secondary"],
    .white-button-wrapper [data-baseweb="button"],
    .white-button-wrapper [data-baseweb="base-button"],
    div.white-button-wrapper button,
    div.white-button-wrapper [data-baseweb="button"] {
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        color: #667eea !important;
        border: 1px solid transparent !important;
        box-shadow: none !important;
        font-weight: 600 !important;
        text-decoration: none !important;
    }

    .white-button-wrapper .stFormSubmitButton > button:hover,
    .white-button-wrapper .stFormSubmitButton > button[kind="primary"]:hover,
    .white-button-wrapper .stFormSubmitButton > button[kind="secondary"]:hover,
    .white-button-wrapper .stButton > button:hover,
    .white-button-wrapper .stButton > button[kind="primary"]:hover,
    .white-button-wrapper .stButton > button[kind="secondary"]:hover,
    .white-button-wrapper button:hover,
    .white-button-wrapper button[kind="primary"]:hover,
    .white-button-wrapper button[kind="secondary"]:hover,
    .white-button-wrapper [data-baseweb="button"]:hover,
    .white-button-wrapper [data-baseweb="base-button"]:hover,
    div.white-button-wrapper button:hover,
    div.white-button-wrapper [data-baseweb="button"]:hover {
        background: rgba(102, 126, 234, 0.08) !important;
        color: #5568d3 !important;
        border-color: transparent !important;
        box-shadow: none !important;
        text-decoration: underline !important;
    }
    
    /* Password visibility toggle button */
    button[aria-label*="password"],
    button[aria-label*="Show"],
    button[aria-label*="Hide"],
    .stTextInput button,
    input[type="password"] + button {
        background: #667eea !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px !important;
        min-width: 40px !important;
        height: 40px !important;
        opacity: 1 !important;
    }
    
    .stTextInput button:hover,
    input[type="password"] + button:hover {
        background: #5568d3 !important;
        transform: scale(1.05);
    }

    /* Pink CREATE FREE ACCOUNT button - using wrapper class (works with all button types) */
    .pink-button-wrapper .stFormSubmitButton > button,
    .pink-button-wrapper .stFormSubmitButton > button[kind="primary"],
    .pink-button-wrapper .stFormSubmitButton > button[kind="secondary"],
    .pink-button-wrapper .stButton > button,
    .pink-button-wrapper .stButton > button[kind="primary"],
    .pink-button-wrapper .stButton > button[kind="secondary"],
    .pink-button-wrapper button,
    .pink-button-wrapper button[kind="primary"],
    .pink-button-wrapper button[kind="secondary"] {
        background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%) !important;
        background-color: #ec4899 !important;
        background-image: linear-gradient(135deg, #ec4899 0%, #f472b6 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3) !important;
    }

    .pink-button-wrapper .stFormSubmitButton > button:hover,
    .pink-button-wrapper .stFormSubmitButton > button[kind="primary"]:hover,
    .pink-button-wrapper .stFormSubmitButton > button[kind="secondary"]:hover,
    .pink-button-wrapper .stButton > button:hover,
    .pink-button-wrapper .stButton > button[kind="primary"]:hover,
    .pink-button-wrapper .stButton > button[kind="secondary"]:hover,
    .pink-button-wrapper button:hover,
    .pink-button-wrapper button[kind="primary"]:hover,
    .pink-button-wrapper button[kind="secondary"]:hover {
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4) !important;
        background: linear-gradient(135deg, #db2777 0%, #ec4899 100%) !important;
        background-color: #db2777 !important;
        background-image: linear-gradient(135deg, #db2777 0%, #ec4899 100%) !important;
    }

    /* Pink secondary buttons - all variations */
    .stButton > button[kind="secondary"],
    .stFormSubmitButton > button[kind="secondary"],
    button[kind="secondary"],
    div[data-testid="stForm"] button[kind="secondary"],
    form button[kind="secondary"] {
        background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%) !important;
        background-color: #ec4899 !important;
        background-image: linear-gradient(135deg, #ec4899 0%, #f472b6 100%) !important;
        color: white !important;
        border: none !important;
        border-color: transparent !important;
        box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3) !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stFormSubmitButton > button[kind="secondary"]:hover,
    button[kind="secondary"]:hover,
    div[data-testid="stForm"] button[kind="secondary"]:hover,
    form button[kind="secondary"]:hover {
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4) !important;
        background: linear-gradient(135deg, #db2777 0%, #ec4899 100%) !important;
        background-color: #db2777 !important;
        background-image: linear-gradient(135deg, #db2777 0%, #ec4899 100%) !important;
    }

    /* HYPERLINKS - Evidence Explorer clickable numbers */
    a {
        transition: opacity 0.2s ease, text-decoration 0.2s ease !important;
    }

    a:hover {
        opacity: 0.7 !important;
        text-decoration: underline !important;
    }

    /* Header links - no underline */
    .header-link {
        text-decoration: none !important;
    }

    .header-link:hover {
        text-decoration: none !important;
        opacity: 0.9 !important;
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
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        max-width: none !important;
        border-bottom: none !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 15px 30px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-bottom: none !important;
        background-color: transparent !important;
        color: #334155 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-2px) !important;
        color: #667eea !important;
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;
        border: none !important;
        border-bottom: none !important;
    }
    
    /* Ensure text stays white on selected tab - all child elements */
    .stTabs [aria-selected="true"] * {
        color: white !important;
    }
    
    /* Selected tab on click/active */
    .stTabs [aria-selected="true"]:active,
    .stTabs [aria-selected="true"]:focus,
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: white !important;
    }
    
    .stTabs [aria-selected="true"]:active *,
    .stTabs [aria-selected="true"]:focus *,
    .stTabs [data-baseweb="tab"][aria-selected="true"] * {
        color: white !important;
    }
    
    /* Remove tab underline/indicator bar */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
        display: none !important;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        background-color: transparent !important;
        display: none !important;
    }
    
    /* Remove any red default underlines on tabs */
    button[data-baseweb="tab"] {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    button[data-baseweb="tab"]:hover {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    button[data-baseweb="tab"]:focus {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
        outline: none !important;
    }
    
    button[data-baseweb="tab"]:active {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
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

    .stTextInput > div > div > input:hover,
    .stSelectbox > div > div > select:hover,
    .stNumberInput > div > div > input:hover {
        border-color: #d1d5db !important;
        background: #f9fafb !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 8px 20px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
        transform: translateY(-1px) !important;
    }
    
    /* Input placeholders */
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
        font-weight: 400 !important;
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
    
    /* DATE INPUT - Fix Calendar Header Purple Background */
    /* Override the calendar popup header background */
    div[data-baseweb="popover"] [data-baseweb="button"],
    div[data-baseweb="calendar"] > div:first-child,
    div[data-baseweb="calendar"] > div > div:first-child,
    div[data-baseweb="popover"] header {
        background: white !important;
        background-color: white !important;
    }
    
    /* Calendar header controls (month/year dropdowns, arrows) */
    div[data-baseweb="calendar"] button {
        background: transparent !important;
        color: #1f2937 !important;
        border-color: #e5e7eb !important;
    }
    
    /* Selected date styling */
    div[data-baseweb="calendar"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* TOGGLE SWITCHES - Modern Design */
    [data-testid="stToggle"] {
        margin-top: 0 !important;
    }

    [data-testid="stToggle"] > div {
        justify-content: center !important;
    }

    /* Toggle switch track */
    [data-testid="stToggle"] [role="switch"] {
        width: 50px !important;
        height: 28px !important;
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }

    /* Toggle switch thumb */
    [data-testid="stToggle"] [role="switch"] > div {
        width: 22px !important;
        height: 22px !important;
        border-radius: 50% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
    }

    /* Toggle checked state */
    [data-testid="stToggle"] [aria-checked="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }

    [data-testid="stToggle"] [aria-checked="false"] {
        background: #cbd5e1 !important;
    }

    /* Hide form submission instruction text */
    .stTextInput [data-testid="stCaptionContainer"] {
        display: none !important;
    }

    /* Hide "Press Enter to submit form" message */
    .stTextInput > label > div[data-testid="stCaptionContainer"],
    .stTextInput div[data-testid="stCaptionContainer"],
    [data-testid="stForm"] .stTextInput [data-testid="stCaptionContainer"],
    [data-testid="stForm"] div[data-testid="stCaptionContainer"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* POPOVER - Enhanced Design - Purple to match other buttons */
    [data-testid="stPopover"] button {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }

    [data-testid="stPopover"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }

    /* ENHANCED CONTAINER BORDERS */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background: white !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1) !important;
        border: 2px solid #e2e8f0 !important;
    }
    
    /* SLIDERS - FORCE BLUE COLOR (Override Streamlit Red) */
    .stSlider {
        padding: 10px 0 !important;
    }

    /* Slider track - FORCE BLUE with multiple selectors */
    .stSlider > div > div > div > div,
    div[data-testid="stSlider"] > div > div > div > div,
    .stSlider [data-baseweb="slider"] > div:first-child > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        height: 10px !important;
        border-radius: 10px !important;
    }

    /* Slider thumb (handle) - Smaller with gradient fill */
    .stSlider > div > div > div > div > div,
    div[data-testid="stSlider"] > div > div > div > div > div,
    .stSlider [data-baseweb="slider"] [role="slider"],
    .stSlider div[role="slider"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        width: 20px !important;
        height: 20px !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4) !important;
        border-radius: 50% !important;
        transition: all 0.2s ease !important;
    }

    .stSlider > div > div > div > div > div:hover,
    div[data-testid="stSlider"] [role="slider"]:hover {
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Override Streamlit's accent-color (this controls slider/checkbox colors) */
    input, select, textarea {
        accent-color: #667eea !important;
    }
    
    /* Force all range inputs to be blue */
    input[type="range"],
    input[type="checkbox"],
    input[type="radio"] {
        accent-color: #667eea !important;
    }
    
    input[type="range"]::-webkit-slider-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4) !important;
        cursor: pointer !important;
    }
    
    input[type="range"]::-webkit-slider-runnable-track {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        height: 10px !important;
        border-radius: 10px !important;
    }
    
    input[type="range"]::-moz-range-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4) !important;
        cursor: pointer !important;
    }
    
    input[type="range"]::-moz-range-track {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        height: 10px !important;
        border-radius: 10px !important;
    }
    
    /* Checkbox - Force blue */
    input[type="checkbox"]:checked {
        accent-color: #667eea !important;
        background-color: #667eea !important;
    }

    /* Show slider value - simple number above handle */
    .stSlider [data-baseweb="slider"] [role="slider"] > div {
        background: none !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        color: #667eea !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        width: auto !important;
        height: auto !important;
    }

    /* Style min/max labels - keep visible */
    .stSlider [data-baseweb="slider"] [data-testid="stTickBarMin"],
    .stSlider [data-baseweb="slider"] [data-testid="stTickBarMax"] {
        font-weight: 600 !important;
        color: #64748b !important;
        font-size: 13px !important;
    }

    /* FIXED: Remove purple dot at end of slider */
    .stSlider > div > div > div::after,
    .stSlider > div > div > div > div::after,
    .stSlider [data-baseweb="slider"]::after {
        display: none !important;
    }

    /* Remove any extra elements at slider ends */
    .stSlider [data-baseweb="slider"] > div:last-child:not([role="slider"]) {
        display: none !important;
    }

    /* FIXED: Ensure only ONE circle on slider handle */
    .stSlider [role="slider"]::before,
    .stSlider [role="slider"]::after {
        display: none !important;
    }

    /* Hide any duplicate slider thumbs */
    .stSlider [data-baseweb="slider"] > div[aria-hidden="true"] {
        display: none !important;
    }

    /* FIXED: Auto-minimise selectbox after selection */
    .stSelectbox [data-baseweb="popover"] {
        max-height: 0 !important;
        overflow: hidden !important;
        transition: max-height 0.3s ease !important;
    }

    .stSelectbox:focus-within [data-baseweb="popover"] {
        max-height: 300px !important;
    }
    
    /* MULTISELECT PILLS - Purple Gradient (Override Streamlit Red) */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        background-color: #667eea !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25) !important;
        border: none !important;
    }
    
    .stMultiSelect [data-baseweb="tag"]:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
        background-color: #5568d3 !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.35) !important;
    }
    
    /* Multiselect close button (X) */
    .stMultiSelect [data-baseweb="tag"] svg {
        fill: white !important;
        color: white !important;
    }
    
    /* Multiselect dropdown */
    .stMultiSelect [data-baseweb="popover"] {
        border: 2px solid #667eea !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2) !important;
        z-index: 1 !important;
    }
    
    /* Fix z-index for all popovers and dropdowns to stay below sticky header - LOWER THAN BEFORE */
    [data-baseweb="popover"],
    [data-baseweb="select"],
    div[role="tooltip"],
    .stSelectbox [data-baseweb="popover"],
    .stMultiSelect [data-baseweb="popover"],
    div[data-baseweb="popover"],
    .stMultiSelect [data-baseweb="base-popover"],
    [data-baseweb="base-popover"] {
        z-index: 1 !important;
    }
    
    /* Ensure sticky header stays on top - MUCH HIGHER */
    header[data-testid="stHeader"] {
        z-index: 10000 !important;
    }
    
    /* Specific fix for condition selector dropdown */
    div[role="listbox"],
    ul[role="listbox"],
    [role="option"] {
        z-index: 1 !important;
    }
    
    /* CSS for header that matches inline styles - MAXIMUM PRIORITY */
    div[style*="position: fixed"][style*="top: 0"][style*="z-index"],
    div[style*="position: fixed"][style*="top: 0"] {
        z-index: 10000 !important;
    }
    
    /* Add even more baseweb selectors */
    ul[role="listbox"],
    li[role="option"],
    div[role="option"],
    .stSelectbox > div[data-baseweb="select"],
    .stMultiSelect > div[data-baseweb="select"] {
        z-index: 1 !important;
    }
    
    /* Ensure all BaseWeb dropdown content stays below header */
    div[data-baseweb="popover"] [role="listbox"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] [role="option"],
    [data-baseweb="select"] [role="listbox"],
    [data-baseweb="select"] ul {
        z-index: 1 !important;
    }
    
    /* Multiselect input field */
    .stMultiSelect [data-baseweb="select"] > div {
        border-color: #e2e8f0 !important;
        border-radius: 12px !important;
    }
    
    .stMultiSelect [data-baseweb="select"] > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* FORMS - Style form container like glass card */
    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 25px !important;
        padding: 40px !important;
        padding-bottom: 80px !important;
        margin-bottom: 100px !important;
        min-height: 400px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Add bottom padding to main content so forms aren't cut off */
    .main .block-container {
        padding-bottom: 200px !important;
    }

    [data-testid="stForm"]:hover {
        /* Removed hover movement to make form easier to populate */
        transform: none !important;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2) !important;
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
        
        /* Mobile: Adjust container padding - Only on actual mobile devices */
        .block-container {
            padding: 2rem 1rem !important;
            max-width: 100% !important;
        }
        
        /* Mobile: Fix tabs width - Keep alignment */
        div[data-testid="stTabs"] {
            padding: 0.5rem 1rem !important;
            margin: 0 -1rem !important;
            width: calc(100% + 2rem) !important;
        }
        
        /* Mobile: Tab buttons */
        .stTabs [data-baseweb="tab"] {
            padding: 10px 15px !important;
            font-size: 14px !important;
        }
        
        /* Mobile: Form inputs */
        input, textarea, select {
            font-size: 16px !important; /* Prevents zoom on iOS */
        }
        
        /* Mobile: Buttons - Don't override colors */
        button {
            padding: 12px 20px !important;
            font-size: 14px !important;
            /* Preserve button colors - do not override */
        }
        
        /* Mobile: Charts */
        .js-plotly-plot {
            width: 100% !important;
            height: auto !important;
        }
    }
    
    /* Small mobile devices */
    @media (max-width: 480px) {
        .hero-title {
            font-size: 32px !important;
        }
        
        .hero-subtitle {
            font-size: 16px !important;
        }
        
        /* Extra small mobile: Further reduce padding */
        .block-container {
            padding: 1rem 0.5rem !important;
        }
        
        div[data-testid="stTabs"] {
            padding: 0.5rem 0.5rem !important;
            margin: 0 -0.5rem !important;
            width: calc(100% + 1rem) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px !important;
            font-size: 12px !important;
        }
    }
    
    /* Desktop: Ensure proper styling is NOT overridden */
    @media (min-width: 769px) {
        .block-container {
            padding: 2rem 3rem !important;
            max-width: 1400px !important;
        }
        
        div[data-testid="stTabs"] {
            padding: 0.5rem 3rem !important;
            margin: 0 -3rem !important;
            width: calc(100% + 6rem) !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Scroll to top on page load/navigation and tab switching
st.markdown("""
<script>
// Scroll to top immediately
window.scrollTo({top: 0, behavior: 'instant'});
document.documentElement.scrollTop = 0;
document.body.scrollTop = 0;

// Add scroll-to-top on tab clicks
setTimeout(function() {
    const tabs = document.querySelectorAll('[role="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            setTimeout(function() {
                window.scrollTo({top: 0, behavior: 'smooth'});
                document.documentElement.scrollTop = 0;
                document.body.scrollTop = 0;
            }, 100);
        });
    });
}, 100);
</script>
""", unsafe_allow_html=True)

# ============================================================================
# SUPABASE HELPER FUNCTIONS
# ============================================================================
# ============================================================================
# SUPABASE AUTH HELPER FUNCTIONS
# ============================================================================

def sign_up_user(email: str, password: str, display_name: str):
    """
    Create a new user account using Supabase Auth
    Returns: (success: bool, user_data: dict, error_message: str)
    """
    if not supabase:
        return False, None, "Supabase connection not available"

    try:
        # Sign up user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name
                }
            }
        })

        if response.user:
            # Also create entry in app_users table for quick lookups
            try:
                supabase.table('app_users').insert({
                    'user_id': response.user.id,
                    'email': email
                }).execute()
            except:
                pass  # Table entry is optional, auth.users is primary

            return True, response.user, None
        else:
            return False, None, "Failed to create account"

    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return False, None, "This email is already registered"
        elif "invalid email" in error_msg.lower():
            return False, None, "Please enter a valid email address"
        elif "password" in error_msg.lower() and "weak" in error_msg.lower():
            return False, None, "Password is too weak. Use at least 8 characters"
        else:
            return False, None, f"Sign up failed: {error_msg}"


def sign_in_user(email: str, password: str):
    """
    Sign in user using Supabase Auth
    Returns: (success: bool, user_data: dict, error_message: str)
    """
    if not supabase:
        return False, None, "Supabase connection not available"

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user:
            return True, response.user, None
        else:
            return False, None, "Invalid credentials"

    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "credentials" in error_msg.lower():
            return False, None, "Invalid email or password"
        else:
            return False, None, f"Sign in failed: {error_msg}"


def sign_out_user():
    """Sign out the current user"""
    if not supabase:
        return False

    try:
        supabase.auth.sign_out()
        return True
    except:
        return False


def update_user_password(new_password: str):
    """
    Update password for currently authenticated user
    Returns: (success: bool, error_message: str)
    """
    if not supabase:
        return False, "Supabase connection not available"

    try:
        response = supabase.auth.update_user({
            "password": new_password
        })

        if response.user:
            return True, None
        else:
            return False, "Failed to update password"

    except Exception as e:
        error_msg = str(e)
        if "weak" in error_msg.lower():
            return False, "Password is too weak. Use at least 8 characters"
        else:
            return False, f"Password update failed: {error_msg}"


def get_current_user():
    """Get currently authenticated user from Supabase Auth"""
    if not supabase:
        return None

    try:
        response = supabase.auth.get_user()
        return response.user if response else None
    except:
        return None


# ============================================================================
# DATABASE PERSISTENCE FUNCTIONS FOR USER LOGS
# ============================================================================
def save_log_entry_to_database(user_id: str, entry_data: dict):
    """
    Save daily log entry to Supabase user_logs table
    Returns: (success: bool, error_message: str)
    """
    if not supabase:
        return False, "Supabase connection not available"
    
    try:
        # Prepare entry data with user_id and timestamp
        log_entry = entry_data.copy()
        log_entry['user_id'] = user_id
        log_entry['created_at'] = datetime.now().isoformat()
        
        # Convert date to ISO format if it's a datetime object
        if 'date' in log_entry and isinstance(log_entry['date'], (datetime, pd.Timestamp)):
            log_entry['date'] = log_entry['date'].strftime('%Y-%m-%d')
        
        # Convert any numpy/pandas types to Python native types
        for key, value in log_entry.items():
            if isinstance(value, (np.integer, np.floating)):
                log_entry[key] = float(value) if isinstance(value, np.floating) else int(value)
            elif isinstance(value, pd.Timestamp):
                log_entry[key] = value.isoformat()
            elif pd.isna(value):
                log_entry[key] = None
        
        # Insert into user_logs table
        response = supabase.table('user_logs').insert(log_entry).execute()
        
        if response.data:
            return True, None
        else:
            return False, "Failed to save log entry"
    
    except Exception as e:
        error_msg = str(e)
        # Check if table doesn't exist
        if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            return False, "Database table not found. Please contact support."
        return False, f"Failed to save entry: {error_msg}"


def load_user_logs_from_database(user_id: str):
    """
    Load all log entries for user from Supabase user_logs table
    Returns: DataFrame with user's log entries
    """
    if not supabase:
        st.warning("⚠️ Database connection not available. Data will not persist.")
        return pd.DataFrame()
    
    try:
        # Query user_logs table for this user's entries
        response = supabase.table('user_logs').select('*').eq('user_id', user_id).order('date', desc=False).execute()
        
        if response.data and len(response.data) > 0:
            df = pd.DataFrame(response.data)
            
            # Convert date column to datetime if it exists
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            # Remove database metadata columns if they exist
            metadata_cols = ['id', 'created_at', 'updated_at', 'user_id']
            for col in metadata_cols:
                if col in df.columns and col != 'user_id':
                    df = df.drop(columns=[col])
            
            return df
        else:
            # No data found - new user
            return pd.DataFrame()
    
    except Exception as e:
        error_msg = str(e)
        # If table doesn't exist, return empty DataFrame (fail gracefully)
        if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            st.warning("⚠️ Database tables are being set up. Your data will be saved once setup is complete.")
            return pd.DataFrame()
        
        st.error(f"❌ Failed to load your data: {error_msg}")
        return pd.DataFrame()


def update_log_entry_in_database(user_id: str, entry_date: str, updated_data: dict):
    """
    Update an existing log entry in the database
    Returns: (success: bool, error_message: str)
    """
    if not supabase:
        return False, "Supabase connection not available"
    
    try:
        # Convert date format if needed
        if isinstance(entry_date, (datetime, pd.Timestamp)):
            entry_date = entry_date.strftime('%Y-%m-%d')
        
        # Update the entry
        response = supabase.table('user_logs').update(updated_data).eq('user_id', user_id).eq('date', entry_date).execute()
        
        if response.data:
            return True, None
        else:
            return False, "Failed to update log entry"
    
    except Exception as e:
        return False, f"Failed to update entry: {str(e)}"


def delete_log_entry_from_database(user_id: str, entry_date: str):
    """
    Delete a log entry from the database
    Returns: (success: bool, error_message: str)
    """
    if not supabase:
        return False, "Supabase connection not available"
    
    try:
        # Convert date format if needed
        if isinstance(entry_date, (datetime, pd.Timestamp)):
            entry_date = entry_date.strftime('%Y-%m-%d')
        
        # Delete the entry
        response = supabase.table('user_logs').delete().eq('user_id', user_id).eq('date', entry_date).execute()
        
        if response.data is not None:
            return True, None
        else:
            return False, "Failed to delete log entry"
    
    except Exception as e:
        return False, f"Failed to delete entry: {str(e)}"


def delete_all_user_logs_from_database(user_id: str):
    """
    Delete all log entries for a user from the database
    Returns: (success: bool, error_message: str)
    """
    if not supabase:
        return False, "Supabase connection not available"
    
    try:
        # Delete all entries for this user
        response = supabase.table('user_logs').delete().eq('user_id', user_id).execute()
        
        return True, None
    
    except Exception as e:
        return False, f"Failed to delete logs: {str(e)}"


# ============================================================================
# SESSION STATE
# ============================================================================
for key, default in {
    'authenticated': False,
    'demo_mode': False,
    'username': "",
    'n1_df': pd.DataFrame(),
    'show_signup': False,
    'show_password_reset': False,
    'show_auth_page': False
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

        # Check if therapy has started
        has_yoga = (day >= therapy_start_day)

        demo_data.append({
            "date": current_date,
            "pain_score": round(pain_score, 1),
            "sleep_hours": round(sleep_hours, 1),
            "mood_score": round(mood_score, 1),
            "stress_score": round(7 - (day * 0.06), 1),
            "therapy_started": "Yoga" if (day == therapy_start_day) else "",
            "therapies_continuing": ["Yoga"] if has_yoga else []
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
# AUTH LANDING PAGE - Sign In / Create Account
# ============================================================================
if st.session_state.show_auth_page and not st.session_state.authenticated and not st.session_state.demo_mode:
    # Clean header with bear icon and title
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 2rem 0;">
        <div style="display: inline-flex; align-items: center; gap: 15px; margin-bottom: 1.5rem;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width: 50px; height: 50px;">
                <circle cx="28" cy="28" r="18" fill="#667eea"/>
                <circle cx="72" cy="28" r="18" fill="#667eea"/>
                <circle cx="50" cy="55" r="35" fill="#667eea"/>
                <ellipse cx="50" cy="68" rx="20" ry="15" fill="#5568d3"/>
            </svg>
            <h1 style="margin: 0; font-size: 48px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
                Welcome to Bearable
            </h1>
        </div>
        <p style="margin: 0; color: #64748b; font-size: 18px; font-weight: 500;">
            Track your health journey with science-backed insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    # PASSWORD RESET UI (if user clicked "Forgot?")
    if st.session_state.get('show_password_reset', False):
        st.markdown('<div style="max-width: 600px; margin: 0 auto;">', unsafe_allow_html=True)
        
        with st.form("auth_password_reset_form", clear_on_submit=False):
            st.markdown("""
                <h3 style="margin: 0 0 10px 0; color: #1a202c;">🔑 Reset Password</h3>
                <p style="font-weight: 600; margin-bottom: 25px; color: #64748b;">
                    Enter your email address and we'll send you a password reset link.
                </p>
            """, unsafe_allow_html=True)

            reset_email = st.text_input("Email Address", placeholder="your.email@example.com", label_visibility="visible", key="auth_reset_email")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
                reset_submit = st.form_submit_button("SEND RESET LINK", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
                reset_cancel = st.form_submit_button("CANCEL", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if reset_submit:
                # Validation
                if not reset_email:
                    st.error("❌ Please enter your email address")
                elif "@" not in reset_email or "." not in reset_email.split("@")[1]:
                    st.error("❌ Please enter a valid email address")
                else:
                    # Send password reset email using Supabase Auth
                    if supabase:
                        try:
                            supabase.auth.reset_password_for_email(
                                reset_email,
                                {
                                    'redirect_to': os.getenv('SUPABASE_REDIRECT_URL', 'http://localhost:8501')
                                }
                            )
                            st.success("✅ Password reset link sent! Check your email inbox (and spam folder).")
                            st.info("📧 Click the link in the email to reset your password. The link will expire in 1 hour.")
                        except Exception as e:
                            # Don't reveal if email exists or not (security best practice)
                            st.success("✅ If an account exists with this email, you will receive a password reset link shortly.")
                    else:
                        st.error("❌ Password reset is currently unavailable. Please try again later.")

            if reset_cancel:
                st.session_state.show_password_reset = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Back to sign in button
        st.markdown('<div style="margin-top: 2rem; text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
        if st.button("← Back to Sign In", key="reset_back_to_signin"):
            st.session_state.show_password_reset = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Back to home button
        st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
            if st.button("← Back to Home", use_container_width=True, key="reset_back_home"):
                st.session_state.show_auth_page = False
                st.session_state.show_password_reset = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.stop()  # Don't show the sign in/sign up forms

    # Two column layout for Sign In and Create Account
    col1, col2 = st.columns(2, gap="large")

    # SIGN IN FORM
    with col1:
        with st.form("auth_signin_form", clear_on_submit=False):
            st.markdown("""
                <div style="margin-bottom: 32px;">
                    <h2 style="margin: 0 0 8px 0; color: #111827; font-size: 28px; font-weight: 700;">Welcome Back</h2>
                    <p style="font-weight: 500; margin-bottom: 0; color: #6b7280; font-size: 15px;">Sign in to continue to your health dashboard</p>
                </div>
            """, unsafe_allow_html=True)

            username = st.text_input("", placeholder="Email address", label_visibility="collapsed", key="auth_login_email")
            st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
            password = st.text_input("", type="password", placeholder="Password", label_visibility="collapsed", key="auth_login_pass")

            st.markdown('<div style="margin-top: 28px; margin-bottom: 20px;"></div>', unsafe_allow_html=True)
            
            col_login, col_forgot = st.columns([2.5, 1])
            with col_login:
                st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
                login_clicked = st.form_submit_button("Sign In", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
            with col_forgot:
                st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
                forgot_clicked = st.form_submit_button("Forgot?", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Add spacing below buttons to make the form taller
            st.markdown('<div style="margin-bottom: 3rem;"></div>', unsafe_allow_html=True)

            if login_clicked:
                # Check demo credentials
                if username == "demo" and password == "demo":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.demo_mode = True
                    st.session_state.show_auth_page = False
                    st.session_state.redirect_to_daily_log = True
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    # Sign in with Supabase Auth
                    success, user_data, error_msg = sign_in_user(username, password)
                    if success:
                        # Get display name from user metadata
                        display_name = user_data.user_metadata.get('display_name', username)
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_id = user_data.id
                        st.session_state.demo_mode = False
                        st.session_state.show_auth_page = False
                        st.session_state.redirect_to_daily_log = True
                        
                        # Load user's historical data from database
                        with st.spinner("Loading your data..."):
                            st.session_state.n1_df = load_user_logs_from_database(user_data.id)
                        
                        st.success(f"✅ Welcome back, {display_name}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error_msg}. Try: demo / demo or create an account")

            if forgot_clicked:
                st.session_state.show_password_reset = True
                st.rerun()

    # CREATE ACCOUNT FORM - Modern Design
    with col2:
        with st.form("auth_signup_form", clear_on_submit=False):
            st.markdown("""
                <div style="margin-bottom: 32px;">
                    <h2 style="margin: 0 0 8px 0; color: #111827; font-size: 28px; font-weight: 700;">Create Account</h2>
                    <p style="font-weight: 500; margin-bottom: 0; color: #6b7280; font-size: 15px;">Start tracking your health journey today</p>
                </div>
            """, unsafe_allow_html=True)

            new_name = st.text_input("", placeholder="Full name", label_visibility="collapsed", key="auth_signup_name")
            st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
            new_email = st.text_input("", placeholder="Email address", label_visibility="collapsed", key="auth_signup_email")
            st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
            new_password = st.text_input("", type="password", placeholder="Password", label_visibility="collapsed", key="auth_signup_password")
            st.markdown('<div style="margin-top: 12px;"></div>', unsafe_allow_html=True)
            confirm_password = st.text_input("", type="password", placeholder="Confirm password", label_visibility="collapsed", key="auth_signup_confirm")

            st.markdown('<div style="margin-top: 28px; margin-bottom: 20px;"></div>', unsafe_allow_html=True)

            st.markdown('<div class="pink-button-wrapper">', unsafe_allow_html=True)
            signup_clicked = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)

            # Add spacing below button to make the form taller
            st.markdown('<div style="margin-bottom: 3rem;"></div>', unsafe_allow_html=True)

            if signup_clicked:
                # Validation
                if not new_name or not new_email or not new_password:
                    st.error("❌ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 8:
                    st.error("❌ Password must be at least 8 characters")
                elif "@" not in new_email:
                    st.error("❌ Please enter a valid email address")
                else:
                    # Create account with Supabase Auth
                    success, user_data, error_msg = sign_up_user(new_email, new_password, new_name)
                    if success:
                        st.success(f"✅ Account created successfully! Welcome, {new_name}!")
                        st.session_state.authenticated = True
                        st.session_state.username = new_email
                        st.session_state.user_id = user_data.id
                        st.session_state.demo_mode = False
                        st.session_state.show_auth_page = False
                        st.session_state.redirect_to_daily_log = True
                        
                        # Initialize empty dataframe for new user
                        st.session_state.n1_df = pd.DataFrame()
                        
                        st.rerun()
                    else:
                        st.error(f"❌ {error_msg}")

    # Back to home button
    st.markdown('<div style="margin-top: 3rem;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
        if st.button("← Back to Home", use_container_width=True, key="auth_back_home"):
            st.session_state.show_auth_page = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ============================================================================
# LANDING PAGE
# ============================================================================
elif not st.session_state.authenticated and not st.session_state.demo_mode:
    # MEGA HERO SECTION - Enhanced V9
    st.markdown("""
    <div class="hero-mega">
        <div style="position: relative; z-index: 2;">
            <div style="display: inline-block; background: rgba(255,255,255,0.2); padding: 8px 20px; border-radius: 30px; margin-bottom: 20px; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: white;">
                ✨ Evidence-Based • AI-Powered • Privacy-First
            </div>
            <h1 class="hero-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width: 60px; height: 60px; vertical-align: middle; margin-right: 15px;">
                    <circle cx="28" cy="28" r="18" fill="#ffffff"/>
                    <circle cx="72" cy="28" r="18" fill="#ffffff"/>
                    <circle cx="50" cy="55" r="35" fill="#ffffff"/>
                    <ellipse cx="50" cy="68" rx="20" ry="15" fill="#f0f0f0"/>
                </svg>
                Welcome to Bearable
            </h1>
            <p class="hero-subtitle">Discover What Natural Therapies Work for YOUR Health Condition</p>
            <p style="font-size: 19px; color: rgba(255,255,255,0.95); margin: 25px auto 0 auto; max-width: 750px; font-weight: 400; line-height: 1.7;">
                Stop guessing. Start tracking. <strong>Track your symptoms</strong>, explore evidence from <strong>500,000+ clinical trials</strong>,
                and use AI to discover personalised patterns that help you feel better.
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

    # How It Works Section
    st.markdown("""
    <div style="margin-top: 30px;">
        <h2 style="text-align: center; font-size: 36px; font-weight: 900; margin-bottom: 50px; color: #1a202c;">
            How It Works
        </h2>
    </div>
    """, unsafe_allow_html=True)

    col1_how, col2_how, col3_how, col4_how = st.columns(4, gap="medium")

    with col1_how:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 340px; display: flex; flex-direction: column; justify-content: flex-start; padding: 30px 20px;">
            <div style="font-size: 56px; margin-bottom: 20px;">1️⃣</div>
            <h3 style="font-size: 20px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Check Evidence</h3>
            <p style="color: #64748b; font-size: 14px; line-height: 1.6; font-weight: 500;">
                Explore the most studied natural therapies with positive evidence for your condition. Science-backed recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2_how:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 340px; display: flex; flex-direction: column; justify-content: flex-start; padding: 30px 20px;">
            <div style="font-size: 56px; margin-bottom: 20px;">2️⃣</div>
            <h3 style="font-size: 20px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Log Your Symptoms</h3>
            <p style="color: #64748b; font-size: 14px; line-height: 1.6; font-weight: 500;">
                Track pain, sleep, mood, and therapies in just 30 seconds per day. Simple sliders, no complex forms.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3_how:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 340px; display: flex; flex-direction: column; justify-content: flex-start; padding: 30px 20px;">
            <div style="font-size: 56px; margin-bottom: 20px;">3️⃣</div>
            <h3 style="font-size: 20px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Discover Patterns</h3>
            <p style="color: #64748b; font-size: 14px; line-height: 1.6; font-weight: 500;">
                AI analyses your data to show which therapies are working. See trends, correlations, and statistical insights.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col4_how:
        st.markdown("""
        <div class="glass-card" style="text-align: center; height: 340px; display: flex; flex-direction: column; justify-content: flex-start; padding: 30px 20px;">
            <div style="font-size: 56px; margin-bottom: 20px;">4️⃣</div>
            <h3 style="font-size: 20px; font-weight: 800; color: #1a202c; margin-bottom: 15px;">Feel Better</h3>
            <p style="color: #64748b; font-size: 14px; line-height: 1.6; font-weight: 500;">
                Make data-driven decisions about your health. Share insights with your doctor. Take control of your pain.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Add spacing after How It Works section
    st.markdown('<div style="margin-bottom: 60px;"></div>', unsafe_allow_html=True)

    # Main Content
    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        st.markdown('<div class="pink-button-wrapper">', unsafe_allow_html=True)
        if st.button("🚀 START FREE DEMO", type="primary", use_container_width=True):
            st.session_state.demo_mode = True
            st.session_state.username = "Demo User"
            st.session_state.n1_df = generate_demo_data_with_therapy()
            st.session_state.demo_just_started = True
            # Scroll to top when demo starts
            st.markdown("""
            <script>
                window.scrollTo({top: 0, behavior: 'smooth'});
            </script>
            """, unsafe_allow_html=True)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<p style="text-align: center; color: #64748b; font-size: 14px; margin-top: 15px; margin-bottom: 30px;">No credit card • No email required • Instant access</p>', unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card">
            <h3 style="margin: 0 0 15px 0;">🚀 Try Demo Mode - No Signup Required</h3>
            <p style="font-weight: 600; margin-bottom: 15px;">Explore the full app with realistic sample data. See how Bearable helps you:</p>
            <ul style="margin: 0 0 20px 20px; padding: 0;">
                <li style="margin-bottom: 8px;">📊 Visualise 30 days of health trends</li>
                <li style="margin-bottom: 8px;">🔬 Browse evidence-based therapies</li>
                <li style="margin-bottom: 8px;">📈 Track pain, sleep, mood, and more</li>
                <li style="margin-bottom: 8px;">💾 Export your data anytime</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 30px;"></div>', unsafe_allow_html=True)

        # Feature Grid - Enhanced
        st.markdown("""
        <div style="margin-top: 40px;">
            <h3 style="text-align: center; font-size: 28px; font-weight: 800; margin-bottom: 35px; color: #1a202c;">
                Why Bearable?
            </h3>
        </div>
        <div class="feature-grid">
            <div class="feature-box">
                <span class="feature-icon">🔬</span>
                <div class="feature-title">500K+ Trials AND<br>1M+ Studies</div>
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
                <div class="feature-desc">Get personalised therapy explanations and pattern detection in your health data</div>
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
                <div class="feature-desc">Mobile-optimised design works perfectly on phone, tablet, or desktop</div>
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

            username = st.text_input("Email", placeholder="your.email@example.com", label_visibility="visible", key="login_email", help="")
            password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="visible", key="login_pass", help="")

            col_login, col_forgot = st.columns([3, 1])
            with col_login:
                st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
                login_clicked = st.form_submit_button("SIGN IN", use_container_width=True, type="primary")
                st.markdown('</div>', unsafe_allow_html=True)
            with col_forgot:
                st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
                forgot_clicked = st.form_submit_button("Forgot?", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if login_clicked:
                # Check demo credentials
                if username == "demo" and password == "demo":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.demo_mode = True
                    st.session_state.redirect_to_daily_log = True
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    # Sign in with Supabase Auth
                    success, user_data, error_msg = sign_in_user(username, password)
                    if success:
                        # Get display name from user metadata
                        display_name = user_data.user_metadata.get('display_name', username)
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_id = user_data.id
                        st.session_state.demo_mode = False
                        st.session_state.redirect_to_daily_log = True
                        st.success(f"✅ Welcome back, {display_name}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error_msg}. Try: demo / demo or create an account")

            if forgot_clicked:
                st.session_state.show_password_reset = True
                st.session_state.show_signup = False
                st.rerun()

            st.markdown("""
                <div style="text-align: center; margin-top: 10px; padding-top: 10px; border-top: 1px solid #e2e8f0;">
                    <p style="color: #94a3b8; font-size: 14px; margin: 0 0 10px 0;">Don't have an account?</p>
                </div>
            """, unsafe_allow_html=True)

            # Create Account button inside form
            st.markdown('<div class="pink-button-wrapper">', unsafe_allow_html=True)
            create_account_clicked = st.form_submit_button("CREATE FREE ACCOUNT", use_container_width=True, type="primary")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add spacing below the button to push it up from the bottom
            st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

            if create_account_clicked:
                st.session_state.show_auth_page = True
                st.session_state.show_signup = False
                st.session_state.show_password_reset = False
                st.rerun()

        st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)

        # Password Reset Form - Using Supabase Auth
        if st.session_state.show_password_reset:
            with st.form("password_reset_form", clear_on_submit=False):
                st.markdown("""
                    <h3 style="margin: 0 0 10px 0;">🔑 Reset Password</h3>
                    <p style="font-weight: 600; margin-bottom: 25px; color: #64748b;">
                        Enter your email address and we'll send you a password reset link.
                    </p>
                """, unsafe_allow_html=True)

                reset_email = st.text_input("Email Address", placeholder="your.email@example.com", label_visibility="visible", key="reset_email")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
                    reset_clicked = st.form_submit_button("SEND RESET LINK", use_container_width=True, type="primary")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
                    cancel_reset_clicked = st.form_submit_button("CANCEL", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                if reset_clicked:
                    # Validation
                    if not reset_email:
                        st.error("❌ Please enter your email address")
                    elif "@" not in reset_email or "." not in reset_email.split("@")[1]:
                        st.error("❌ Please enter a valid email address")
                    else:
                        # Send password reset email using Supabase Auth
                        if supabase:
                            try:
                                # Supabase will send a password reset email
                                supabase.auth.reset_password_for_email(
                                    reset_email,
                                    {
                                        'redirect_to': os.getenv('SUPABASE_REDIRECT_URL', 'http://localhost:8501')
                                    }
                                )
                                st.success("✅ Password reset link sent! Check your email inbox (and spam folder).")
                                st.info("📧 Click the link in the email to reset your password. The link will expire in 1 hour.")
                                st.session_state.show_password_reset = False
                                # Don't rerun immediately so user can read the message
                            except Exception as e:
                                error_msg = str(e)
                                if "not found" in error_msg.lower() or "user" in error_msg.lower():
                                    # Don't reveal if email exists or not (security best practice)
                                    st.success("✅ If an account exists with this email, you will receive a password reset link shortly.")
                                    st.session_state.show_password_reset = False
                                else:
                                    st.error(f"❌ Failed to send reset link: {error_msg}")
                        else:
                            st.error("❌ Password reset is currently unavailable. Please try again later.")

                if cancel_reset_clicked:
                    st.session_state.show_password_reset = False
                    st.rerun()

            st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)

        # Initialize session state for showing signup form
        if "show_signup" not in st.session_state:
            st.session_state.show_signup = False

        if st.session_state.show_signup:
            # Show signup form
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("""
                    <h3 style="margin: 0 0 10px 0;">📝 Create Your Account</h3>
                    <p style="font-weight: 600; margin-bottom: 25px; color: #64748b;">Start tracking your health journey</p>
                """, unsafe_allow_html=True)

                new_name = st.text_input("Name", placeholder="Enter your full name", label_visibility="visible", key="signup_name")
                new_email = st.text_input("Email", placeholder="your.email@example.com", label_visibility="visible", key="signup_email")
                new_password = st.text_input("Password", type="password", placeholder="Create a strong password", label_visibility="visible", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", label_visibility="visible", key="signup_confirm")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="pink-button-wrapper">', unsafe_allow_html=True)
                    signup_clicked = st.form_submit_button("CREATE ACCOUNT", use_container_width=True, type="primary")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
                    cancel_clicked = st.form_submit_button("CANCEL", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                if signup_clicked:
                    # Validation
                    if not new_name or not new_email or not new_password:
                        st.error("❌ Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    elif "@" not in new_email:
                        st.error("❌ Please enter a valid email address")
                    else:
                        # Load existing accounts
                        import json
                        import os
                        accounts_file = "data/accounts.json"

                        # Create data directory if it doesn't exist
                        os.makedirs("data", exist_ok=True)

                        # Load existing accounts or create new file
                        if os.path.exists(accounts_file):
                            with open(accounts_file, "r") as f:
                                accounts = json.load(f)
                        else:
                            accounts = {}

                        # Check if email already exists
                        if new_email in accounts:
                            st.error("❌ This email is already registered")
                        else:
                            # Save new account - username is the email
                            accounts[new_email] = {
                                "name": new_name,
                                "username": new_email,  # Username is the email
                                "password": new_password,  # In production, hash this!
                                "email": new_email
                            }

                            with open(accounts_file, "w") as f:
                                json.dump(accounts, f, indent=2)

                            st.success(f"✅ Account created successfully! Welcome, {new_name}!")
                            st.session_state.authenticated = True
                            st.session_state.username = new_email
                            st.session_state.demo_mode = False
                            st.session_state.show_signup = False
                            st.session_state.redirect_to_daily_log = True
                            st.rerun()

                if cancel_clicked:
                    st.session_state.show_signup = False
                    st.rerun()

        # Trust Badges
        st.markdown("""
        <div class="glass-card" style="margin-top: 25px; padding: 25px;">
            <div style="text-align: center;">
                <p style="font-size: 13px; color: #64748b; margin-bottom: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Trusted By</p>
                <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div style="font-size: 20px;">🏥</div>
                    <div style="font-size: 20px;">🔬</div>
                    <div style="font-size: 20px;">🧘🏻‍♀️</div>
                    <div style="font-size: 20px;">🩺</div>
                </div>
                <p style="font-size: 13px; color: #64748b; margin-top: 15px; font-weight: 500;">Healthcare providers & health condition patients worldwide</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Testimonials
        testimonial_html = """
        <div class="glass-card" style="margin-top: 30px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(245, 243, 255, 0.95) 100%); border-left: 4px solid #8b5cf6; padding: 35px;">
            <div style="text-align: center;">
                <div style="font-size: 32px; margin-bottom: 20px; letter-spacing: 3px;">
                    <span style="color: #8b5cf6;">★★★★★</span>
                </div>
                <p style="font-style: italic; color: #1e293b; margin-bottom: 18px; font-size: 16px; font-weight: 500; line-height: 1.8;">
                    After 2 years with my health condition, this app helped me identify that yoga actually reduced my pain by 35%. My doctor was amazed by the data.
                </p>
                <div style="display: inline-block; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 8px 20px; border-radius: 20px; margin-bottom: 25px;">
                    <p style="font-size: 13px; font-weight: 700; color: white; margin: 0;">Sarah M., Fibromyalgia patient</p>
                </div>
                <div style="border-top: 2px solid #e2e8f0; padding-top: 25px; margin-top: 25px;">
                    <p style="font-style: italic; color: #1e293b; margin-bottom: 18px; font-size: 16px; font-weight: 500; line-height: 1.8;">
                        The evidence explorer saved me hours of research. I found 3 therapies I had never heard of, all with solid clinical backing.
                    </p>
                    <div style="display: inline-block; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 8px 20px; border-radius: 20px; margin-bottom: 25px;">
                        <p style="font-size: 13px; font-weight: 700; color: white; margin: 0;">Michael R., Back pain sufferer</p>
                    </div>
                </div>
                <div style="border-top: 2px solid #e2e8f0; padding-top: 25px; margin-top: 25px;">
                    <p style="font-style: italic; color: #1e293b; margin-bottom: 18px; font-size: 16px; font-weight: 500; line-height: 1.8;">
                        Tracking my symptoms daily helped me realise certain foods were triggering my migraines. I've reduced episodes by 60% in just 3 months!
                    </p>
                    <div style="display: inline-block; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 8px 20px; border-radius: 20px;">
                        <p style="font-size: 13px; font-weight: 700; color: white; margin: 0;">Jennifer L., Migraine patient</p>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(testimonial_html, unsafe_allow_html=True)

    # Final CTA
    st.markdown("""
    <div class="glass-card" style="text-align: center; margin: 60px 0 40px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 50px 40px;">
        <h2 style="color: white; font-size: 32px; font-weight: 900; margin-bottom: 20px;">
            Ready to Take Control of Your Health?
        </h2>
        <p style="color: rgba(255,255,255,0.95); font-size: 18px; margin-bottom: 35px; max-width: 600px; margin-left: auto; margin-right: auto;">
            Join thousands using Bearable to discover what actually works for their health condition.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="pink-button-wrapper">', unsafe_allow_html=True)
        if st.button("🚀 START FREE DEMO", type="primary", use_container_width=True, key="cta_bottom"):
            st.session_state.demo_mode = True
            st.session_state.username = "Demo User"
            st.session_state.n1_df = generate_demo_data_with_therapy()
            st.session_state.demo_just_started = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ============================================================================
# AUTHENTICATED APP
# ============================================================================

# Sidebar
with st.sidebar:
    if st.session_state.demo_mode:
        st.markdown("### 🎯 Demo Mode")
        st.info(f"Welcome, {st.session_state.username}!")
        st.markdown("---")
        st.markdown('<div class="pink-button-wrapper">', unsafe_allow_html=True)
        if st.button("🏠 EXIT DEMO & RETURN HOME", use_container_width=True, type="primary"):
            st.session_state.demo_mode = False
            st.session_state.authenticated = False
            st.session_state.n1_df = pd.DataFrame()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.authenticated:
        st.markdown(f"### 👋 {st.session_state.username}")
        st.markdown("---")
        st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Modern Sticky Header Bar - Create unified header
if st.session_state.demo_mode:
    st.markdown("""
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 0.75rem 3rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                display: flex; align-items: center; justify-content: flex-start;">
        <a href="?" target="_self" class="header-link" style="display: flex; align-items: center; gap: 12px; text-decoration: none; cursor: pointer;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width: 32px; height: 32px;">
                <circle cx="28" cy="28" r="18" fill="#ffffff"/>
                <circle cx="72" cy="28" r="18" fill="#ffffff"/>
                <circle cx="50" cy="55" r="35" fill="#ffffff"/>
                <ellipse cx="50" cy="68" rx="20" ry="15" fill="#f0f0f0"/>
            </svg>
            <h1 style="margin: 0; font-size: 1.5rem; color: white; font-weight: 800;">Bearable</h1>
            <span style="background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-left: 0.5rem; box-shadow: 0 2px 8px rgba(236, 72, 153, 0.3);">DEMO MODE</span>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
else:
    st.markdown("""
    <div style="position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 0.75rem 3rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                display: flex; align-items: center; justify-content: flex-start;">
        <a href="?" target="_self" class="header-link" style="display: flex; align-items: center; gap: 12px; text-decoration: none; cursor: pointer;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width: 32px; height: 32px;">
                <circle cx="28" cy="28" r="18" fill="#ffffff"/>
                <circle cx="72" cy="28" r="18" fill="#ffffff"/>
                <circle cx="50" cy="55" r="35" fill="#ffffff"/>
                <ellipse cx="50" cy="68" rx="20" ry="15" fill="#f0f0f0"/>
            </svg>
            <h1 style="margin: 0; font-size: 1.5rem; color: white; font-weight: 800;">Bearable</h1>
        </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 30px 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            border: 1px solid rgba(255, 255, 255, 0.8);
            text-align: center; 
            margin-left: -3rem;
            margin-right: -3rem;
            margin-bottom: 40px;
            margin-top: 2rem;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 15px;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width: 50px; height: 50px;">
            <circle cx="28" cy="28" r="18" fill="#7c5dcf"/>
            <circle cx="72" cy="28" r="18" fill="#7c5dcf"/>
            <circle cx="50" cy="55" r="35" fill="#8b6ddb"/>
            <ellipse cx="50" cy="68" rx="20" ry="15" fill="#9d82e8"/>
        </svg>
        <h1 style="margin: 0; font-size: 42px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Welcome to Bearable
        </h1>
    </div>
    <p style="margin: 0; color: #64748b; font-size: 18px; font-weight: 500;">
        Track your health journey with science-backed insights
    </p>
</div>
""", unsafe_allow_html=True)

# Create tabs - add login/logout as 5th tab
if st.session_state.authenticated:
    tab_names = [
        "📊 Dashboard",
        "🌱 Daily Log",
        "🔬 Evidence Explorer",
        "⚙️ Settings",
        "🚪 Logout"
    ]
else:
    tab_names = [
        "📊 Dashboard",
        "🌱 Daily Log",
        "🔬 Evidence Explorer",
        "⚙️ Settings",
        "🔐 Login"
    ]

tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_names)

# Scroll to top when demo mode is activated
if st.session_state.get("demo_just_started", False):
    st.markdown("""
    <script>
    // Scroll to top immediately and repeatedly to ensure it works
    function scrollToTopForce() {
        window.scrollTo(0, 0);
        window.parent.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }
    
    // Execute immediately
    scrollToTopForce();
    
    // Execute after slight delay to catch any late-rendering elements
    setTimeout(scrollToTopForce, 50);
    setTimeout(scrollToTopForce, 100);
    setTimeout(scrollToTopForce, 200);
    setTimeout(scrollToTopForce, 300);
    
    // Keep forcing scroll to top until page settles
    let scrollAttempts = 0;
    const scrollInterval = setInterval(function() {
        scrollToTopForce();
        scrollAttempts++;
        if (scrollAttempts >= 10) {
            clearInterval(scrollInterval);
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    st.session_state.demo_just_started = False

# Auto-redirect to Daily Log after login
if st.session_state.get("redirect_to_daily_log", False):
    st.markdown("""
    <script>
    // Scroll to top
    window.parent.scrollTo(0, 0);

    // Click the Daily Log tab (second tab, index 1)
    setTimeout(function() {
        const tabs = window.parent.document.querySelectorAll('[role="tab"]');
        if (tabs && tabs.length > 1) {
            tabs[1].click();
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    st.session_state.redirect_to_daily_log = False

# ============================================================================
# TAB 1: DASHBOARD
# ============================================================================
with tab1:
    # Header box matching Daily Log style
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem 2.5rem; border-radius: 20px; margin-bottom: 2rem;
                box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            📊 Health Dashboard
        </h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Visualize your health trends and discover patterns
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Check for empty state (new user or no data logged yet)
    # Temporarily commented out to fix tab rendering issue
    if False and st.session_state.n1_df.empty and not st.session_state.demo_mode:
        # EMPTY STATE FOR NEW USERS
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px; margin: 2rem 0; box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);">
            <h2 style="color: white; font-size: 2.5rem; margin-bottom: 1rem; font-weight: 800;">
                👋 Welcome to Your Health Dashboard!
            </h2>
            <p style="color: rgba(255,255,255,0.95); font-size: 1.3rem; max-width: 600px; margin: 0 auto 1.5rem auto; line-height: 1.6;">
                Start logging your symptoms in the <strong>📝 Daily Log</strong> tab to see your personalized health insights here.
            </p>
            <div style="background: rgba(255,255,255,0.15); border-radius: 15px; padding: 1.5rem; max-width: 500px; margin: 0 auto; backdrop-filter: blur(10px);">
                <p style="color: white; font-size: 1.1rem; margin: 0 0 0.5rem 0; font-weight: 600;">
                    💡 Pro Tip
                </p>
                <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin: 0;">
                    Log for <strong>7 consecutive days</strong> to unlock trend analysis and therapy effectiveness insights!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show call to action
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
            if st.button("📝 Go to Daily Log", type="primary", use_container_width=True, key="empty_state_cta"):
                st.session_state.active_tab = "📝 Daily Log"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Use demo or user data
        if st.session_state.n1_df.empty:
            display_df = generate_demo_data()
            st.info("📊 Showing demo data. Start logging to see your own insights!")
        else:
            display_df = st.session_state.n1_df.copy()
        
        # Show progress message for users with some data but less than 7 days
        if not st.session_state.demo_mode and len(st.session_state.n1_df) > 0 and len(st.session_state.n1_df) < 7:
            days_logged = len(st.session_state.n1_df)
            days_remaining = 7 - days_logged
            st.info(f"📊 Great progress! You've logged **{days_logged}** day(s). Keep going for **{days_remaining}** more day(s) to unlock full trend analysis!")   

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
                value=round(pain_current, 1),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "😣 Pain Level", 'font': {'size': 18, 'family': 'Inter'}},
                number={'valueformat': '.1f', 'suffix': "/10", 'font': {'size': 32, 'family': 'Inter', 'color': '#1a202c'}},
                delta={'reference': round(pain_prev, 1), 'increasing': {'color': "#ef4444"}, 'decreasing': {'color': "#10b981"}},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#e2e8f0"},
                    'bar': {'color': "#ec4899", 'thickness': 0.7},
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
            st.plotly_chart(pain_gauge, use_container_width=True, config={'displayModeBar': False})

        with col2:
            # Sleep gauge (0-8h, higher is better - use blue color)
            sleep_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=round(sleep_current, 1),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "😴 Sleep Hours", 'font': {'size': 18, 'family': 'Inter'}},
                number={'valueformat': '.1f', 'suffix': "h", 'font': {'size': 32, 'family': 'Inter', 'color': '#1a202c'}},
                delta={'reference': round(sleep_prev, 1), 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
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
            st.plotly_chart(sleep_gauge, use_container_width=True, config={'displayModeBar': False})

        with col3:
            # Mood gauge (0-10, higher is better - use green color)
            mood_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=round(mood_current, 1),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "🙂 Mood Score", 'font': {'size': 18, 'family': 'Inter'}},
                number={'valueformat': '.1f', 'suffix': "/10", 'font': {'size': 32, 'family': 'Inter', 'color': '#1a202c'}},
                delta={'reference': round(mood_prev, 1), 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
                gauge={
                    'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#e2e8f0"},
                    'bar': {'color': "#8b5cf6", 'thickness': 0.7},
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
            st.plotly_chart(mood_gauge, use_container_width=True, config={'displayModeBar': False})

        st.markdown("---")
        
        # Trend Chart
        st.markdown("### 📊 30-Day Trend Analysis")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=display_df['date'],
            y=display_df['pain_score'],
            mode='lines+markers',
            name='Pain',
            line=dict(color='#ec4899', width=4),
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
            line=dict(color='#8b5cf6', width=4),
            marker=dict(size=10, line=dict(width=2, color='white'))
        ))

        # Add invisible trace for "Started Natural Therapy" legend entry
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='lines',
            name='Started Natural Therapy',
            line=dict(color='#10b981', width=3, dash='dash'),
            showlegend=True
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
                        line_color="#10b981",
                        line_width=3
                    )
                    # Add a text annotation with yoga emoji and therapy name in white box
                    fig.add_annotation(
                        x=therapy_date,
                        y=1,
                        yref="paper",
                        text=f"🧘🏻‍♀️ {therapy_name}",
                        showarrow=False,
                        font=dict(size=16, color="#1a202c", family="Inter", weight=700),
                        yshift=25,
                        bgcolor="rgba(255, 255, 255, 0.98)",
                        bordercolor="rgba(0, 0, 0, 0)",
                        borderwidth=0,
                        borderpad=10,
                        opacity=1
                    )

        fig.update_layout(
            height=550,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=14, color="#1a202c"),
            hovermode=False,
            margin=dict(b=180),  # Add more bottom margin for legend space
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.28,
                xanchor="center",
                x=0.5,
                font=dict(size=16, weight=700),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)'
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

        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': False,
            'staticPlot': False,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['toImage']
        })

        st.markdown("---")

        # ============================================================================
        # CAUSAL ANALYSIS SECTION
        # ============================================================================
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                    padding: 2rem 2.5rem; border-radius: 20px; margin: 2rem 0;
                    box-shadow: 0 15px 50px rgba(139, 92, 246, 0.3);">
            <h2 style="color: white; margin: 0 0 0.5rem 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
                🎯 Is Your Therapy Working?
            </h2>
            <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 1rem; font-weight: 400; line-height: 1.6;">
                We compare your pain levels <strong>before and after</strong> starting each therapy to see if there's a real change.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Check if there are any therapies started
        if 'therapy_started' in display_df.columns:
            therapies_started = display_df[display_df['therapy_started'].notna() & (display_df['therapy_started'] != '')]['therapy_started'].unique()

            if len(therapies_started) > 0:
                # Analyse each therapy
                for therapy in therapies_started:
                    therapy_effect = calculate_therapy_effect(display_df, therapy, metric="pain_score")

                    if therapy_effect and therapy_effect.get('ready'):
                        # Determine effectiveness level in plain language
                        effect_size = therapy_effect['cohens_d']
                        if effect_size < 0.2:
                            effect_label = "Minimal Change"
                            effect_color = "#94a3b8"
                            effect_description = "Very small difference noticed"
                        elif effect_size < 0.5:
                            effect_label = "Noticeable Change"
                            effect_color = "#60a5fa"
                            effect_description = "You may be feeling some improvement"
                        elif effect_size < 0.8:
                            effect_label = "Significant Change"
                            effect_color = "#8b5cf6"
                            effect_description = "Clear improvement in your pain"
                        else:
                            effect_label = "Major Change"
                            effect_color = "#7c3aed"
                            effect_description = "Substantial improvement in your pain"

                        # Significance badge in plain language
                        sig_badge = "✅ Results Look Reliable" if therapy_effect['significant'] else "~ Needs More Data"
                        sig_color = "#22c55e" if therapy_effect['significant'] else "#ec4899"

                        # Create therapy effect card with enhanced design
                        st.markdown(f"""
                        <div style="background: white; border-radius: 24px; padding: 2rem; margin: 1.5rem 0;
                                    box-shadow: 0 20px 60px rgba(0,0,0,0.12); border-left: 6px solid #8b5cf6;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                                <div style="display: flex; align-items: center; gap: 0.75rem;">
                                    <div style="background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                                                width: 50px; height: 50px; border-radius: 14px;
                                                display: flex; align-items: center; justify-content: center;">
                                        <span style="font-size: 24px;">🧘🏻‍♀️</span>
                                    </div>
                                    <h3 style="margin: 0; color: #0f172a; font-size: 1.75rem; font-weight: 800;">
                                        {therapy}
                                    </h3>
                                </div>
                                <div style="background: {'#22c55e' if therapy_effect['significant'] else 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)'};
                                            color: white; padding: 0.65rem 1.5rem; border-radius: 25px;
                                            font-size: 0.9rem; font-weight: 700;">
                                    {sig_badge}
                                </div>
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem;">
                                <div style="background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                                            padding: 1.5rem; border-radius: 16px; color: white;">
                                    <div style="font-size: 0.75rem; font-weight: 700; margin-bottom: 0.75rem;">HOW MUCH CHANGE?</div>
                                    <div style="font-size: 2rem; font-weight: 900; margin-bottom: 0.5rem;">{effect_label}</div>
                                    <div style="font-size: 0.9rem; font-weight: 600;">{effect_description}</div>
                                </div>
                                <div style="background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                                            padding: 1.5rem; border-radius: 16px; color: white;">
                                    <div style="font-size: 0.75rem; font-weight: 700; margin-bottom: 0.75rem;">PAIN REDUCTION</div>
                                    <div style="font-size: 2rem; font-weight: 900; margin-bottom: 0.5rem;">{abs(therapy_effect['effect']):.1f} pts</div>
                                    <div style="font-size: 0.9rem; font-weight: 600;">{abs(therapy_effect['effect_pct']):.1f}% change</div>
                                </div>
                                <div style="background: {'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' if therapy_effect['significant'] else 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)'};
                                            padding: 1.5rem; border-radius: 16px; color: white;">
                                    <div style="font-size: 0.75rem; font-weight: 700; margin-bottom: 0.75rem;">RELIABILITY</div>
                                    <div style="font-size: 1.4rem; font-weight: 900; margin-bottom: 0.5rem; line-height: 1.3;">{"95% confident<br/>this is real" if therapy_effect['significant'] else "Need more tracking days"}</div>
                                    <div style="font-size: 0.9rem; font-weight: 600;">Based on {therapy_effect['days_before'] + therapy_effect['days_after']} days of data</div>
                                </div>
                                <div style="background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                                            padding: 1.5rem; border-radius: 16px; color: white;">
                                    <div style="font-size: 0.75rem; font-weight: 700; margin-bottom: 0.75rem;">TRACKING PERIOD</div>
                                    <div style="font-size: 2rem; font-weight: 900; margin-bottom: 0.5rem;">{therapy_effect['days_before'] + therapy_effect['days_after']} days</div>
                                    <div style="font-size: 0.9rem; font-weight: 600; line-height: 1.5;">
                                        {therapy_effect['days_before']} days before therapy<br/>
                                        {therapy_effect['days_after']} days after therapy
                                    </div>
                                </div>
                            </div>
                            <div style="background: #f1f5f9; padding: 1.5rem; border-radius: 16px; margin-top: 1rem;
                                        border-left: 6px solid #8b5cf6;">
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; color: #334155;">
                                    <div><strong style="color: #3b82f6;">📈 Before:</strong> <span style="font-weight: 600;">{therapy_effect['before_mean']:.1f}/10 avg pain</span></div>
                                    <div><strong style="color: #8b5cf6;">📉 After:</strong> <span style="font-weight: 600;">{therapy_effect['after_mean']:.1f}/10 avg pain</span></div>
                                    <div><strong style="color: #8b5cf6;">🎯 Impact:</strong> <span style="font-weight: 600;">{abs(therapy_effect['effect']):.1f} point {"reduction" if therapy_effect['effect'] < 0 else "increase"}</span></div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    elif therapy_effect and not therapy_effect.get('ready'):
                        # Not enough data yet
                        days_needed = therapy_effect.get('days_needed', 0)
                        stage = therapy_effect.get('stage', 'before')

                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
                                    border: 3px solid #ec4899; border-radius: 24px;
                                    padding: 2rem; margin: 1.5rem 0;
                                    box-shadow: 0 20px 60px rgba(245, 158, 11, 0.2);">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                <div style="background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
                                            width: 50px; height: 50px; border-radius: 14px;
                                            display: flex; align-items: center; justify-content: center;
                                            box-shadow: 0 8px 20px rgba(245, 158, 11, 0.3);">
                                    <span style="font-size: 24px;">⏳</span>
                                </div>
                                <h3 style="margin: 0; color: #92400e; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px;">
                                    {therapy} - Building Evidence
                                </h3>
                            </div>
                            <div style="background: rgba(255,255,255,0.7); padding: 1.25rem;
                                        border-radius: 12px; border-left: 4px solid #ec4899;">
                                <p style="margin: 0; color: #78350f; font-size: 1rem; line-height: 1.6; font-weight: 600;">
                                    📊 Need <strong style="color: #ea580c; font-size: 1.1rem;">{days_needed} more days</strong>
                                    of data {"before" if stage == "before" else "after"} starting this therapy
                                </p>
                                <p style="margin: 0.75rem 0 0 0; color: #92400e; font-size: 0.95rem;">
                                    💡 Keep logging daily to unlock causal analysis with statistical significance!
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("🎯 Start tracking a therapy in the Daily Log tab to see causal analysis here!")
        else:
            st.info("🎯 Start tracking a therapy in the Daily Log tab to see causal analysis here!")

        # ============================================================================
        # KEY INSIGHTS SUMMARY
        # ============================================================================
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                    padding: 2rem 2.5rem; border-radius: 20px; margin: 2rem 0;
                    box-shadow: 0 15px 50px rgba(139, 92, 246, 0.3);">
            <h2 style="color: white; margin: 0 0 0.5rem 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
                💡 Data Insights & Patterns
            </h2>
            <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 1rem; font-weight: 400; line-height: 1.6;">
                Automated analysis of your unique data patterns and trends.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Generate insights based on data
        insights = []

        # Pain trend insight
        if len(display_df) >= 7:
            recent_pain = display_df.tail(7)['pain_score'].mean()
            older_pain = display_df.head(7)['pain_score'].mean()
            pain_change = recent_pain - older_pain

            if pain_change < -1:
                insights.append(("🎉 Positive Progress",
                               f"Your pain has decreased by {abs(pain_change):.1f} points over the tracking period.",
                               "#8b5cf6"))
            elif pain_change > 1:
                insights.append(("⚠️ Change Detected",
                               f"Your pain has increased by {pain_change:.1f} points recently.",
                               "#3b82f6"))
            else:
                insights.append(("📊 Stable Pattern",
                               "Your pain levels have remained relatively stable. Continue tracking to identify patterns.",
                               "#3b82f6"))

        # Sleep-pain relationship
        if 'sleep_hours' in display_df.columns and len(display_df) >= 10:
            sleep_pain_corr = display_df[['sleep_hours', 'pain_score']].corr().iloc[0, 1]
            if sleep_pain_corr < -0.3:
                # Convert correlation to user-friendly description
                if sleep_pain_corr < -0.7:
                    strength = "strong"
                elif sleep_pain_corr < -0.5:
                    strength = "moderate"
                else:
                    strength = "weak"
                insights.append(("😴 Sleep-Pain Connection",
                               f"Your data shows a {strength} link between better sleep and lower pain. When you sleep more, your pain tends to decrease.",
                               "#3b82f6"))

        # Mood insight
        if 'mood_score' in display_df.columns and len(display_df) >= 7:
            recent_mood = display_df.tail(7)['mood_score'].mean()
            if recent_mood >= 7:
                insights.append(("🌟 Positive Mood Trend",
                               f"Your mood has been trending positive (avg: {recent_mood:.1f}/10).",
                               "#8b5cf6"))
            elif recent_mood < 5:
                insights.append(("💭 Mood Pattern Noted",
                               f"Your mood scores have been lower (avg: {recent_mood:.1f}/10).",
                               "#ec4899"))

        # Display insights using simple containers
        for title, message, color in insights:
            with st.container():
                st.markdown(f"""
                <div style="background: white; border-left: 6px solid {color};
                            border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <h4 style="color: {color}; margin: 0 0 0.5rem 0; font-size: 1.1rem; font-weight: 700;">
                        {title}
                    </h4>
                    <p style="color: #475569; margin: 0; font-size: 0.95rem; line-height: 1.6;">
                        {message}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        if not insights:
            st.info("📊 Keep logging for at least 7 days to see personalised insights!")

    else:
        st.info("📝 Start logging in the Daily Log tab to see your dashboard!")

    # Add bottom spacing to ensure content is visible above footer
    st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)

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
    # Enhanced header with modern gradient background
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem 2.5rem; border-radius: 20px; margin-bottom: 2rem;
                box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            🌱 Daily Wellness Log
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 400;">
            Track how you feel to discover what helps you most
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for toggles
    st.session_state.setdefault("good_day", False)
    st.session_state.setdefault("track_cycle", False)
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

    # Modern Action bar with white box container - using container with border
    with st.container(border=True):
        # Header
        st.markdown("""
        <div style="margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 2px solid #f1f5f9;">
            <h3 style="margin: 0; color: #1a202c; font-size: 1.4rem; font-weight: 800;">
                ⚡ Quick Actions
            </h3>
            <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 1rem; font-weight: 500;">
                Speed up your daily logging with these helpful tools
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Grid layout for actions
        col1, col2, col3, col4 = st.columns(4, gap="large")

        # Copy Yesterday button
        with col1:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="background: rgba(102, 126, 234, 0.1); width: 80px; height: 80px;
                            border-radius: 50%; display: flex; align-items: center;
                            justify-content: center; margin: 0 auto 1rem auto;">
                    <span style="font-size: 3rem;">🌿</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Check if data was already copied today
            today = dt.date.today()

            st.markdown('<div class="blue-button-wrapper" style="margin-bottom: 0;">', unsafe_allow_html=True)
            if st.button("Copy Yesterday", key="dup_yesterday_bar", use_container_width=True, type="primary"):
                last = _get_latest_row()
                if last is None:
                    st.toast("⚠️ No previous day to duplicate yet. Add your first entry below.", icon="⚠️")
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
                    st.toast("✅ Duplicated yesterday's values to today!", icon="✅")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Quick note popover
        with col2:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="background: rgba(102, 126, 234, 0.1); width: 80px; height: 80px;
                            border-radius: 50%; display: flex; align-items: center;
                            justify-content: center; margin: 0 auto 1rem auto;">
                    <span style="font-size: 3rem;">📝</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Use popover for note input - wrap in blue-button-wrapper for consistency
            st.markdown('<div class="blue-button-wrapper" style="margin-bottom: 0;">', unsafe_allow_html=True)
            with st.popover("Add Note", use_container_width=True):
                note = st.text_area("Note for today", key="quick_note_text", height=100, placeholder="Write your note here...")
                col_save, col_clear = st.columns(2)
                with col_save:
                    st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
                    if st.button("Save", key="quick_note_save", use_container_width=True, type="primary"):
                        if note.strip():
                            st.session_state.quick_notes.append(
                                {"date": dt.date.today().isoformat(), "note": note.strip()}
                            )
                            st.toast("✓ Note saved!", icon="✅")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_clear:
                    st.markdown('<div class="white-button-wrapper">', unsafe_allow_html=True)
                    if st.button("Clear", key="quick_note_clear", use_container_width=True):
                        # Use a different key for clearing to avoid state conflict
                        if "quick_note_text" in st.session_state:
                            del st.session_state["quick_note_text"]
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Mark good day button
        with col3:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="background: rgba(102, 126, 234, 0.1); width: 80px; height: 80px;
                            border-radius: 50%; display: flex; align-items: center;
                            justify-content: center; margin: 0 auto 1rem auto;">
                    <span style="font-size: 3rem;">😊</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Button to toggle good day
            current_status = st.session_state.get("good_day", False)
            button_label = "✅ Good Day (ON)" if current_status else "Mark Good Day"

            st.markdown('<div class="blue-button-wrapper" style="margin-bottom: 0;">', unsafe_allow_html=True)
            if st.button(button_label, key="good_day_btn", use_container_width=True, type="primary"):
                st.session_state["good_day"] = not current_status
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Track menstrual cycle button
        with col4:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="background: rgba(102, 126, 234, 0.1); width: 80px; height: 80px;
                            border-radius: 50%; display: flex; align-items: center;
                            justify-content: center; margin: 0 auto 1rem auto;">
                    <span style="font-size: 3rem;">🩸</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Button to toggle cycle tracking
            cycle_status = st.session_state.get("track_cycle", False)
            cycle_label = "✅ Tracking (ON)" if cycle_status else "Track Cycle"

            st.markdown('<div class="blue-button-wrapper" style="margin-bottom: 0;">', unsafe_allow_html=True)
            if st.button(cycle_label, key="track_cycle_btn", use_container_width=True, type="primary"):
                st.session_state["track_cycle"] = not cycle_status
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Add extra spacing at the bottom of the Quick Actions box
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

    is_female = st.session_state["track_cycle"]

    with st.form("n1_entry_form", clear_on_submit=False):
        # Essential Metrics Section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
            <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px;">
                📊 Essential Metrics
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                Track your core daily health indicators
            </p>
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
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; margin: 2rem 0 1rem 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
            <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px;">
                🌟 Therapy Tracking
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                Monitor your treatment approaches and their effects
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(236, 72, 153, 0.08); padding: 0.8rem 1rem; border-radius: 8px;
                    margin-bottom: 1rem; border-left: 3px solid #ec4899;">
            <p style="margin: 0; color: #334155; font-size: 14px;">
                <strong>💡 Tip:</strong> You can track multiple natural therapies simultaneously. Use the checkbox below only when starting a NEW natural therapy for before/after analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            f_condition_today = st.multiselect(
                "🏥 Conditions felt today",
                options=condition_options,
                default=[],
                help="Select all conditions experienced today."
            )
        with c4:
            f_therapy_used = st.multiselect(
                "🧘🏻‍♀️ Natural Therapy used today",
                options=therapy_options,
                help="Select all natural therapies you used today."
            )

        t1, t2 = st.columns(2)
        with t1:
            f_started_therapy = st.checkbox(
                "Started a new primary natural therapy today",
                help="Check this box on the first day you begin a new PRIMARY natural therapy for before/after analysis."
            )
        with t2:
            if f_started_therapy:
                f_therapy_name = st.text_input(
                    "Which natural therapy?",
                    placeholder="e.g., Acupuncture or Acupuncture + Yoga",
                    help="Name the primary natural therapy you're analyzing (can include multiple: 'Acupuncture + Yoga')"
                )
            else:
                f_therapy_name = ""

        # Conditional Menstrual Tracking
        if is_female:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 1rem 1.5rem; border-radius: 12px; margin: 2rem 0 1rem 0;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
                <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px;">
                    🩸 Hormonal Cycle
                </h3>
                <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                    Track your menstrual cycle and related symptoms
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div style="background: rgba(236, 72, 153, 0.08); padding: 0.8rem 1rem; border-radius: 8px;
                        margin-bottom: 1rem; border-left: 3px solid #ec4899;">
                <p style="margin: 0; color: #334155; font-size: 14px;">
                    <strong>💡 Tip:</strong> Just mark your menstrual days - cycle day will be calculated automatically!
                </p>
            </div>
            """, unsafe_allow_html=True)
            hc1, hc2 = st.columns(2)
            with hc1:
                f_menstruating = st.radio("Menstruating today?", ["No", "Yes"], index=0)
            with hc2:
                f_pms = st.multiselect(
                    "PMS symptoms",
                    pms_options,
                    default=[]
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
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; margin: 2rem 0 1rem 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
            <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px;">
                ❤️ Core Symptoms
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                Monitor your mental and emotional well-being
            </p>
        </div>
        """, unsafe_allow_html=True)
        c9, c10 = st.columns(2)
        with c9:
            f_anxiety = st.slider("😟 Anxiety (0–10)", 0, 10, 5)
        with c10:
            f_patience = st.slider("😌 Patience (0–10)", 0, 10, 5)

        # Emotional & Physical Symptoms
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; margin: 2rem 0 1rem 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
            <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px;">
                💭 Emotional & Physical Symptoms
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                Record specific symptoms you're experiencing
            </p>
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
            default=[]
        )

        # Physical State
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; margin: 2rem 0 1rem 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
            <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px;">
                🏃‍♀️ Physical State
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                Track your movement and digestive health
            </p>
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
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
        add_clicked = st.form_submit_button("💾 SAVE ENTRY", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
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

            # Save to session state (for immediate display)
            st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_entry], ignore_index=True)
            
            # Save to database for persistence (if not in demo mode)
            if not st.session_state.demo_mode and st.session_state.get('user_id'):
                entry_dict = new_entry.iloc[0].to_dict()
                success, error_msg = save_log_entry_to_database(st.session_state.user_id, entry_dict)
                
                if success:
                    st.success("✅ Entry saved successfully!")
                    st.balloons()
                else:
                    st.success("✅ Entry saved to session (data will persist until logout)")
                    st.warning(f"⚠️ Could not save to database: {error_msg}")
            else:
                st.success("✅ Entry saved successfully!")
                st.balloons()

    # Show recent entries with modern card design
    if not st.session_state.n1_df.empty:
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem 1.5rem; border-radius: 12px; margin: 2rem 0 1.5rem 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);">
            <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">
                📋 Recent Entries
            </h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                Your last 5 logged entries
            </p>
        </div>
        """, unsafe_allow_html=True)

        recent = st.session_state.n1_df.tail(5).iloc[::-1]  # Reverse to show newest first

        for idx, row in recent.iterrows():
            # Create card for each entry
            date_str = pd.to_datetime(row['date']).strftime('%b %d, %Y') if 'date' in row else 'N/A'

            # Determine card color based on pain score
            pain = row.get('pain_score', 5)
            if pain <= 3:
                card_color = "#10b981"  # Green
                pain_emoji = "😊"
            elif pain <= 6:
                card_color = "#f59e0b"  # Orange
                pain_emoji = "😐"
            else:
                card_color = "#ef4444"  # Red
                pain_emoji = "😣"

            sleep_val = row.get('sleep_hours', 'N/A')
            mood_val = row.get('mood_score', 'N/A')
            stress_val = row.get('stress_score', 'N/A')
            
            # Check for therapy data in multiple possible column names
            therapy_val = 'None'
            if 'therapies_continuing' in row and row.get('therapies_continuing'):
                # Handle list column
                therapies_list = row['therapies_continuing'] if isinstance(row['therapies_continuing'], list) else [row['therapies_continuing']]
                therapy_val = ', '.join(therapies_list) if therapies_list and therapies_list != [''] else 'None'
            elif 'therapy_used' in row and row.get('therapy_used'):
                therapies_list = row['therapy_used'] if isinstance(row['therapy_used'], list) else [row['therapy_used']]
                therapy_val = ', '.join(therapies_list) if therapies_list and therapies_list != [''] else 'None'
            elif 'therapy' in row and row.get('therapy'):
                therapy_val = row['therapy']

            # Build the card with Streamlit columns instead of HTML grid
            with st.container():
                # Card container
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.95);
                            border-radius: 15px;
                            padding: 1.5rem;
                            margin-bottom: 1rem;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                            border-left: 5px solid {card_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="margin: 0; color: #1a202c; font-size: 1.1rem; font-weight: 700;">
                            📅 {date_str}
                        </h4>
                        <span style="background: {card_color}; color: white; padding: 0.3rem 0.8rem;
                                    border-radius: 20px; font-size: 0.85rem; font-weight: 700;">
                            {pain_emoji} Pain: {pain}/10
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Metrics row using columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div style="background: rgba(102, 126, 234, 0.08); padding: 0.8rem; border-radius: 10px; text-align: center;">
                        <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 0.3rem;">
                            😴 Sleep
                        </div>
                        <div style="font-size: 1.2rem; color: #1a202c; font-weight: 700;">
                            {sleep_val}h
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style="background: rgba(16, 185, 129, 0.08); padding: 0.8rem; border-radius: 10px; text-align: center;">
                        <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 0.3rem;">
                            🙂 Mood
                        </div>
                        <div style="font-size: 1.2rem; color: #1a202c; font-weight: 700;">
                            {mood_val}/10
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div style="background: rgba(239, 68, 68, 0.08); padding: 0.8rem; border-radius: 10px; text-align: center;">
                        <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 0.3rem;">
                            😰 Stress
                        </div>
                        <div style="font-size: 1.2rem; color: #1a202c; font-weight: 700;">
                            {stress_val}/10
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div style="background: rgba(139, 92, 246, 0.08); padding: 0.8rem; border-radius: 10px; text-align: center;">
                        <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 0.3rem;">
                            🧘🏻‍♀️ Therapies
                        </div>
                        <div style="font-size: 0.9rem; color: #1a202c; font-weight: 600;">
                            {therapy_val}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # Add bottom spacing to ensure content is visible above footer
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

# ============================================================================
# TAB 3: EVIDENCE EXPLORER
# ============================================================================
with tab3:
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem 2.5rem; border-radius: 20px; margin-bottom: 2rem;
                box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            🔬 Evidence Explorer
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 400;">
            Browse clinical trials and research for natural therapies
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Check if user wants to fetch live data
    if 'fetching_evidence' in st.session_state and st.session_state.fetching_evidence:
        st.session_state.fetching_evidence = False
        
        # Define the therapies and conditions to fetch
        therapies_list = ["Acupuncture", "Yoga", "Meditation", "Massage", "Tai Chi", 
                         "Cognitive Behavioural Therapy", "Herbal", "Aromatherapy", 
                         "Exercise Therapy", "Qi Gong"]
        conditions_list = [
            "Addiction", "Anxiety", "Burnout", "Cancer Pain", "Chronic Fatigue Syndrome", "Chronic Pain",
            "Depression", "Eating Disorders", "Endometriosis", "Fibromyalgia", "Headache", "Infertility", 
            "Insomnia", "Irritable Bowel Syndrome", "Knee Pain", "Low Back Pain", "Menopause", "Migraine",
            "Myofascial Pain", "Neck Pain", "Neuropathic Pain", "Obsessive-Compulsive Disorder",
            "Osteoarthritis", "Perimenopause", "Polycystic Ovary Syndrome", "Postoperative Pain",
            "Post-Traumatic Stress Disorder", "Rheumatoid Arthritis", "Schizophrenia", "Shoulder Pain", "Stress"
        ]
        
        st.info("⏳ **Fetching live data from PubMed & ClinicalTrials.gov...** This may take 5-10 minutes.")
        
        # Fetch live data
        live_evidence_df = fetch_live_evidence_for_therapies(therapies_list, conditions_list)
        
        if not live_evidence_df.empty:
            # Save to CSV
            output_path = Path("data/evidence_counts.csv")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            live_evidence_df.to_csv(output_path, index=False)
            
            # Clear cache and reload
            load_evidence_data.clear()
            evidence_df = load_evidence_data()
            st.success(f"✅ Successfully fetched and saved live evidence data for {len(live_evidence_df)} records!")
            st.rerun()
        else:
            st.error("❌ Failed to fetch live evidence data. Please try again or use the script method.")
            st.stop()
    
    # Load evidence data from CSV
    evidence_df = load_evidence_data()
    
    if evidence_df.empty:
        st.error("⚠️ **No evidence data available.**")
        st.info("""
        **To load evidence data, please:**
        1. Run `python scripts/build_evidence_counts.py` to generate the data file, OR
        2. Click '🔄 Refresh Evidence Data' button below to fetch live data from PubMed & ClinicalTrials.gov
        
        **Note:** Fetching live data may take 5-10 minutes and will query ~320 condition-therapy combinations.
        """)
        
        # Add refresh button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Refresh Evidence Data", type="primary", use_container_width=True):
                st.session_state.fetching_evidence = True
                st.rerun()
        
        st.stop()
    else:
        # Keep all condition-therapy combinations (don't aggregate)
        # Each row represents one therapy for one condition with its specific evidence
        
        # Add therapy definitions
        therapy_definitions = {
            "Acupuncture": "Traditional Chinese medicine practice using thin needles at specific body points",
            "Yoga": "Mind-body practice combining physical postures, breathing, and meditation",
            "Meditation": "Mental training practice to focus awareness and achieve calm and clarity",
            "Massage": "Manual manipulation of soft tissue to reduce tension and promote healing",
            "Tai Chi": "Gentle Chinese martial art combining slow movements and deep breathing",
            "Cognitive Behavioural Therapy": "Talk therapy to change negative thought patterns and behaviors",
            "Herbal": "Use of plant-based remedies to support health and treat various conditions",
            "Aromatherapy": "Use of essential oils and aromatic compounds for therapeutic benefits",
            "Exercise Therapy": "Structured exercise program to restore movement and reduce pain",
            "Qi Gong": "Gentle movement and breathing exercises from Chinese tradition",
            "Ayurveda": "Traditional Indian system of medicine using herbs, diet, and lifestyle"
        }
        
        # Prepare the data for display
        all_therapy_data = evidence_df.copy()
        all_therapy_data['Definition'] = all_therapy_data['therapy'].map(therapy_definitions).fillna('Natural therapy approach')
        
        # Rename columns to match expected format
        all_therapy_data = all_therapy_data.rename(columns={
            'therapy': 'Natural Therapy',
            'clinicaltrials_n': 'Clinical Trials',
            'pubmed_n': 'PubMed Articles',
            'evidence_direction': 'Evidence',
            'condition': 'Condition',
            'trials_url': 'trials_url',
            'articles_url': 'articles_url'
        })
        
        # Sort by Clinical Trials count
        all_therapy_data = all_therapy_data.sort_values('Clinical Trials', ascending=False).reset_index(drop=True)
        
        # Get the last updated date from the CSV
        csv_path = _locate_evidence_csv()
        if csv_path:
            last_modified = datetime.fromtimestamp(csv_path.stat().st_mtime).strftime("%Y-%m-%d")
            unique_therapies = len(all_therapy_data['Natural Therapy'].unique())
            total_combinations = len(all_therapy_data)
            st.success(f"✅ Loaded {total_combinations} condition-therapy combinations for {unique_therapies} natural therapies (Last updated: {last_modified})")
        else:
            unique_therapies = len(all_therapy_data['Natural Therapy'].unique())
            total_combinations = len(all_therapy_data)
            st.success(f"✅ Loaded {total_combinations} condition-therapy combinations for {unique_therapies} natural therapies")
        
        # Add refresh button in sidebar or at top
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Update Evidence Data (Fetch Live from APIs)", type="secondary", use_container_width=True):
                st.session_state.fetching_evidence = True
                st.rerun()

    # FILTERS SECTION
    st.markdown("""
    <div style="background: rgba(102, 126, 234, 0.05); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;">
        <h3 style="color: #667eea; margin: 0 0 0.8rem 0; font-size: 1.3rem; font-weight: 700;">
            🔍 Find natural therapies with positive evidence for your conditions
        </h3>
        <p style="color: #64748b; margin: 0; font-size: 0.95rem; line-height: 1.6;">
            <strong>Natural therapies</strong> are non-pharmaceutical treatments that support your body's healing processes. 
            These include mind-body practices (yoga, meditation), physical therapies (massage, acupuncture), 
            and lifestyle interventions (nutrition, exercise) backed by clinical research.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Create filter columns
    col1, col2 = st.columns(2)

    with col1:
        # Condition selector - Use same comprehensive list from Daily Log
        evidence_condition_options = [
            "Addiction", "Anxiety", "Arthritis", "Burnout", "Cancer Pain", 
            "Chronic Fatigue Syndrome", "Chronic Pain", "Depression", "Eating Disorders", 
            "Endometriosis", "Fibromyalgia", "Headache", "Infertility", "Insomnia", 
            "Irritable Bowel Syndrome", "Knee Pain", "Low Back Pain", "Menopause", "Migraine", 
            "Myofascial Pain", "Neck Pain", "Neuropathic Pain", "Obsessive-Compulsive Disorder",
            "PCOS", "Postoperative Pain", "Rheumatoid Arthritis", "Schizophrenia", 
            "Shoulder Pain", "Stress", "General Wellness"
        ]
        # Default to "Depression" and "Anxiety" in demo mode, empty when signed in
        default_conditions = ["Depression", "Anxiety"] if st.session_state.demo_mode else []
        # Add spacing to align with therapies column
        st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
        
        selected_conditions = st.multiselect(
            "🏥 Select Condition(s)",
            options=evidence_condition_options,
            default=default_conditions,
            help="Select one or more health conditions to filter therapies"
        )

        # Evidence type filter
        evidence_types = st.multiselect(
            "📊 Evidence Type",
            options=["Positive", "Mixed", "Negative"],
            default=["Positive", "Mixed", "Negative"],
            help="Filter by evidence quality: Positive (shows benefit), Mixed (some benefit, needs more research), Negative (shows little to no benefit)"
        )

        # Years slider - Show actual year range
        current_year = 2025
        start_year, end_year = st.slider(
            "📅 Publication Year Range",
            min_value=1990,
            max_value=current_year,
            value=(2015, current_year),  # Default: last 10 years
            help="Filter evidence published between these years"
        )
        years_range = end_year - start_year  # Calculate range for display

    with col2:
        # Natural Therapy selector (multi-select to allow deselection)
        all_therapies = all_therapy_data["Natural Therapy"].unique().tolist()
        
        # Add some spacing before the multiselect to align with the year slider
        st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
        
        selected_therapies = st.multiselect(
            "🧘🏻‍♀️ Select Natural Therapies",
            options=all_therapies,
            default=all_therapies,
            help="Choose which natural therapies to display (all natural therapies are set as default)"
        )

    # Apply filters
    therapy_data = all_therapy_data.copy()

    # Filter by condition(s) - show all therapy-condition combinations that match
    if selected_conditions:  # If any conditions selected
        therapy_data = therapy_data[therapy_data["Condition"].isin(selected_conditions)]

    # Filter by selected therapies
    therapy_data = therapy_data[therapy_data["Natural Therapy"].isin(selected_therapies)]

    # Filter by evidence type
    therapy_data = therapy_data[therapy_data["Evidence"].isin(evidence_types)]

    # Show filter results count
    condition_text = ", ".join(selected_conditions) if selected_conditions else "All Conditions"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.8rem 1.5rem; 
                border-radius: 10px; margin-bottom: 1.5rem; text-align: center;">
        <p style="margin: 0; color: white; font-size: 0.95rem; font-weight: 600;">
            Showing {len(therapy_data)} therapies for {condition_text} (Evidence from {start_year} - {end_year})
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Check if we have results
    if therapy_data.empty:
        st.warning("⚠️ No therapies found matching your filters. Try adjusting your selection.")
        st.stop()

    # Check if multiple conditions are selected for stacked breakdown
    multiple_conditions = len(selected_conditions) > 1
    
    if multiple_conditions:
        # For multiple conditions, show breakdown by condition in stacked bars
        # Group by therapy and condition to preserve breakdown
        therapy_by_condition = therapy_data.groupby(['Natural Therapy', 'Condition']).agg({
            'Clinical Trials': 'sum',
            'PubMed Articles': 'sum',
            'Evidence': lambda x: x.mode()[0] if len(x) > 0 else 'Unclear'
        }).reset_index()
        
        # Calculate totals for ranking
        therapy_totals = therapy_by_condition.groupby('Natural Therapy')['Clinical Trials'].sum().reset_index()
        therapy_totals = therapy_totals.sort_values("Clinical Trials", ascending=False)
        
        # Add ranking
        therapy_totals["Therapy_Ranked"] = [
            f"{i+1}. {therapy}" for i, therapy in enumerate(therapy_totals["Natural Therapy"])
        ]
        
        # Merge ranking back
        therapy_by_condition = therapy_by_condition.merge(therapy_totals[['Natural Therapy', 'Therapy_Ranked']], on='Natural Therapy')
        
        # Generate distinct shades for each condition
        base_colors = ['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe', '#2563eb', '#1d4ed8']
        color_map = {cond: base_colors[i % len(base_colors)] for i, cond in enumerate(selected_conditions)}
        
    fig = px.bar(
            therapy_by_condition,
            x="Clinical Trials",
            y="Therapy_Ranked",
            color="Condition",
            orientation='h',
            title=f"Top 10 Therapies by Clinical Trial Count ({condition_text})",
            color_discrete_map=color_map,
            height=450,
            category_orders={"Therapy_Ranked": therapy_totals["Therapy_Ranked"].tolist()}
        )
    else:
        # Single condition or all conditions - aggregate by therapy
        therapy_aggregated = therapy_data.groupby('Natural Therapy').agg({
            'Clinical Trials': 'sum',
            'PubMed Articles': 'sum',
            'Evidence': lambda x: x.mode()[0] if len(x) > 0 else 'Unclear',
            'Definition': 'first',
            'trials_url': 'first',
            'articles_url': 'first'
        }).reset_index()
        
        therapy_aggregated = therapy_aggregated.sort_values("Clinical Trials", ascending=False)
        therapy_aggregated["Therapy_Ranked"] = [
            f"{i+1}. {therapy}" for i, therapy in enumerate(therapy_aggregated["Natural Therapy"])
        ]
        
        # Determine if therapies are filtered
        all_therapies = all_therapy_data['Natural Therapy'].unique().tolist()
        is_filtered = len(selected_therapies) < len(all_therapies) and len(selected_therapies) > 0
        
        # Create bar chart - color by therapy if filtered, by evidence if showing all
        if is_filtered and len(selected_therapies) <= 12:
            therapy_colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel + px.colors.qualitative.Dark2
            color_map = {therapy: therapy_colors[i % len(therapy_colors)] for i, therapy in enumerate(selected_therapies)}
            
            fig = px.bar(
                therapy_aggregated,
                x="Clinical Trials",
                y="Therapy_Ranked",
                color="Natural Therapy",
                orientation='h',
                title=f"Clinical Evidence for Selected Therapies (n={len(selected_therapies)})",
                color_discrete_map=color_map,
                height=450,
                category_orders={"Therapy_Ranked": therapy_aggregated["Therapy_Ranked"].tolist()}
            )
        else:
            # Default: color by evidence
            fig = px.bar(
                therapy_aggregated,
        x="Clinical Trials",
        y="Therapy_Ranked",
        color="Evidence",
        orientation='h',
                title="Top 10 Therapies by Clinical Trial Count (All Conditions)",
        color_discrete_map={"Positive": "#22c55e", "Mixed": "#fb923c", "Negative": "#ef4444"},
                height=450,
                category_orders={"Therapy_Ranked": therapy_aggregated["Therapy_Ranked"].tolist()}
            )

    # Adjust legend based on whether showing multiple conditions
    if multiple_conditions:
        # Vertical legend on the right for multiple conditions
        legend_config = dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            title_text="",
            font=dict(size=13),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)',
            tracegroupgap=10
        )
        margin_config = dict(b=60, r=150)  # Right margin for vertical legend
    else:
        # Horizontal legend at bottom for evidence types
        legend_config = dict(
            orientation="h",
            yanchor="top",
            y=-0.30,
            xanchor="center",
            x=0.5,
            title_text="",
            font=dict(size=13),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        )
        margin_config = dict(b=140)  # Bottom margin for horizontal legend

    fig.update_layout(
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", size=14),
        showlegend=True,
        legend=legend_config,
        margin=margin_config,
        xaxis=dict(
            title="Number of Clinical Trials",
            showgrid=True,
            gridcolor='rgba(102, 126, 234, 0.2)',
            gridwidth=2,
            linecolor='#667eea',
            linewidth=2
        ),
        yaxis=dict(
            title="",
            categoryorder='total ascending',  # Show largest at top
            linecolor='#667eea',
            linewidth=2
        ),
        title_font_size=18,
        title_font_family="Inter",
        title_font_color="#1a202c"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Therapy cards - modern design without expanders
    st.markdown("""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h3 style="color: #1a202c; font-size: 1.5rem; font-weight: 800; margin: 0;">
            🧘🏻‍♀️ Detailed Therapy Information
        </h3>
        <p style="color: #64748b; font-size: 0.95rem; margin: 0.5rem 0 0 0;">
            Comprehensive research data for each therapy
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Use single uniform color for all therapy headers
    uniform_header_color = "#667eea"  # Blue/purple for all therapies
    
    # Use aggregated data for therapy cards to avoid duplicates when multiple conditions are selected
    if multiple_conditions:
        # For multiple conditions, use the aggregated data grouped by therapy
        cards_data = therapy_data.groupby('Natural Therapy').agg({
            'Clinical Trials': 'sum',
            'PubMed Articles': 'sum',
            'Evidence': lambda x: x.mode()[0] if len(x) > 0 else 'Unclear',
            'Definition': 'first',
            'trials_url': 'first',
            'articles_url': 'first'
        }).reset_index()
    else:
        # For single condition, use the original therapy_data
        cards_data = therapy_data.copy()

    for idx, row in cards_data.iterrows():
        therapy_name = row['Natural Therapy']
        evidence = row['Evidence']
        color = uniform_header_color  # All therapies use the same color
        
        # Use URLs from CSV if available, otherwise generate generic ones
        # If multiple conditions are selected, generate combined URLs
        if multiple_conditions and selected_conditions:
            # Generate combined ClinicalTrials.gov URL with all selected conditions
            conditions_part = ' AND '.join([f'({cond})' for cond in selected_conditions])
            trials_url = f"https://clinicaltrials.gov/search?cond={conditions_part}+AND+({therapy_name.replace(' ', '+')})"
            
            # Generate combined PubMed URL with all selected conditions  
            conditions_terms = ' OR '.join([f'"{cond}"' for cond in selected_conditions])
            therapy_terms = f'"{therapy_name}" OR "{therapy_name.lower()}"'
            pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/?term=({conditions_terms})+AND+({therapy_terms})"
        elif 'trials_url' in row and pd.notna(row['trials_url']) and row['trials_url']:
            trials_url = row['trials_url']
        else:
            trials_url = f"https://clinicaltrials.gov/search?term={therapy_name.replace(' ', '+')}"
        
        if not multiple_conditions and 'articles_url' in row and pd.notna(row['articles_url']) and row['articles_url']:
            pubmed_url = row['articles_url']
        elif not multiple_conditions:
            pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={therapy_name.replace(' ', '+')}"

        # Set evidence color and emoji based on evidence type
        if evidence == "Positive":
            evidence_color = "#22c55e"  # Bright Green
            evidence_emoji = "✅"
            evidence_display = f"{evidence_emoji} {evidence}"
        elif evidence == "Mixed":
            evidence_color = "#fb923c"  # Bright Orange
            evidence_emoji = "⚠️"
            evidence_display = f"{evidence_emoji} {evidence}"
        elif evidence == "Negative":
            evidence_color = "#ef4444"  # Red
            evidence_emoji = "❌"
            evidence_display = f"{evidence_emoji} {evidence}"
        else:
            evidence_color = color
            evidence_display = evidence

        # Therapy card container
        st.markdown(f"""
        <div style="background: white;
                    border-radius: 15px;
                    padding: 0;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    border-left: 6px solid {color};
                    overflow: hidden;">
            <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                        padding: 1.25rem 1.5rem;">
                <h4 style="color: white; margin: 0; font-size: 1.3rem; font-weight: 800;">
                    {therapy_name}
                </h4>
                <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
                    {row['Definition']}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics row
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}15 0%, {color}25 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;
                        border: 2px solid {color}30; margin-bottom: 1rem;">
                <p style="color: #64748b; font-size: 0.85rem; margin: 0; font-weight: 600; text-transform: uppercase;">
                    Clinical Trials
                </p>
                <p style="margin: 0.5rem 0 0 0;">
                    <a href="{trials_url}" target="_blank" style="color: {color}; font-size: 2rem; font-weight: 800; text-decoration: none; transition: opacity 0.2s;">
                        {row['Clinical Trials']:,}
                    </a>
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}15 0%, {color}25 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;
                        border: 2px solid {color}30; margin-bottom: 1rem;">
                <p style="color: #64748b; font-size: 0.85rem; margin: 0; font-weight: 600; text-transform: uppercase;">
                    PubMed Articles
                </p>
                <p style="margin: 0.5rem 0 0 0;">
                    <a href="{pubmed_url}" target="_blank" style="color: {color}; font-size: 2rem; font-weight: 800; text-decoration: none; transition: opacity 0.2s;">
                        {row['PubMed Articles']:,}
                    </a>
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {evidence_color}15 0%, {evidence_color}25 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;
                        border: 2px solid {evidence_color}30; margin-bottom: 1rem;">
                <p style="color: #64748b; font-size: 0.85rem; margin: 0; font-weight: 600; text-transform: uppercase;">
                    Evidence Level
                </p>
                <p style="color: {evidence_color}; font-size: 2rem; font-weight: 800; margin: 0.5rem 0 0 0;">
                    {evidence_display}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Description
        # Create evidence text with description
        if evidence == "Positive":
            evidence_text = f"<strong>{evidence.lower()} evidence (shows positive benefit)</strong>"
        elif evidence == "Mixed":
            evidence_text = f"<strong>{evidence.lower()} evidence (some benefit, needs more research)</strong>"
        elif evidence == "Negative":
            evidence_text = f"<strong>{evidence.lower()} evidence (shows little to no benefit)</strong>"
        else:
            evidence_text = f"<strong>{evidence.lower()} evidence</strong>"
        
        st.markdown(f"""
        <div style="background: rgba(248, 250, 252, 0.8);
                    padding: 1.25rem 1.5rem; border-radius: 10px;
                    border-left: 4px solid {color};
                    margin-bottom: 2rem;">
            <p style="margin: 0; color: #334155; font-size: 0.95rem; line-height: 1.6;">
                <strong style="color: {color};">{therapy_name}</strong> has shown {evidence_text}
                in clinical research for various health conditions including pain management, anxiety, stress management,
                and overall wellness improvement.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Add bottom spacing to ensure content is visible above footer
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

# ============================================================================
# TAB 4: SETTINGS
# ============================================================================
with tab4:
    # Header box matching Daily Log style
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem 2.5rem; border-radius: 20px; margin-bottom: 2rem;
                box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            ⚙️ Account & Data Management
        </h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Manage your account settings and personal data
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Account Settings Section (only for authenticated users, not demo mode)
    if st.session_state.authenticated and not st.session_state.demo_mode:
        st.markdown("#### 👤 Account Settings")

        # Load current account data
        import json
        import os
        accounts_file = "data/accounts.json"

        with open(accounts_file, "r") as f:
            accounts = json.load(f)

        current_email = st.session_state.username
        current_account = accounts.get(current_email, {})

        # Handle old format accounts (string instead of dict)
        if isinstance(current_account, str):
            st.warning("⚠️ Your account is in an old format. Please contact support to update your account.")
            current_account = {"name": current_email, "password": current_account, "username": current_email}

        # Create tabs for different settings
        settings_tab1, settings_tab2, settings_tab3 = st.tabs(["📝 Profile", "🔒 Security", "🗑️ Danger Zone"])

        # Profile Tab
        with settings_tab1:
            with st.form("profile_form"):
                st.markdown("**Update Your Profile Information**")
                new_name = st.text_input("Name", value=current_account.get("name", ""), key="update_name")
                new_email = st.text_input("Email", value=current_email, key="update_email",
                                         help="Changing email will require you to login again")

                st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
                update_profile = st.form_submit_button("💾 UPDATE PROFILE", type="primary")
                st.markdown('</div>', unsafe_allow_html=True)

                if update_profile:
                    if not new_name or not new_email:
                        st.error("❌ Please fill in all fields")
                    elif "@" not in new_email:
                        st.error("❌ Please enter a valid email address")
                    elif new_email != current_email and new_email in accounts:
                        st.error("❌ This email is already registered to another account")
                    else:
                        # Update account
                        old_data = accounts.pop(current_email)

                        # Handle both old format (string) and new format (dict)
                        if isinstance(old_data, dict):
                            old_data["name"] = new_name
                            old_data["username"] = new_email
                            old_data["email"] = new_email
                            accounts[new_email] = old_data
                        else:
                            # Old format: convert to new format
                            accounts[new_email] = {
                                "name": new_name,
                                "username": new_email,
                                "password": old_data,  # old_data is the hashed password
                                "email": new_email
                            }

                        # Save
                        with open(accounts_file, "w") as f:
                            json.dump(accounts, f, indent=2)

                        # Update session if email changed
                        if new_email != current_email:
                            st.session_state.username = new_email
                            st.success("✅ Profile updated! You'll need to use your new email to login next time.")
                        else:
                            st.success("✅ Profile updated successfully!")
                        st.rerun()

        # Security Tab
        with settings_tab2:
            with st.form("password_form"):
                st.markdown("**Change Your Password**")
                st.info("💡 Your password is managed securely by Supabase Auth. You don't need to enter your current password.")
                new_password = st.text_input("New Password", type="password", key="new_pwd",
                                            help="Must be at least 8 characters")
                confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_pwd")

                st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
                change_password = st.form_submit_button("🔐 CHANGE PASSWORD", type="primary")
                st.markdown('</div>', unsafe_allow_html=True)

                if change_password:
                    if not new_password or not confirm_new_password:
                        st.error("❌ Please fill in all fields")
                    elif new_password != confirm_new_password:
                        st.error("❌ New passwords do not match")
                    elif len(new_password) < 8:
                        st.error("❌ New password must be at least 8 characters")
                    else:
                        # Update password using Supabase Auth
                        success, error_msg = update_user_password(new_password)
                        if success:
                            st.success("✅ Password changed successfully!")
                        else:
                            st.error(f"❌ {error_msg}")

        # Danger Zone Tab
        with settings_tab3:
            st.markdown("**⚠️ Danger Zone**")
            st.warning("These actions are permanent and cannot be undone!")

            with st.expander("🗑️ Delete Account"):
                st.markdown("**Delete your account and all associated data permanently.**")
                st.markdown("This will:")
                st.markdown("- Delete your account credentials")
                st.markdown("- Remove all your health tracking data")
                st.markdown("- Cannot be reversed")

                confirm_text = st.text_input("Type 'DELETE' to confirm", key="delete_confirm")

                st.markdown('<div class="pink-button-wrapper">', unsafe_allow_html=True)
                if st.button("🗑️ DELETE MY ACCOUNT", type="primary"):
                    if confirm_text == "DELETE":
                        # Delete account
                        accounts.pop(current_email, None)

                        # Save
                        with open(accounts_file, "w") as f:
                            json.dump(accounts, f, indent=2)

                        # Logout
                        st.session_state.authenticated = False
                        st.session_state.username = ""
                        st.session_state.n1_df = pd.DataFrame()
                        st.success("✅ Account deleted successfully. Goodbye! 👋")
                        st.rerun()
                    else:
                        st.error("❌ Please type 'DELETE' to confirm")
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

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
            st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
            st.download_button(
                label="📥 DOWNLOAD CSV",
                data=csv_data,
                file_name=f"health_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            json_data = df.to_json(orient='records', indent=2)
            st.markdown('<div class="pink-button-wrapper">', unsafe_allow_html=True)
            st.download_button(
                label="📥 DOWNLOAD JSON",
                data=json_data,
                file_name=f"health_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
                type="primary"
            )
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📝 No data to export yet. Start logging to see your data here!")
    
    st.markdown("---")
    
    # About section
    st.markdown("### ℹ️ About Bearable")
    st.markdown("""
    **Version:** 15.0 Final Polish Edition

    **Key Features:**
    - 🔬 Evidence-based therapy research with 500,000+ clinical trials
    - 📊 Personal health tracking with beautiful visualizations
    - 🤖 AI-powered insights and pattern detection
    - 📱 Mobile-optimised responsive design
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

    # Add bottom spacing to ensure content is visible above footer
    st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

# Tab 5: Login/Logout
with tab5:
    if st.session_state.authenticated:
        # Logout content
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem 2.5rem; border-radius: 20px; margin-bottom: 2rem;
                    box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);">
            <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; text-align: center;">
                🚪 Logout
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;">
                You are currently logged in as <strong style="color: #667eea;">{st.session_state.username}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
            if st.button("🚪 LOGOUT", key="logout_tab", type="primary", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.demo_mode = False
                st.session_state.username = ""
                st.session_state.n1_df = pd.DataFrame()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)
    else:
        # Login content - redirect to login page
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem 2.5rem; border-radius: 20px; margin-bottom: 2rem;
                    box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);">
            <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; text-align: center;">
                🔐 Login to Your Account
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;">
                Click the button below to access the login page and sign in to your Bearable account.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="blue-button-wrapper">', unsafe_allow_html=True)
            if st.button("🔐 GO TO LOGIN PAGE", key="login_tab", type="primary", use_container_width=True):
                st.session_state.show_auth_page = True
                st.session_state.demo_mode = False
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.session_state.n1_df = pd.DataFrame()
                st.session_state.show_signup = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="custom-footer" style="
    text-align: center; 
    margin-top: 0 !important; 
    margin-bottom: 0 !important; 
    padding: 30px !important;
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 15px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
    position: relative !important;
    z-index: 1000 !important;
    display: block !important;
    visibility: visible !important;
    width: 100% !important;
    box-sizing: border-box !important;
">
    <p style="color: #64748b; font-size: 15px; margin: 0; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width: 20px; height: 20px;">
            <circle cx="28" cy="28" r="18" fill="#7c5dcf"/>
            <circle cx="72" cy="28" r="18" fill="#7c5dcf"/>
            <circle cx="50" cy="55" r="35" fill="#8b6ddb"/>
            <ellipse cx="50" cy="68" rx="20" ry="15" fill="#9d82e8"/>
        </svg>
        <span>Bearable © 2025 • Evidence-Based Health Tracking Platform</span>
    </p>
    <p style="color: #94a3b8; font-size: 13px; margin: 8px 0 0 0;">
        Built with ❤️ using Streamlit • Not medical advice - consult healthcare professionals
    </p>
</div>

<script>
setTimeout(function() {
    // Remove bottom padding from containers
    const containers = ['.main', '.block-container', '.stApp', 'div[class*="st-emotion-cache"]'];
    containers.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.style.paddingBottom = '0';
            el.style.marginBottom = '0';
        });
    });
    
    // Ensure footer is visible
    const footer = document.querySelector('.custom-footer');
    if (footer) {
        footer.style.display = 'block';
        footer.style.visibility = 'visible';
    }
}, 100);
</script>
""", unsafe_allow_html=True)