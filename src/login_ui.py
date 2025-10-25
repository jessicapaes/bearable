"""
Login and signup UI components for Streamlit
"""
import streamlit as st
from src.auth import AuthManager, init_session_state


def show_login_page(auth_manager: AuthManager):
    """Display login/signup page"""
    
    # Initialize session state
    init_session_state()
    
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
    
    # Check if authentication is enabled
    if not auth_manager.is_enabled():
        st.error("⚠️ Authentication not configured")
        st.warning("""
        To enable user accounts:
        
        1. **Create a Supabase account** at https://supabase.com
        2. **Create a new project**
        3. **Run the SQL schema** from `scripts/create_user_tables.sql` in your Supabase SQL Editor
        4. **Get your project credentials**:
           - Go to Project Settings → API
           - Copy the URL and anon/public key
        5. **Create a .env file** in the project root with:
           ```
           SUPABASE_URL=your_url_here
           SUPABASE_KEY=your_key_here
           ```
        6. **Restart the app**
        
        **For now, you can use demo mode** (toggle below to test without authentication)
        """)
        
        if st.button("🎭 Continue in Demo Mode (No Login Required)", type="primary"):
            st.session_state.authenticated = True
            st.session_state.user = {"id": "demo-user", "email": "demo@bearable.com"}
            st.session_state.demo_mode = True
            st.rerun()
        return
    
    # Two column layout for Sign In and Create Account
    col1, col2 = st.columns(2, gap="large")
    
    # SIGN IN FORM
    with col1:
        with st.form("auth_signin_form", clear_on_submit=False):
            st.markdown("""
                <h3 style="margin: 0 0 10px 0; color: #1a202c;">🔐 Sign In</h3>
                <p style="font-weight: 600; margin-bottom: 25px; color: #64748b;">Access your personal health dashboard</p>
            """, unsafe_allow_html=True)
            
            email = st.text_input("Email", placeholder="your.email@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            col_submit, col_forgot = st.columns([3, 1])
            with col_submit:
                submit = st.form_submit_button("SIGN IN", type="primary", use_container_width=True)
            with col_forgot:
                forgot_clicked = st.form_submit_button("Forgot?", use_container_width=True)
            
            # Add spacing below buttons
            st.markdown('<div style="margin-bottom: 3rem;"></div>', unsafe_allow_html=True)
            
            if submit:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    with st.spinner("Logging in..."):
                        result = auth_manager.login(email, password)
                    
                    if result["success"]:
                        st.success(result["message"])
                        st.session_state.authenticated = True
                        st.session_state.user = result["user"]
                        st.session_state.user_profile = result.get("profile")
                        st.session_state.demo_mode = False
                        st.rerun()
                    else:
                        st.error(result["message"])
            
            if forgot_clicked:
                st.info("Password reset functionality coming soon!")
    
    # CREATE ACCOUNT FORM
    with col2:
        with st.form("auth_signup_form", clear_on_submit=False):
            st.markdown("""
                <h3 style="margin: 0 0 10px 0; color: #1a202c;">📝 Create Account</h3>
                <p style="font-weight: 600; margin-bottom: 25px; color: #64748b;">Start tracking your health journey</p>
            """, unsafe_allow_html=True)
            
            signup_name = st.text_input("Name", placeholder="Enter your full name", key="signup_name")
            signup_email = st.text_input("Email", placeholder="your.email@example.com", key="signup_email")
            signup_password = st.text_input("Password", type="password", placeholder="Create a strong password", 
                                          help="At least 8 characters", key="signup_password")
            signup_password2 = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password", key="signup_password2")
            
            agree = st.checkbox("I agree to store my health data securely", key="agree_terms")
            
            submit_signup = st.form_submit_button("CREATE ACCOUNT", type="primary", use_container_width=True)
            
            # Add spacing below button
            st.markdown('<div style="margin-bottom: 3rem;"></div>', unsafe_allow_html=True)
            
            if submit_signup:
                # Validation
                if not all([signup_name, signup_email, signup_password, signup_password2]):
                    st.error("Please fill in all fields")
                elif signup_password != signup_password2:
                    st.error("Passwords don't match")
                elif len(signup_password) < 8:
                    st.error("Password must be at least 8 characters")
                elif not agree:
                    st.error("Please agree to the terms")
                else:
                    with st.spinner("Creating your account..."):
                        result = auth_manager.signup(signup_email, signup_password, signup_name)
                    
                    if result["success"]:
                        st.success(result["message"])
                        st.info("📧 Please check your email to verify your account, then login above.")
                    else:
                        st.error(result["message"])
    
    # Demo mode option
    st.markdown('<div style="margin-top: 3rem;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("### 🎭 Try Demo Mode")
        st.caption("No account needed - explore with sample data")
        if st.button("Continue in Demo Mode", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user = {"id": "demo-user", "email": "demo@bearable.com"}
            st.session_state.demo_mode = True
            st.rerun()


def show_user_menu(auth_manager: AuthManager):
    """Display user menu in sidebar"""
    
    with st.sidebar:
        st.markdown("---")
        
        # User info
        user = st.session_state.get("user")
        profile = st.session_state.get("user_profile", {})
        
        if st.session_state.get("demo_mode"):
            st.info("🎭 **Demo Mode**\n\nYour data is temporary")
            if st.button("🔑 Login to Save Data", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.demo_mode = False
                st.rerun()
        else:
            # User is a Pydantic model, access attributes directly
            user_email = getattr(user, 'email', '')
            display_name = profile.get("display_name") if profile else (user_email.split("@")[0] if user_email else "User")
            st.markdown(f"### 👤 {display_name}")
            st.caption(user_email)
            
            # Stats
            if hasattr(st.session_state, 'user_stats'):
                stats = st.session_state.user_stats
                st.metric("Total Logs", stats.get("total_logs", 0))
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                auth_manager.logout()
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.user_profile = None
                st.session_state.demo_mode = False
                # Clear any cached data
                if "n1_df" in st.session_state:
                    del st.session_state.n1_df
                st.rerun()


def require_authentication(auth_manager: AuthManager):
    """
    Check if user is authenticated, show login page if not
    Returns True if authenticated, False otherwise
    """
    init_session_state()
    
    if not st.session_state.get("authenticated", False):
        show_login_page(auth_manager)
        return False
    
    return True

