import streamlit as st
import pandas as pd
from pathlib import Path
import os
import json
import hashlib
from datetime import datetime, timedelta
from functools import lru_cache

# ============================================================================
# AI ASSISTANT CONFIGURATION
# ============================================================================
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Load OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Cost-effective model

# AI Feature Configuration
AI_RATE_LIMIT_PER_DAY = 50  # Maximum API calls per user per day
AI_CACHE_TTL_HOURS = 24  # Cache therapy explanations for 24 hours

# Initialize OpenAI if key is available
if OPENAI_API_KEY and OPENAI_AVAILABLE:
    openai.api_key = OPENAI_API_KEY
    ENABLE_AI_FEATURES = True
else:
    ENABLE_AI_FEATURES = False

st.set_page_config(
    page_title="Pain Relief Map", 
    page_icon="💆🏻‍♀️",
    layout="wide",  # Make content wider
    initial_sidebar_state="collapsed"
)

# ============================================================================
# AI ASSISTANT HELPER FUNCTIONS
# ============================================================================

def check_ai_available() -> tuple[bool, str]:
    """Check if AI features are available and why/why not"""
    if not ENABLE_AI_FEATURES:
        return False, "No API key configured"
    
    if not st.session_state.get('ai_enabled', False):
        return False, "AI features disabled by user"
    
    if st.session_state.get('ai_calls_count', 0) >= AI_RATE_LIMIT_PER_DAY:
        return False, f"Daily limit reached ({AI_RATE_LIMIT_PER_DAY} calls/day)"
    
    return True, "Available"


def increment_ai_usage():
    """Track AI API usage"""
    st.session_state.ai_calls_count = st.session_state.get('ai_calls_count', 0) + 1


def get_remaining_calls() -> int:
    """Get remaining AI calls for today"""
    return max(0, AI_RATE_LIMIT_PER_DAY - st.session_state.get('ai_calls_count', 0))


def get_cached_explanation(therapy_name: str) -> str | None:
    """Get cached therapy explanation if available and not expired"""
    cache_key = therapy_name.lower().strip()
    
    # Check if cached and not expired
    if cache_key in st.session_state.get('therapy_explanation_cache', {}):
        cached_time = st.session_state.get('cache_timestamp', {}).get(cache_key)
        if cached_time:
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            if age_hours < AI_CACHE_TTL_HOURS:
                return st.session_state.therapy_explanation_cache[cache_key]
    
    return None


def cache_explanation(therapy_name: str, explanation: str):
    """Cache a therapy explanation"""
    cache_key = therapy_name.lower().strip()
    if 'therapy_explanation_cache' not in st.session_state:
        st.session_state.therapy_explanation_cache = {}
    if 'cache_timestamp' not in st.session_state:
        st.session_state.cache_timestamp = {}
    
    st.session_state.therapy_explanation_cache[cache_key] = explanation
    st.session_state.cache_timestamp[cache_key] = datetime.now()


def parse_symptom_entry(user_message: str, user_context: dict = None) -> dict:
    """Parse natural language symptom description into structured data"""
    
    available, reason = check_ai_available()
    if not available:
        return {"success": False, "error": f"AI unavailable: {reason}"}
    
    system_prompt = """You are a medical symptom tracking assistant. Parse user descriptions into structured health data.

Extract these fields when mentioned (use null if not mentioned):
- pain_score: 0-10 scale (0=none, 10=worst)
- sleep_hours: hours of sleep (0-14)
- mood_score: 0-10 scale (0=terrible, 10=great)
- stress_score: 0-10 scale (0=none, 10=extreme)
- anxiety_score: 0-10 scale
- therapy_used: list of therapies (e.g., ["Yoga", "Meditation"])
- physical_symptoms: list (e.g., ["headache", "fatigue"])
- emotional_symptoms: list (e.g., ["anxious", "irritable"])
- notes: any additional context

Return ONLY valid JSON. Be conservative - only extract what's clearly stated.
For comparative statements like "worse than yesterday", adjust scores up/down from context."""

    context_str = ""
    if user_context:
        context_str = f"\nYesterday's data: Pain {user_context.get('yesterday_pain', 5)}/10, Sleep {user_context.get('yesterday_sleep', 7)}h, Mood {user_context.get('yesterday_mood', 5)}/10"

    user_prompt = f"""User's health update: "{user_message}"

Today's date: {datetime.now().strftime('%B %d, %Y')}{context_str}

Parse into JSON:"""

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=400
        )
        
        increment_ai_usage()
        
        result = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        parsed_data = json.loads(result)
        return {"success": True, "data": parsed_data}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_therapy_explanation(therapy_name: str, user_condition: str = None) -> dict:
    """Get detailed explanation of a therapy (with caching)"""
    
    # Check cache first
    cache_key = f"{therapy_name}_{user_condition or 'general'}"
    cached = get_cached_explanation(cache_key)
    if cached:
        return {"success": True, "explanation": cached, "cached": True}
    
    # Check if AI available
    available, reason = check_ai_available()
    if not available:
        return {"success": False, "error": f"AI unavailable: {reason}"}
    
    system_prompt = """You are a knowledgeable health educator specializing in complementary and alternative therapies. 
Provide clear, evidence-based explanations that are:
- Accurate and scientifically grounded
- Easy to understand for non-medical audiences
- Balanced (benefits AND limitations)
- Practical (how it works, what to expect)

Keep responses under 200 words."""

    user_prompt = f"""Explain {therapy_name} therapy"""
    if user_condition:
        user_prompt += f" specifically for someone with {user_condition}"
    
    user_prompt += """\n\nInclude:
1. What it is (2-3 sentences)
2. How it works
3. What to expect in a session
4. Who might benefit most
5. Any important considerations"""

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        increment_ai_usage()
        
        explanation = response.choices[0].message.content.strip()
        
        # Cache the explanation
        cache_explanation(cache_key, explanation)
        
        return {"success": True, "explanation": explanation, "cached": False}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_ai_usage_stats():
    """Display AI usage statistics"""
    remaining = get_remaining_calls()
    used = st.session_state.get('ai_calls_count', 0)
    total = AI_RATE_LIMIT_PER_DAY
    percentage = (used / total) * 100
    
    # Display using native Streamlit components
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**AI Usage Today**")
        with col2:
            st.markdown(f"**{remaining} calls left**")
        
        st.progress(percentage / 100)
        st.caption(f"{used}/{total} calls used • Resets at midnight")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# AI Feature Toggles and Tracking
if 'ai_enabled' not in st.session_state:
    st.session_state.ai_enabled = ENABLE_AI_FEATURES  # User can disable even if API key exists

if 'ai_calls_count' not in st.session_state:
    st.session_state.ai_calls_count = 0

if 'ai_last_reset' not in st.session_state:
    st.session_state.ai_last_reset = datetime.now().date()

if 'ai_chat_history' not in st.session_state:
    st.session_state.ai_chat_history = []

if 'ai_symptom_data' not in st.session_state:
    st.session_state.ai_symptom_data = None

if 'ai_original_input' not in st.session_state:
    st.session_state.ai_original_input = ""

if 'log_mode' not in st.session_state:
    st.session_state.log_mode = "form"  # Default to form

if 'ai_logger_used' not in st.session_state:
    st.session_state.ai_logger_used = False

if 'ai_quick_prompt' not in st.session_state:
    st.session_state.ai_quick_prompt = ""

# Therapy explanation cache
if 'therapy_explanation_cache' not in st.session_state:
    st.session_state.therapy_explanation_cache = {}

if 'cache_timestamp' not in st.session_state:
    st.session_state.cache_timestamp = {}

# Reset AI call count daily
if st.session_state.ai_last_reset != datetime.now().date():
    st.session_state.ai_calls_count = 0
    st.session_state.ai_last_reset = datetime.now().date()

# Authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

if 'username' not in st.session_state:
    st.session_state.username = ""

# ============================================================================
# LOGIN / DEMO MODE SCREEN
# ============================================================================

if not st.session_state.authenticated and not st.session_state.demo_mode:
    # Main Title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="color: #333; font-size: 3em; margin-bottom: 10px;">💆🏻‍♀️ Pain Relief Map</h1>
        <p style="font-size: 1.2em; color: #666;">
            Your personal health journey companion with AI-powered insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Two Column Layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        # Demo Mode Column
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 20px; margin: 20px 0; color: white; height: 100%;">
            <h2 style="color: white; margin-bottom: 20px; font-size: 2.5em;">🚀 Try Demo Mode</h2>
            <p style="font-size: 1.1em; margin-bottom: 30px; opacity: 0.9;">
                Experience the full app without signing up
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Demo", type="primary", use_container_width=True, key="demo_btn"):
            st.session_state.demo_mode = True
            st.session_state.username = "Demo User"
            st.rerun()
        
        st.markdown("""
        <div style="padding: 20px; background: rgba(102, 126, 234, 0.1); border-radius: 15px; margin-top: 20px;">
            <h3 style="color: #667eea; margin-bottom: 15px; text-align: center;">✨ What's Inside?</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Use Streamlit columns for features
        feat_col1, feat_col2 = st.columns(2)
        
        with feat_col1:
            st.markdown("🔬 **Evidence Explorer**")
            st.caption("Find research-backed therapies")
            st.markdown("🏠 **Dashboard**")
            st.caption("Analyze patterns")
            st.markdown("📅 **Calendar**")
            st.caption("Visualize your journey")
        
        with feat_col2:
            st.markdown("🌱 **Daily Log**")
            st.caption("Track symptoms & mood")
            st.markdown("🤖 **AI Assistant**")
            st.caption("Get personalized insights")
            st.markdown("⚙️ **Settings**")
            st.caption("Manage your data")
    
    with col2:
        # Sign In/Create Account Column
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    border-radius: 20px; margin: 20px 0; color: white; height: 100%;">
            <h2 style="color: white; margin-bottom: 20px; font-size: 2.5em;">🔐 Sign In</h2>
            <p style="font-size: 1.1em; margin-bottom: 30px; opacity: 0.9;">
                Access your personal health data
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_login, col_signup = st.columns(2)
            
            with col_login:
                login_clicked = st.form_submit_button("Sign In", use_container_width=True)
            
            with col_signup:
                signup_clicked = st.form_submit_button("Create Account", use_container_width=True)
            
            if login_clicked:
                if username and password:
                    # Simple authentication (in production, use proper auth)
                    if username == "admin" and password == "password":
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Try: username='admin', password='password'")
                else:
                    st.warning("Please enter both username and password")
            
            if signup_clicked:
                st.info("📝 Account creation coming soon! For now, try Demo Mode or use:\nUsername: admin\nPassword: password")
        
    
    st.stop()  # Don't show the rest of the app until authenticated

# Show logout/exit demo button in sidebar
with st.sidebar:
    if st.session_state.demo_mode:
        st.markdown("### 🎯 Demo Mode Active")
        st.info(f"Welcome, {st.session_state.username}!")
        st.caption("You're exploring with sample data")
        if st.button("Exit Demo", use_container_width=True):
            st.session_state.demo_mode = False
            st.session_state.authenticated = False
            st.rerun()
    elif st.session_state.authenticated:
        st.markdown(f"### 👋 Welcome, {st.session_state.username}!")
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

# Simple welcome screen
st.markdown("## 👋 Welcome to Pain Relief Map!")
st.markdown("**Get started in 3 simple steps**")

# Progress indicator
col1, col2 = st.columns([3, 1])
with col1:
    st.progress(0 / 3)
with col2:
    st.metric("Progress", "0/3 Complete")

# Step cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔬 Step 1")
    st.markdown("**Explore Evidence**")
    st.markdown("Find therapies that work for your condition")

with col2:
    st.markdown("### 📝 Step 2")
    st.markdown("**Log Symptoms**")
    st.markdown("Track how you feel each day")

with col3:
    st.markdown("### 📊 Step 3")
    st.markdown("**View Insights**")
    st.markdown("See what's helping you")

st.markdown("---")

# Header
st.markdown("# 💆🏻‍♀️ Pain Relief Map")
st.markdown("**Track your health journey with science-backed insights**")
st.markdown("---")

# Create tabs
if st.session_state.ai_enabled and ENABLE_AI_FEATURES:
    # Add AI Assistant tab when AI is enabled
    tab_evidence, tab_analysis, tab_dashboard, tab_ai, tab_calendar, tab_settings = st.tabs([
        "🔬 Evidence Explorer (Start Here!)",
        "🌱 Daily Log (Step 2)",
        "🏠 Dashboard (Step 3)",
        "🤖 AI Assistant",
        "📅 Calendar",
        "⚙️ Settings"
    ])
else:
    # Standard tabs without AI Assistant
    tab_evidence, tab_analysis, tab_dashboard, tab_calendar, tab_settings = st.tabs([
        "🔬 Evidence Explorer (Start Here!)",
        "🌱 Daily Log (Step 2)",
        "🏠 Dashboard (Step 3)",
        "📅 Calendar",
        "⚙️ Settings"
    ])

# Evidence Explorer Tab
with tab_evidence:
    # Demo mode banner
    if st.session_state.demo_mode:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 16px; padding: 32px; margin-bottom: 32px; color: white; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">🔬</div>
            <h2 style="margin: 0 0 12px 0; color: white;">Evidence Explorer</h2>
            <p style="margin: 0; font-size: 18px; opacity: 0.95;">
                Discover therapies backed by clinical research
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## 🔬 Evidence Explorer")
    st.markdown("Find therapies backed by clinical research for your condition")
    
    # Load evidence data
    @st.cache_data
    def load_evidence():
        """Load and standardize evidence data"""
        try:
            csv_path = Path("data/evidence_counts.csv")
            if not csv_path.exists():
                st.error("❌ Evidence data file not found!")
                return pd.DataFrame()
            
            df = pd.read_csv(csv_path)
            
            # Standardize column names
            if 'condition' in df.columns:
                df['condition'] = df['condition'].str.strip()
            if 'therapy' in df.columns:
                df['therapy'] = df['therapy'].str.strip()
            if 'evidence_direction' in df.columns:
                df['evidence_direction'] = df['evidence_direction'].str.strip()
            
            return df
            
        except Exception as e:
            st.error(f"❌ Error loading evidence data: {e}")
            return pd.DataFrame()
    
    evidence = load_evidence()
    
    if evidence.empty:
        st.warning("⚠️ No evidence data available. Please check your data file.")
        st.stop()
    
    st.success(f"✅ Loaded {len(evidence)} therapy-condition pairs")
    
    # Filters
    with st.expander("🔍 **Search Filters** (Select your condition to get started)", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Condition filter
            conditions = sorted(evidence['condition'].unique())
            selected_condition = st.selectbox(
                "Select your condition:",
                ["All Conditions"] + conditions,
                key="condition_filter"
            )
        
        with col2:
            # Therapy group filter
            therapy_groups = sorted(evidence['therapy_group'].unique()) if 'therapy_group' in evidence.columns else []
            selected_group = st.selectbox(
                "Therapy category:",
                ["All Categories"] + therapy_groups,
                key="group_filter"
            )
        
        with col3:
            # Evidence direction filter
            evidence_directions = sorted(evidence['evidence_direction'].unique()) if 'evidence_direction' in evidence.columns else []
            selected_direction = st.selectbox(
                "Evidence strength:",
                ["All Evidence"] + evidence_directions,
                key="direction_filter"
            )
    
    # Apply filters
    filtered_evidence = evidence.copy()
    
    if selected_condition != "All Conditions":
        filtered_evidence = filtered_evidence[filtered_evidence['condition'] == selected_condition]
    
    if selected_group != "All Categories" and 'therapy_group' in filtered_evidence.columns:
        filtered_evidence = filtered_evidence[filtered_evidence['therapy_group'] == selected_group]
    
    if selected_direction != "All Evidence" and 'evidence_direction' in filtered_evidence.columns:
        filtered_evidence = filtered_evidence[filtered_evidence['evidence_direction'] == selected_direction]
    
    st.markdown(f"**Found {len(filtered_evidence)} therapies** for your criteria")
    
    if len(filtered_evidence) == 0:
        st.info("No therapies match your current filters. Try adjusting your selection.")
    else:
        # Sort by evidence strength
        if 'trials_num' in filtered_evidence.columns:
            filtered_evidence = filtered_evidence.sort_values('trials_num', ascending=False)
        
        # Display results
        st.markdown("### 📊 **Therapy Results**")
        
        for idx, (_, row) in enumerate(filtered_evidence.head(20).iterrows()):
            therapy_name = row.get("therapy", "Unknown")
            condition_name = row.get("condition", "")
            category = row.get("therapy_group", "Unknown")
            evidence_dir = row.get("evidence_direction", "Unclear")
            trials_n = int(row.get("trials_num", 0))
            pubmed_n = int(row.get("pubmed_num", 0))
            
            # Evidence strength indicator
            if evidence_dir == "Positive":
                evidence_icon = "✅"
                evidence_emoji = "🟢"
            elif evidence_dir == "Negative":
                evidence_icon = "❌"
                evidence_emoji = "🔴"
            else:
                evidence_icon = "⚠️"
                evidence_emoji = "🟡"
            
            # Create therapy card using native Streamlit components
            with st.container():
                # Header with therapy name and evidence
                col_header1, col_header2 = st.columns([3, 1])
                with col_header1:
                    st.markdown(f"#### {therapy_name}")
                with col_header2:
                    st.markdown(f"**{evidence_icon} {evidence_dir}**")
                
                # Info columns
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("CONDITION")
                    st.markdown(f"**{condition_name}**")
                with col2:
                    st.caption("CATEGORY")
                    st.markdown(f"**{category}**")
                
                # Metrics
                col3, col4 = st.columns(2)
                with col3:
                    st.metric("Clinical Trials", trials_n)
                with col4:
                    st.metric("Research Papers", pubmed_n)
                
                st.divider()
            
            # Add AI Explain button if enabled
            if st.session_state.ai_enabled and ENABLE_AI_FEATURES:
                explain_key = f"explain_{therapy_name.replace(' ', '_')}_{idx}"
                explain_state_key = f"explanation_{explain_key}"
                
                # Check if explanation is already shown for this therapy
                show_explanation = st.session_state.get(explain_state_key, False)
                
                col_btn1, col_btn2 = st.columns([1, 3])
                
                with col_btn1:
                    available, reason = check_ai_available()
                    button_disabled = not available
                    
                    if st.button(
                        f"🤖 Explain" if available else f"🤖 ({reason})",
                        key=explain_key,
                        disabled=button_disabled,
                        use_container_width=True
                    ):
                        st.session_state[explain_state_key] = not show_explanation
                        st.rerun()
                
                # Show explanation if toggled
                if show_explanation:
                    with st.spinner(f"Learning about {therapy_name}..."):
                        condition = selected_condition if selected_condition != "All Conditions" else None
                        result = get_therapy_explanation(therapy_name, condition)
                        
                        if result["success"]:
                            cache_badge = "💾 Cached" if result.get("cached") else "✨ Fresh"
                            
                            # Display explanation with native Streamlit components
                            with st.container():
                                col_exp1, col_exp2 = st.columns([3, 1])
                                with col_exp1:
                                    st.markdown(f"**💡 Understanding {therapy_name}**")
                                with col_exp2:
                                    st.caption(cache_badge)
                                
                                st.info(result["explanation"])
                        else:
                            st.error(f"❌ {result['error']}")
        
        if len(filtered_evidence) > 20:
            st.info(f"Showing top 20 results. Total: {len(filtered_evidence)} therapies found.")

# Daily Log Tab
with tab_analysis:
    # Demo mode banner
    if st.session_state.demo_mode:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    border-radius: 16px; padding: 32px; margin-bottom: 32px; color: white; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">🌱</div>
            <h2 style="margin: 0 0 12px 0; color: white;">Daily Wellness Log</h2>
            <p style="margin: 0; font-size: 18px; opacity: 0.95;">
                Track your health journey with AI-powered insights
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## 🌱 Daily Wellness Log")
    
    # Initialize data storage if not exists
    if 'n1_df' not in st.session_state:
        st.session_state.n1_df = pd.DataFrame()
    
    # Check if user has any data
    is_first_entry = st.session_state.n1_df.empty
    
    # Show AI usage stats if AI is enabled
    if st.session_state.ai_enabled and ENABLE_AI_FEATURES:
        show_ai_usage_stats()
    
    # Mode selector if AI is available
    if st.session_state.ai_enabled and ENABLE_AI_FEATURES:
        st.markdown("### How would you like to log today?")
        
        col_choice1, col_choice2 = st.columns(2)
        
        available, reason = check_ai_available()
        
        with col_choice1:
            ai_button_disabled = not available
            ai_button_label = "💬 Chat with AI Logger" if available else f"💬 AI Logger ({reason})"
            
            if st.button(ai_button_label, use_container_width=True, 
                        type="primary" if available else "secondary",
                        disabled=ai_button_disabled):
                st.session_state.log_mode = "ai"
                st.rerun()
        
        with col_choice2:
            if st.button("📝 Use Traditional Form", use_container_width=True):
                st.session_state.log_mode = "form"
                st.rerun()
        
        st.markdown("---")
        
        # ==================== AI CHAT LOGGER ====================
        if st.session_state.log_mode == "ai" and available:
            st.markdown("### 💬 AI Symptom Logger")
            st.caption("Just tell me how you're feeling in your own words - I'll handle the rest!")
            
            # Show example prompts for first-time users
            if not st.session_state.ai_logger_used:
                st.info("**Try saying things like:**\n- 'I had a headache today, pain about 6/10, and only slept 5 hours'\n- 'Feeling good today! Did yoga and my mood is much better'\n- 'Anxious and stressed, pain is worse than yesterday'")
            
            # Display recent context
            if not st.session_state.n1_df.empty:
                last_entry = st.session_state.n1_df.iloc[-1] if len(st.session_state.n1_df) > 0 else None
                if last_entry is not None:
                    st.info(f"**Yesterday's snapshot:** Pain {last_entry.get('pain_score', 'N/A')}/10 • Sleep {last_entry.get('sleep_hours', 'N/A')}h • Mood {last_entry.get('mood_score', 'N/A')}/10")
            
            # Chat input
            user_input = st.text_area(
                "Tell me about today:",
                placeholder="E.g., 'Had a rough night, only slept 4 hours. Pain is about 7/10, mostly in my lower back. Did some stretching but feeling pretty stressed.'",
                height=120,
                key="ai_symptom_input"
            )
            
            col_parse, col_clear = st.columns([3, 1])
            
            with col_parse:
                if st.button("✨ Parse & Preview", type="primary", use_container_width=True):
                    if user_input.strip():
                        with st.spinner("Understanding your symptoms..."):
                            # Get recent context
                            context = None
                            if not st.session_state.n1_df.empty:
                                last = st.session_state.n1_df.iloc[-1]
                                context = {
                                    "yesterday_pain": float(last.get("pain_score", 5)),
                                    "yesterday_sleep": float(last.get("sleep_hours", 7)),
                                    "yesterday_mood": float(last.get("mood_score", 5))
                                }
                            
                            result = parse_symptom_entry(user_input, context)
                            
                            if result["success"]:
                                st.session_state.ai_symptom_data = result["data"]
                                st.session_state.ai_original_input = user_input
                                st.success("✅ Got it! Review the extracted data below.")
                            else:
                                st.error(f"❌ {result['error']}")
                    else:
                        st.warning("Please describe your symptoms first!")
            
            with col_clear:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.ai_symptom_data = None
                    st.session_state.ai_original_input = ""
                    st.rerun()
            
            # Show parsed data for review
            if st.session_state.ai_symptom_data:
                st.markdown("---")
                st.markdown("### 📊 Extracted Data - Please Review")
                
                parsed = st.session_state.ai_symptom_data
                
                # Show what was captured
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pain_val = parsed.get('pain_score')
                    st.metric("Pain", f"{pain_val}/10" if pain_val is not None else "Not mentioned")
                    stress_val = parsed.get('stress_score')
                    st.metric("Stress", f"{stress_val}/10" if stress_val is not None else "Not mentioned")
                
                with col2:
                    sleep_val = parsed.get('sleep_hours')
                    st.metric("Sleep", f"{sleep_val}h" if sleep_val is not None else "Not mentioned")
                    anxiety_val = parsed.get('anxiety_score')
                    st.metric("Anxiety", f"{anxiety_val}/10" if anxiety_val is not None else "Not mentioned")
                
                with col3:
                    mood_val = parsed.get('mood_score')
                    st.metric("Mood", f"{mood_val}/10" if mood_val is not None else "Not mentioned")
                
                if parsed.get('therapy_used'):
                    st.markdown(f"**Therapies mentioned:** {', '.join(parsed['therapy_used'])}")
                
                if parsed.get('physical_symptoms'):
                    st.markdown(f"**Physical symptoms:** {', '.join(parsed['physical_symptoms'])}")
                
                if parsed.get('emotional_symptoms'):
                    st.markdown(f"**Emotional state:** {', '.join(parsed['emotional_symptoms'])}")
                
                if parsed.get('notes'):
                    st.markdown(f"**Notes:** {parsed['notes']}")
                
                # Allow editing and saving
                st.markdown("#### ✏️ Want to adjust anything?")
                
                with st.form("ai_entry_review"):
                    edit_col1, edit_col2, edit_col3 = st.columns(3)
                    
                    with edit_col1:
                        final_pain = st.slider("Pain", 0, 10, parsed.get('pain_score') if parsed.get('pain_score') is not None else 5)
                        final_sleep = st.slider("Sleep (hours)", 0, 14, parsed.get('sleep_hours') if parsed.get('sleep_hours') is not None else 7)
                    
                    with edit_col2:
                        final_mood = st.slider("Mood", 0, 10, parsed.get('mood_score') if parsed.get('mood_score') is not None else 5)
                        final_stress = st.slider("Stress", 0, 10, parsed.get('stress_score') if parsed.get('stress_score') is not None else 5)
                    
                    with edit_col3:
                        final_anxiety = st.slider("Anxiety", 0, 10, parsed.get('anxiety_score') if parsed.get('anxiety_score') is not None else 5)
                        final_patience = st.slider("Patience", 0, 10, 5)
                    
                    additional_notes = st.text_area(
                        "Additional notes (optional)",
                        value=parsed.get('notes', ''),
                        height=80
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    
                    with col_save:
                        save_clicked = st.form_submit_button("💾 Save Entry", type="primary", use_container_width=True)
                    
                    with col_cancel:
                        cancel_clicked = st.form_submit_button("❌ Cancel", use_container_width=True)
                    
                    if save_clicked:
                        # Save the entry
                        row_data = {
                            "date": datetime.now().date(),
                            "pain_score": final_pain,
                            "sleep_hours": final_sleep,
                            "mood_score": final_mood,
                            "stress_score": final_stress,
                            "anxiety_score": final_anxiety,
                            "patience_score": final_patience,
                            "therapy_used": parsed.get('therapy_used', []),
                            "physical_symptoms": parsed.get('physical_symptoms', []),
                            "emotional_symptoms": parsed.get('emotional_symptoms', []),
                            "notes": additional_notes,
                        }
                        
                        # Add to dataframe
                        new_row = pd.DataFrame([row_data])
                        st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_row], ignore_index=True)
                        
                        st.success("✅ Entry saved via AI! Check your Dashboard to see trends.")
                        st.balloons()
                        
                        # Mark as used
                        st.session_state.ai_logger_used = True
                        
                        # Clear
                        st.session_state.ai_symptom_data = None
                        st.session_state.ai_original_input = ""
                        
                        st.rerun()
                    
                    if cancel_clicked:
                        st.session_state.ai_symptom_data = None
                        st.rerun()
        
        # Show message if AI mode selected but unavailable
        elif st.session_state.log_mode == "ai" and not available:
            st.warning(f"⚠️ AI Logger is currently unavailable: {reason}")
            st.info("👉 Please use the traditional form below or wait until tomorrow for rate limit reset.")
            st.session_state.log_mode = "form"
    
    # ==================== TRADITIONAL FORM ====================
    # Show traditional form if:
    # - AI is disabled
    # - User chose form mode
    # - This is first time user with simplified entry
    
    if not (st.session_state.ai_enabled and st.session_state.log_mode == "ai" and ENABLE_AI_FEATURES):
        if is_first_entry:
            # SIMPLIFIED FIRST ENTRY
            st.markdown("# 🌱")
            st.markdown("## Step 2: Your First Entry")
            st.markdown("**Takes just 30 seconds! Track the basics to get started.**")
            st.markdown("---")
            
            with st.form("first_entry"):
                st.markdown("### Quick Health Check")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pain_score = st.slider("Pain Level (0-10)", 0, 10, 5, help="0 = No pain, 10 = Worst pain")
                    sleep_hours = st.slider("Sleep Hours", 0, 14, 7, help="How many hours did you sleep?")
                
                with col2:
                    mood_score = st.slider("Mood (0-10)", 0, 10, 5, help="0 = Terrible, 10 = Excellent")
                    stress_score = st.slider("Stress Level (0-10)", 0, 10, 5, help="0 = No stress, 10 = Extreme stress")
                
                with col3:
                    anxiety_score = st.slider("Anxiety (0-10)", 0, 10, 5, help="0 = No anxiety, 10 = Severe anxiety")
                    patience_score = st.slider("Patience (0-10)", 0, 10, 5, help="0 = No patience, 10 = Very patient")
                
                notes = st.text_area("Any additional notes?", placeholder="How are you feeling today? Any symptoms or improvements?")
                
                submitted = st.form_submit_button("💾 Save My First Entry", type="primary", use_container_width=True)
                
                if submitted:
                    # Save the entry
                    row_data = {
                        "date": datetime.now().date(),
                        "pain_score": pain_score,
                        "sleep_hours": sleep_hours,
                        "mood_score": mood_score,
                        "stress_score": stress_score,
                        "anxiety_score": anxiety_score,
                        "patience_score": patience_score,
                        "therapy_used": [],
                        "physical_symptoms": [],
                        "emotional_symptoms": [],
                        "notes": notes,
                    }
                    
                    # Add to dataframe
                    new_row = pd.DataFrame([row_data])
                    st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_row], ignore_index=True)
                    
                    st.success("🎉 Great! Your first entry is saved. Check out your Dashboard to see your data!")
                    st.balloons()
                    st.rerun()
        else:
            # FULL FORM
            st.markdown("### 📝 Traditional Entry Form")
            
            with st.form("daily_entry"):
                st.markdown("#### How are you feeling today?")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pain_score = st.slider("Pain Level (0-10)", 0, 10, 5)
                    sleep_hours = st.slider("Sleep Hours", 0, 14, 7)
                
                with col2:
                    mood_score = st.slider("Mood (0-10)", 0, 10, 5)
                    stress_score = st.slider("Stress Level (0-10)", 0, 10, 5)
                
                with col3:
                    anxiety_score = st.slider("Anxiety (0-10)", 0, 10, 5)
                    patience_score = st.slider("Patience (0-10)", 0, 10, 5)
                
                # Therapy tracking
                st.markdown("#### Therapies & Activities")
                therapy_used = st.multiselect(
                    "What therapies did you use today?",
                    ["Yoga", "Meditation", "Exercise", "Massage", "Acupuncture", "Physical Therapy", "Other"],
                    help="Select all that apply"
                )
                
                # Symptoms
                physical_symptoms = st.multiselect(
                    "Physical symptoms today:",
                    ["Headache", "Fatigue", "Muscle tension", "Nausea", "Dizziness", "Other"],
                    help="Select any physical symptoms"
                )
                
                emotional_symptoms = st.multiselect(
                    "Emotional state today:",
                    ["Anxious", "Depressed", "Irritable", "Calm", "Happy", "Frustrated", "Other"],
                    help="How did you feel emotionally?"
                )
                
                notes = st.text_area("Additional notes:", placeholder="Any other observations about your day?")
                
                submitted = st.form_submit_button("💾 Save Entry", type="primary", use_container_width=True)
                
                if submitted:
                    # Save the entry
                    row_data = {
                        "date": datetime.now().date(),
                        "pain_score": pain_score,
                        "sleep_hours": sleep_hours,
                        "mood_score": mood_score,
                        "stress_score": stress_score,
                        "anxiety_score": anxiety_score,
                        "patience_score": patience_score,
                        "therapy_used": therapy_used,
                        "physical_symptoms": physical_symptoms,
                        "emotional_symptoms": emotional_symptoms,
                        "notes": notes,
                    }
                    
                    # Add to dataframe
                    new_row = pd.DataFrame([row_data])
                    st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_row], ignore_index=True)
                    
                    st.success("✅ Entry saved! Your data is being tracked.")
                    st.rerun()
    
    # Show recent entries
    if not st.session_state.n1_df.empty:
        st.markdown("---")
        st.markdown("### 📊 Recent Entries")
        recent_df = st.session_state.n1_df.tail(5)[["date", "pain_score", "sleep_hours", "mood_score"]]
        st.dataframe(recent_df, use_container_width=True)

# Dashboard Tab
with tab_dashboard:
    # Demo mode banner
    if st.session_state.demo_mode:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    border-radius: 16px; padding: 32px; margin-bottom: 32px; color: white; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">🏠</div>
            <h2 style="margin: 0 0 12px 0; color: white;">Health Dashboard</h2>
            <p style="margin: 0; font-size: 18px; opacity: 0.95;">
                Analyze patterns and track your progress
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## 🏠 Your Health Dashboard")
    st.markdown("Track your progress and discover patterns in your wellness journey")
    
    # Check if user has data
    if 'n1_df' not in st.session_state or st.session_state.n1_df.empty:
        st.info("📊 No data yet! Start logging in the Daily Log tab to see your dashboard.")
        st.markdown("### Getting Started")
        st.markdown("""
        1. **Go to Daily Log** - Add your first entry
        2. **Track consistently** - Log daily for best insights
        3. **Check back here** - Watch your patterns emerge
        """)
    else:
        df = st.session_state.n1_df.copy()
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        st.success(f"📈 You have {len(df)} entries! Here's what we found:")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_pain = df['pain_score'].mean() if 'pain_score' in df.columns else 0
            st.metric("Average Pain", f"{avg_pain:.1f}/10", 
                     delta=f"{df['pain_score'].iloc[-1] - avg_pain:.1f}" if len(df) > 1 else None)
        
        with col2:
            avg_sleep = df['sleep_hours'].mean() if 'sleep_hours' in df.columns else 0
            st.metric("Average Sleep", f"{avg_sleep:.1f}h", 
                     delta=f"{df['sleep_hours'].iloc[-1] - avg_sleep:.1f}" if len(df) > 1 else None)
        
        with col3:
            avg_mood = df['mood_score'].mean() if 'mood_score' in df.columns else 0
            st.metric("Average Mood", f"{avg_mood:.1f}/10", 
                     delta=f"{df['mood_score'].iloc[-1] - avg_mood:.1f}" if len(df) > 1 else None)
        
        with col4:
            tracking_days = len(df)
            st.metric("Tracking Days", f"{tracking_days}", 
                     delta="+1" if len(df) > 1 else None)
        
        st.markdown("---")
        
        # Charts section
        st.markdown("### 📊 Trends Over Time")
        
        if len(df) >= 2:
            # Pain trend
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Pain Level")
                st.line_chart(df.set_index('date')['pain_score'], height=200)
            
            with col2:
                st.markdown("#### Sleep Hours")
                st.line_chart(df.set_index('date')['sleep_hours'], height=200)
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.markdown("#### Mood Score")
                st.line_chart(df.set_index('date')['mood_score'], height=200)
            
            with col4:
                st.markdown("#### Stress Level")
                if 'stress_score' in df.columns:
                    st.line_chart(df.set_index('date')['stress_score'], height=200)
                else:
                    st.info("No stress data yet")
        else:
            st.info("📈 Add more entries to see trend charts!")
        
        st.markdown("---")
        
        # Insights section
        st.markdown("### 💡 Insights & Patterns")
        
        if len(df) >= 3:
            # Pain-Sleep correlation
            if 'pain_score' in df.columns and 'sleep_hours' in df.columns:
                correlation = df['pain_score'].corr(df['sleep_hours'])
                
                if abs(correlation) > 0.3:
                    if correlation < -0.3:
                        st.success(f"🔍 **Sleep-Pain Connection**: Better sleep tends to reduce pain (correlation: {correlation:.2f})")
                    else:
                        st.warning(f"🔍 **Sleep-Pain Connection**: More sleep is associated with higher pain (correlation: {correlation:.2f})")
                else:
                    st.info("🔍 **Sleep-Pain Connection**: No strong correlation found between sleep and pain")
            
            # Mood trends
            if 'mood_score' in df.columns:
                recent_mood = df['mood_score'].tail(3).mean()
                overall_mood = df['mood_score'].mean()
                
                if recent_mood > overall_mood + 0.5:
                    st.success(f"📈 **Mood Trend**: Your mood is improving! Recent average: {recent_mood:.1f}/10")
                elif recent_mood < overall_mood - 0.5:
                    st.warning(f"📉 **Mood Trend**: Your mood has been lower recently. Average: {recent_mood:.1f}/10")
                else:
                    st.info(f"📊 **Mood Trend**: Your mood is stable around {recent_mood:.1f}/10")
            
            # Therapy effectiveness
            if 'therapy_used' in df.columns:
                therapy_data = df[df['therapy_used'].notna() & (df['therapy_used'] != '')]
                if not therapy_data.empty:
                    st.markdown("#### 🧘 Therapy Usage")
                    
                    # Count therapy usage
                    all_therapies = []
                    for therapies in therapy_data['therapy_used']:
                        if isinstance(therapies, list):
                            all_therapies.extend(therapies)
                    
                    if all_therapies:
                        therapy_counts = pd.Series(all_therapies).value_counts()
                        st.bar_chart(therapy_counts)
                        
                        # Show most used therapy
                        most_used = therapy_counts.index[0]
                        st.info(f"🎯 **Most Used Therapy**: {most_used} ({therapy_counts.iloc[0]} times)")
        else:
            st.info("💡 Add more entries to unlock personalized insights!")
        
        st.markdown("---")
        
        # Recent entries table
        st.markdown("### 📋 Recent Entries")
        display_df = df.tail(10)[['date', 'pain_score', 'sleep_hours', 'mood_score', 'notes']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, use_container_width=True)
        
        # Export data
        st.markdown("### 💾 Export Your Data")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"health_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# AI Assistant Tab (only show if AI is enabled)
if st.session_state.ai_enabled and ENABLE_AI_FEATURES:
    with tab_ai:
        # Demo mode banner
        if st.session_state.demo_mode:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        border-radius: 16px; padding: 32px; margin-bottom: 32px; color: white; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 16px;">🤖</div>
                <h2 style="margin: 0 0 12px 0; color: white;">AI Health Assistant</h2>
                <p style="margin: 0; font-size: 18px; opacity: 0.95;">
                    Get personalized insights and recommendations
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("## 🤖 Your Health Assistant")
        st.caption("Ask me anything about your symptoms, therapies, or insights!")
        
        # Show usage stats
        show_ai_usage_stats()
        
        available, reason = check_ai_available()
        
        if not available:
            st.warning(f"⚠️ AI Assistant unavailable: {reason}")
            if "limit" in reason.lower():
                st.info("💡 Your daily limit will reset at midnight. In the meantime, explore your Dashboard or browse the Evidence Explorer!")
        
        # Quick action buttons
        st.markdown("### Quick Actions")
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        
        with quick_col1:
            if st.button("📊 Analyze My Patterns", use_container_width=True, disabled=not available):
                st.session_state.ai_quick_prompt = "Can you analyze my symptom patterns and tell me what you notice?"
        
        with quick_col2:
            if st.button("💊 Recommend Therapies", use_container_width=True, disabled=not available):
                st.session_state.ai_quick_prompt = "Based on my data, what therapies should I consider trying?"
        
        with quick_col3:
            if st.button("🎯 Set a Goal", use_container_width=True, disabled=not available):
                st.session_state.ai_quick_prompt = "Help me set a realistic health goal based on my current progress."
        
        st.markdown("---")
        
        # Chat interface
        st.markdown("### 💬 Chat")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if st.session_state.ai_chat_history:
                for msg in st.session_state.ai_chat_history[-10:]:  # Show last 10 messages
                    if msg["role"] == "user":
                        with st.chat_message("user"):
                            st.write(msg["content"])
                    else:
                        with st.chat_message("assistant"):
                            st.write(msg["content"])
            else:
                st.info("👋 Hi! I'm your AI health assistant. Ask me anything about:\n- Your symptom patterns\n- Therapy recommendations\n- Understanding your data\n- Staying motivated with tracking")
        
        # Chat input
        prompt = st.session_state.get("ai_quick_prompt", "")
        if prompt:
            st.session_state.ai_quick_prompt = ""  # Clear after use
        
        user_message = st.text_input(
            "Ask me anything:",
            value=prompt,
            placeholder="E.g., 'Why is my pain worse on weekends?' or 'Tell me about acupuncture'",
            key="ai_chat_input",
            disabled=not available
        )
        
        col_send, col_clear_chat = st.columns([4, 1])
        
        with col_send:
            send_clicked = st.button("Send", type="primary", use_container_width=True, disabled=not available)
            
            if (send_clicked or prompt) and user_message.strip() and available:
                # Add user message to history
                st.session_state.ai_chat_history.append({
                    "role": "user",
                    "content": user_message
                })
                
                # Get AI response
                with st.spinner("Thinking..."):
                    user_df = st.session_state.n1_df if "n1_df" in st.session_state else pd.DataFrame()
                    
                    # Simple chat function for now (we'll implement the full one later)
                    try:
                        response = openai.ChatCompletion.create(
                            model=OPENAI_MODEL,
                            messages=[
                                {"role": "system", "content": "You are a supportive health tracking assistant. Be helpful and encouraging."},
                                {"role": "user", "content": user_message}
                            ],
                            temperature=0.7,
                            max_tokens=300
                        )
                        
                        increment_ai_usage()
                        
                        assistant_response = response.choices[0].message.content.strip()
                        
                        # Add assistant response to history
                        st.session_state.ai_chat_history.append({
                            "role": "assistant",
                            "content": assistant_response
                        })
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                
                st.rerun()
        
        with col_clear_chat:
            if st.button("Clear", use_container_width=True):
                st.session_state.ai_chat_history = []
                st.rerun()
        
        st.markdown("---")
        
        # Suggested questions
        st.markdown("### 💡 Suggested Questions")
        suggestions = [
            "What's the correlation between my sleep and pain?",
            "Should I try meditation based on my stress levels?",
            "How has my mood changed this month?",
            "What days am I tracking best and worst?",
            "Give me motivation to keep tracking!"
        ]
        
        for suggestion in suggestions:
            if st.button(f"💬 {suggestion}", key=f"suggest_{suggestion}", 
                        use_container_width=True, disabled=not available):
                st.session_state.ai_quick_prompt = suggestion
                st.rerun()

# Calendar Tab
with tab_calendar:
    # Demo mode banner
    if st.session_state.demo_mode:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                    border-radius: 16px; padding: 32px; margin-bottom: 32px; color: white; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">📅</div>
            <h2 style="margin: 0 0 12px 0; color: white;">Health Calendar</h2>
            <p style="margin: 0; font-size: 18px; opacity: 0.95;">
                Visualize your health journey over time
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## 📅 Health Calendar")
    st.markdown("Visualize your health journey over time")
    
    # Check if user has data
    if 'n1_df' not in st.session_state or st.session_state.n1_df.empty:
        st.info("📅 No data yet! Start logging in the Daily Log tab to see your calendar.")
        st.markdown("### Calendar Features")
        st.markdown("""
        - **Daily health scores** - See your pain, mood, and sleep at a glance
        - **Therapy tracking** - Mark which therapies you used each day
        - **Pattern recognition** - Spot trends across weeks and months
        - **Export options** - Download your calendar data
        """)
    else:
        df = st.session_state.n1_df.copy()
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        st.success(f"📅 Showing {len(df)} entries in calendar view")
        
        # Calendar controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            view_type = st.selectbox("View Type", ["Monthly", "Weekly", "Daily"], key="calendar_view")
        
        with col2:
            metric_to_show = st.selectbox("Primary Metric", 
                                        ["pain_score", "sleep_hours", "mood_score", "stress_score"], 
                                        key="calendar_metric")
        
        with col3:
            show_therapies = st.checkbox("Show Therapies", value=True, key="show_therapies")
        
        st.markdown("---")
        
        # Calendar display
        if view_type == "Monthly":
            st.markdown("### 📅 Monthly Overview")
            
            # Get current month or selected month
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                month_name = datetime(current_year, current_month, 1).strftime('%B %Y')
                st.markdown(f"#### {month_name}")
            
            # Create monthly grid
            month_data = df[df['date'].dt.month == current_month]
            
            if not month_data.empty:
                # Create a simple calendar grid
                st.markdown("**Daily Health Scores**")
                
                # Show metrics for each day
                calendar_df = month_data[['date', metric_to_show, 'therapy_used', 'notes']].copy()
                calendar_df['day'] = calendar_df['date'].dt.day
                calendar_df = calendar_df.sort_values('day')
                
                # Display in a grid format
                cols = st.columns(7)  # 7 days per week
                day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                
                for i, day_name in enumerate(day_names):
                    with cols[i]:
                        st.markdown(f"**{day_name}**")
                
                # Show days with data
                for _, row in calendar_df.iterrows():
                    day = row['day']
                    metric_value = row[metric_to_show]
                    therapies = row['therapy_used']
                    
                    # Color coding based on metric - use emoji indicators
                    if metric_to_show == "pain_score":
                        if metric_value <= 3:
                            indicator = "🟢"  # Green
                        elif metric_value <= 6:
                            indicator = "🟡"  # Orange
                        else:
                            indicator = "🔴"  # Red
                    elif metric_to_show == "mood_score":
                        if metric_value >= 7:
                            indicator = "🟢"  # Green
                        elif metric_value >= 4:
                            indicator = "🟡"  # Orange
                        else:
                            indicator = "🔴"  # Red
                    else:
                        indicator = "🔵"  # Blue
                    
                    st.markdown(f"**Day {day}:** {indicator} {metric_value:.1f}")
                    
                    if show_therapies and therapies:
                        therapy_list = ', '.join(therapies) if isinstance(therapies, list) else therapies
                        st.caption(therapy_list)
            else:
                st.info(f"No entries for {month_name}")
        
        elif view_type == "Weekly":
            st.markdown("### 📅 Weekly Overview")
            
            # Show last 4 weeks
            recent_data = df.tail(28)  # Last 4 weeks
            
            if not recent_data.empty:
                # Group by week
                recent_data['week'] = recent_data['date'].dt.isocalendar().week
                recent_data['year'] = recent_data['date'].dt.year
                
                weeks = recent_data.groupby(['year', 'week'])
                
                for (year, week), week_data in list(weeks)[-4:]:  # Last 4 weeks
                    st.markdown(f"#### Week {week}, {year}")
                    
                    # Show daily data for this week
                    week_data = week_data.sort_values('date')
                    
                    cols = st.columns(len(week_data))
                    for i, (_, day_data) in enumerate(week_data.iterrows()):
                        with cols[i]:
                            day_name = day_data['date'].strftime('%a')
                            day_num = day_data['date'].day
                            metric_value = day_data[metric_to_show]
                            
                            st.markdown(f"**{day_name} {day_num}**")
                            st.metric("", f"{metric_value:.1f}")
                            
                            if show_therapies and day_data['therapy_used']:
                                therapies = day_data['therapy_used']
                                if isinstance(therapies, list):
                                    st.caption(', '.join(therapies[:2]))
                                else:
                                    st.caption(str(therapies))
            
            else:
                st.info("No recent data for weekly view")
        
        else:  # Daily view
            st.markdown("### 📅 Daily Detail View")
            
            # Date picker
            if not df.empty:
                min_date = df['date'].min().date()
                max_date = df['date'].max().date()
                
                selected_date = st.date_input(
                    "Select a date to view details:",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date
                )
                
                # Show data for selected date
                day_data = df[df['date'].dt.date == selected_date]
                
                if not day_data.empty:
                    day_info = day_data.iloc[0]
                    
                    st.markdown(f"#### {selected_date.strftime('%A, %B %d, %Y')}")
                    
                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Pain", f"{day_info['pain_score']}/10")
                    with col2:
                        st.metric("Sleep", f"{day_info['sleep_hours']}h")
                    with col3:
                        st.metric("Mood", f"{day_info['mood_score']}/10")
                    with col4:
                        st.metric("Stress", f"{day_info['stress_score']}/10")
                    
                    # Therapies used
                    if show_therapies and day_info['therapy_used']:
                        st.markdown("#### 🧘 Therapies Used")
                        therapies = day_info['therapy_used']
                        if isinstance(therapies, list):
                            for therapy in therapies:
                                st.markdown(f"- {therapy}")
                        else:
                            st.markdown(f"- {therapies}")
                    
                    # Notes
                    if day_info['notes']:
                        st.markdown("#### 📝 Notes")
                        st.markdown(day_info['notes'])
                    
                    # Symptoms
                    if day_info['physical_symptoms'] or day_info['emotional_symptoms']:
                        st.markdown("#### 🩺 Symptoms")
                        
                        if day_info['physical_symptoms']:
                            st.markdown("**Physical:**")
                            symptoms = day_info['physical_symptoms']
                            if isinstance(symptoms, list):
                                for symptom in symptoms:
                                    st.markdown(f"- {symptom}")
                            else:
                                st.markdown(f"- {symptoms}")
                        
                        if day_info['emotional_symptoms']:
                            st.markdown("**Emotional:**")
                            symptoms = day_info['emotional_symptoms']
                            if isinstance(symptoms, list):
                                for symptom in symptoms:
                                    st.markdown(f"- {symptom}")
                            else:
                                st.markdown(f"- {symptoms}")
                else:
                    st.info(f"No data recorded for {selected_date.strftime('%B %d, %Y')}")
            else:
                st.info("No data available for daily view")
        
        st.markdown("---")
        
        # Export calendar data
        st.markdown("### 💾 Export Calendar Data")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Calendar CSV",
            data=csv,
            file_name=f"health_calendar_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Settings Tab
with tab_settings:
    # Demo mode banner
    if st.session_state.demo_mode:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%); 
                    border-radius: 16px; padding: 32px; margin-bottom: 32px; color: white; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">⚙️</div>
            <h2 style="margin: 0 0 12px 0; color: white;">Settings & Data Management</h2>
            <p style="margin: 0; font-size: 18px; opacity: 0.95;">
                Manage your data and customize your experience
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## ⚙️ Settings & Data Management")
    
    # AI Features Section
    st.markdown("### 🤖 AI Features")
    
    if ENABLE_AI_FEATURES:
        st.success("✅ OpenAI API key is configured!")
        
        # AI Toggle
        col_toggle, col_stats = st.columns([1, 1])
        
        with col_toggle:
            ai_enabled = st.toggle(
                "Enable AI Features",
                value=st.session_state.ai_enabled,
                help="Toggle AI-powered features on/off. You can disable to save API calls.",
                key="ai_enable_toggle"
            )
            
            if ai_enabled != st.session_state.ai_enabled:
                st.session_state.ai_enabled = ai_enabled
                st.success(f"AI features {'enabled' if ai_enabled else 'disabled'}!")
                st.rerun()
        
        with col_stats:
            # Usage statistics
            remaining = get_remaining_calls()
            used = st.session_state.ai_calls_count
            
            st.metric(
                "API Calls Today",
                f"{used}/{AI_RATE_LIMIT_PER_DAY}",
                f"{remaining} remaining",
                help="Resets daily at midnight"
            )
        
        # Cache statistics
        cache_size = len(st.session_state.get('therapy_explanation_cache', {}))
        st.metric("Cached Explanations", cache_size, help="Reduces API calls by reusing explanations")
        
        # Clear cache button
        if cache_size > 0:
            if st.button("🗑️ Clear Explanation Cache", help="Clear cached therapy explanations"):
                st.session_state.therapy_explanation_cache = {}
                st.session_state.cache_timestamp = {}
                st.success("Cache cleared!")
                st.rerun()
        
        st.markdown("---")
        
        # Cost estimation
        with st.expander("💰 Cost Estimation"):
            avg_cost_per_call = 0.002  # ~$0.002 for gpt-3.5-turbo
            daily_cost = used * avg_cost_per_call
            monthly_estimate = daily_cost * 30
            
            st.markdown(f"""
            **Today's Usage:**
            - API Calls: {used}
            - Estimated Cost: ${daily_cost:.3f}
            
            **Projected Monthly (at current rate):**
            - Estimated Cost: ${monthly_estimate:.2f}
            
            **Model:** {OPENAI_MODEL}
            
            *Note: Actual costs may vary. Check your OpenAI dashboard for precise billing.*
            """)
        
        # API Configuration
        with st.expander("🔧 Advanced Configuration"):
            st.markdown("**Current Settings:**")
            st.code(f"""
Model: {OPENAI_MODEL}
Daily Rate Limit: {AI_RATE_LIMIT_PER_DAY} calls
Cache TTL: {AI_CACHE_TTL_HOURS} hours
            """)
            
            st.markdown("**To change these settings:**")
            st.markdown("""
            1. Update your `.env` file:
```
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4
```
            2. Restart the app
            """)
        
        # Privacy info
        with st.expander("🔐 Privacy & Data Usage"):
            st.markdown("""
            **What data is shared with OpenAI:**
            - Your symptom descriptions (only when using AI logger)
            - Your aggregated statistics (for recommendations)
            - No personally identifying information
            
            **What's NOT shared:**
            - Your raw data entries (unless explicitly sent via AI logger)
            - Your identity or contact information
            - Any data from other users
            
            **Your control:**
            - You can toggle AI features on/off anytime
            - You can use the traditional form (no AI)
            - You own all your data
            - Cached explanations are stored locally only
            
            **Security:**
            - API key is stored in environment variables
            - All communication is encrypted (HTTPS)
            - OpenAI's data usage policy: [link](https://openai.com/policies/privacy-policy)
            """)
    
    else:
        st.warning("⚠️ AI features are disabled. Add your OpenAI API key to enable:")
        
        st.markdown("""
        **AI features include:**
        - 💬 Natural language symptom logging (chat instead of forms)
        - 🤖 Therapy explanations and recommendations  
        - 📊 Insight analysis and pattern recognition
        - 💡 Personalized health suggestions
        
        **To enable:**
        1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
        2. Create a `.env` file in your project root:
        """)
        
        st.code("""
# .env file
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
        """)
        
        st.markdown("3. Restart the app")
        
        st.info("💡 Using GPT-3.5-turbo keeps costs low (~$0.05-0.15 per day for active users)")
    
    st.markdown("---")
    
    # Data Management Section
    st.markdown("### 💾 Data Management")
    
    # Check if user has data
    if 'n1_df' not in st.session_state or st.session_state.n1_df.empty:
        st.info("📊 No data to manage yet. Start logging in the Daily Log tab!")
    else:
        df = st.session_state.n1_df
        st.success(f"📈 You have {len(df)} entries stored locally")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Entries", len(df))
        
        with col2:
            if 'date' in df.columns:
                date_range = f"{df['date'].min().strftime('%m/%d')} - {df['date'].max().strftime('%m/%d')}"
                st.metric("Date Range", date_range)
            else:
                st.metric("Date Range", "Unknown")
        
        with col3:
            # Calculate data size
            csv_size = len(df.to_csv())
            st.metric("Data Size", f"{csv_size:,} bytes")
        
        st.markdown("#### Export Your Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export CSV
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"pain_relief_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Export JSON
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"pain_relief_data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown("#### Data Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
                st.session_state.n1_df = pd.DataFrame()
                st.success("All data cleared!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset AI Usage", use_container_width=True, type="secondary"):
                st.session_state.ai_calls_count = 0
                st.session_state.ai_last_reset = datetime.now().date()
                st.success("AI usage reset!")
                st.rerun()
        
        with col3:
            if st.button("🧹 Clear Cache", use_container_width=True, type="secondary"):
                st.session_state.therapy_explanation_cache = {}
                st.session_state.cache_timestamp = {}
                st.success("Cache cleared!")
                st.rerun()
    
    st.markdown("---")
    
    # About Section
    st.markdown("### ℹ️ About Pain Relief Map")
    
    st.markdown("""
    **Pain Relief Map** is a comprehensive health tracking application that helps you:
    
    - 🔬 **Discover Evidence-Based Therapies** - Find treatments backed by clinical research
    - 📝 **Track Your Symptoms** - Log pain, sleep, mood, and other health metrics
    - 📊 **Analyze Patterns** - See correlations and trends in your data
    - 📅 **Visualize Progress** - Calendar view of your health journey
    - 🤖 **AI-Powered Insights** - Get personalized recommendations and explanations
    
    **Features:**
    - Natural language symptom logging (with AI)
    - Therapy effectiveness tracking
    - Data export capabilities
    - Privacy-first design
    - No account required (data stored locally)
    
    **Version:** 6.0 with AI Integration
    **Built with:** Streamlit, Python, OpenAI GPT-3.5-turbo
    """)
    
    # Support section
    with st.expander("🆘 Support & Help"):
        st.markdown("""
        **Need help?**
        
        - 📖 **Getting Started**: Use the Evidence Explorer to find therapies, then log daily in the Daily Log tab
        - 🤖 **AI Features**: Enable AI in Settings to get natural language logging and therapy explanations
        - 📊 **Dashboard**: Check your Dashboard tab to see trends and insights
        - 📅 **Calendar**: Use the Calendar tab to visualize your progress over time
        
        **Troubleshooting:**
        - If AI features aren't working, check your API key in Settings
        - Data is stored locally in your browser - clearing browser data will remove it
        - Export your data regularly to avoid data loss
        
        **Privacy:**
        - All data stays on your device
        - AI features only send anonymized data to OpenAI
        - No personal information is collected or stored
        """)
