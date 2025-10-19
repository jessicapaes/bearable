# Pain Relief Map - Authenticated Version
# This is a simplified version showing how authentication integrates

from pathlib import Path
import sys
import datetime as dt
import os

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.warning("python-dotenv not installed. Run: pip install python-dotenv")

# -----------------------------------------------------------------------------
# App config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pain Relief Map — Authenticated",
    layout="wide",
)

# Root for relative paths
ROOT = Path(__file__).resolve().parents[1]

# Ensure local imports resolve
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Import authentication and database modules
try:
    from src.auth import AuthManager, init_session_state
    from src.login_ui import require_authentication, show_user_menu
    from src.db_operations import DatabaseManager
    
    # Initialize managers
    auth_manager = AuthManager()
    db_manager = DatabaseManager()
    
    # Initialize session state for authentication
    init_session_state()
    
except ImportError as e:
    st.error(f"Error importing modules: {str(e)}")
    st.info("Make sure you have all required files in the src/ directory")
    st.stop()

# -----------------------------------------------------------------------------
# Authentication Check
# -----------------------------------------------------------------------------
if not require_authentication(auth_manager):
    st.stop()  # Stop here if not authenticated - login page will be shown

# Show user menu in sidebar
show_user_menu(auth_manager)

# -----------------------------------------------------------------------------
# Main App (for authenticated users)
# -----------------------------------------------------------------------------

st.title("💆🏻‍♀️ Pain Relief Map (With User Accounts)")

# Check if in demo mode or database mode
demo_mode = st.session_state.get("demo_mode", False)

if demo_mode:
    st.info("🎭 **Demo Mode**: Your data is temporary and will be lost when you close the browser. Login to save permanently!")

# -----------------------------------------------------------------------------
# Load user data
# -----------------------------------------------------------------------------

def load_user_data():
    """Load data from database or session state"""
    if demo_mode:
        # Demo mode: use session state
        if "n1_df" not in st.session_state:
            st.session_state.n1_df = pd.DataFrame()
        return st.session_state.n1_df
    else:
        # Database mode: load from Supabase
        user = st.session_state.get("user")
        if user and hasattr(user, 'id'):
            user_id = user.id
            df = db_manager.get_user_logs(user_id)
            st.session_state.n1_df = df
            return df
        else:
            return pd.DataFrame()

def save_user_log(log_data):
    """Save a log entry to database or session state"""
    if demo_mode:
        # Demo mode: append to session state
        if "n1_df" not in st.session_state:
            st.session_state.n1_df = pd.DataFrame()
        
        new_row = pd.DataFrame([log_data])
        st.session_state.n1_df = pd.concat([st.session_state.n1_df, new_row], ignore_index=True)
        return {"success": True, "message": "Saved to session"}
    else:
        # Database mode: save to Supabase
        user = st.session_state.get("user")
        if user and hasattr(user, 'id'):
            user_id = user.id
            result = db_manager.save_log(user_id, log_data)
            
            if result["success"]:
                # Reload data
                st.session_state.n1_df = db_manager.get_user_logs(user_id)
            
            return result
        else:
            return {"success": False, "message": "Please log in to save data"}

# Load user's data
user_data = load_user_data()

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab_dashboard, tab_log, tab_settings = st.tabs([
    "🏠 Dashboard",
    "🌱 Daily Log",
    "⚙️ Settings"
])

# -----------------------------------------------------------------------------
# Dashboard Tab
# -----------------------------------------------------------------------------
with tab_dashboard:
    st.subheader("Your Health Dashboard")
    
    if user_data.empty:
        st.info("👋 Welcome! Start by adding your first daily log in the 'Daily Log' tab.")
        
        # Show example of what dashboard will look like
        st.markdown("### What you'll see here:")
        st.markdown("""
        - **Latest entry snapshot** (pain, sleep, mood)
        - **14-day trend chart** showing your progress
        - **Key insights** about therapy effects
        - **Progress summary** (before vs after)
        """)
    else:
        # Show actual dashboard with user data
        st.markdown(f"### 📊 Your Stats ({len(user_data)} entries logged)")
        
        # Latest entry
        if "date" in user_data.columns:
            user_data["date"] = pd.to_datetime(user_data["date"], errors="coerce")
            latest = user_data.sort_values("date").iloc[-1]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Latest Pain", f"{int(latest.get('pain_score', 0))}/10")
            col2.metric("Latest Sleep", f"{float(latest.get('sleep_hours', 0)):.1f}h")
            col3.metric("Latest Mood", f"{int(latest.get('mood_score', 0))}/10")
        
        # Simple trend chart
        if len(user_data) > 1 and "date" in user_data.columns:
            st.markdown("### 📈 Your Trend")
            
            recent = user_data.tail(14)
            fig = px.line(
                recent,
                x="date",
                y="pain_score",
                title="Pain Score (Last 14 Days)",
                markers=True
            )
            fig.update_layout(yaxis_range=[0, 10])
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# Daily Log Tab
# -----------------------------------------------------------------------------
with tab_log:
    st.subheader("🌱 Daily Wellness Log")
    st.markdown("Track your daily health metrics")
    
    with st.form("daily_log", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            log_date = st.date_input("Date", value=dt.date.today(), format="DD/MM/YYYY")
            pain = st.slider("Pain (0-10)", 0, 10, 0)
            sleep = st.slider("Sleep hours", 0, 12, 7)
        
        with col2:
            mood = st.slider("Mood (0-10)", 0, 10, 5)
            stress = st.slider("Stress (0-10)", 0, 10, 0)
        
        condition = st.text_input("Condition felt today", placeholder="e.g., Anxiety, Chronic Pain")
        therapy = st.text_input("Therapy used today", placeholder="e.g., Meditation, Yoga")
        notes = st.text_area("Notes (optional)", placeholder="Any observations...")
        
        submitted = st.form_submit_button("Save Entry", type="primary")
        
        if submitted:
            log_entry = {
                "date": log_date,
                "pain_score": pain,
                "stress_score": stress,
                "mood_score": mood,
                "sleep_hours": sleep,
                "condition_today": condition,
                "therapy_used": therapy,
                "notes": notes,
            }
            
            result = save_user_log(log_entry)
            
            if result["success"]:
                st.success("✅ Entry saved!")
                st.rerun()
            else:
                st.error(f"Error: {result['message']}")
    
    # Show existing logs
    if not user_data.empty:
        st.markdown("---")
        st.markdown("### Your Logged Entries")
        
        # Format date column for display
        display_df = user_data.copy()
        if "date" in display_df.columns:
            display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%d/%m/%Y")
        
        # Show relevant columns
        cols_to_show = [c for c in ["date", "pain_score", "stress_score", "mood_score", "sleep_hours", 
                                     "condition_today", "therapy_used", "notes"] if c in display_df.columns]
        
        st.dataframe(
            display_df[cols_to_show].sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True
        )

# -----------------------------------------------------------------------------
# Settings Tab
# -----------------------------------------------------------------------------
with tab_settings:
    st.subheader("⚙️ Settings")
    
    # User profile
    if not demo_mode:
        st.markdown("### 👤 Your Profile")
        profile = st.session_state.get("user_profile", {})
        user = st.session_state.get("user")
        
        if user and hasattr(user, 'email'):
            st.text_input("Email", value=user.email, disabled=True)
            st.text_input("Display Name", value=profile.get("display_name", "") if profile else "", key="profile_name")
            
            if st.button("Update Profile"):
                st.info("Profile update coming soon!")
        else:
            st.warning("Please log in to view your profile")
    
    # Export data
    st.markdown("### 💾 Export Your Data")
    if not user_data.empty:
        csv = user_data.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            data=csv,
            file_name=f"health_log_{dt.date.today()}.csv",
            mime="text/csv"
        )
        st.caption(f"{len(user_data)} entries ready to export")
    else:
        st.info("No data to export yet")
    
    # Danger zone
    if demo_mode:
        st.markdown("---")
        st.markdown("### 🔐 Save Your Data Permanently")
        st.warning("You're in demo mode. Create an account to save your data!")
        if st.button("Create Account", type="primary"):
            st.session_state.authenticated = False
            st.rerun()
    else:
        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")
        if st.checkbox("Show danger zone"):
            st.error("**Delete All Data**: This cannot be undone!")
            confirm = st.text_input("Type 'DELETE' to confirm")
            if st.button("Delete All My Data") and confirm == "DELETE":
                user = st.session_state.get("user")
                if user and hasattr(user, 'id'):
                    user_id = user.id
                    # Would implement deletion here
                    st.warning("Deletion not yet implemented")
                else:
                    st.error("Not authenticated")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("💚 Pain Relief Map - Your health data stays private and secure")

