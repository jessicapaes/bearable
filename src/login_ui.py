"""
Login and signup UI components for Streamlit
"""
import streamlit as st
from src.auth import AuthManager, init_session_state


def show_login_page(auth_manager: AuthManager):
    """Display login/signup page"""
    
    # Initialize session state
    init_session_state()
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #667eea; font-size: 2.5rem;">🐻 Bearable</h1>
            <p style="color: #7f8c8d; font-size: 1.1rem;">
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
        
        # Tabs for Login and Signup
        tab_login, tab_signup = st.tabs(["🔑 Login", "📝 Sign Up"])
        
        # LOGIN TAB
        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("### Welcome Back!")
                email = st.text_input("Email", key="login_email", placeholder="your.email@example.com")
                password = st.text_input("Password", type="password", key="login_password")
                
                col_submit, col_forgot = st.columns([1, 1])
                with col_submit:
                    submit = st.form_submit_button("Login", type="primary", use_container_width=True)
                
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
            
            # Forgot password
            with st.expander("🔒 Forgot Password?"):
                reset_email = st.text_input("Enter your email", key="reset_email")
                if st.button("Send Reset Link"):
                    if reset_email:
                        result = auth_manager.reset_password(reset_email)
                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
                    else:
                        st.warning("Please enter your email")
        
        # SIGNUP TAB
        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("### Create Your Account")
                st.caption("Start tracking your health journey today - free forever!")
                
                signup_name = st.text_input("Display Name", key="signup_name", placeholder="How should we call you?")
                signup_email = st.text_input("Email", key="signup_email", placeholder="your.email@example.com")
                signup_password = st.text_input("Password", type="password", key="signup_password", 
                                              help="At least 8 characters")
                signup_password2 = st.text_input("Confirm Password", type="password", key="signup_password2")
                
                agree = st.checkbox("I agree to store my health data securely", key="agree_terms")
                
                submit_signup = st.form_submit_button("Create Account", type="primary", use_container_width=True)
                
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
        st.markdown("---")
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

