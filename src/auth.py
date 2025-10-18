"""
Authentication module for Pain Relief Map
Handles user registration, login, and session management
"""
import os
from typing import Optional, Dict, Any
import streamlit as st
from supabase import create_client, Client
from datetime import datetime

class AuthManager:
    """Manages user authentication and sessions"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        
        if not supabase_url or not supabase_key:
            self.supabase = None
            self.enabled = False
        else:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.enabled = True
    
    def is_enabled(self) -> bool:
        """Check if authentication is enabled"""
        return self.enabled
    
    def signup(self, email: str, password: str, display_name: str = "") -> Dict[str, Any]:
        """
        Register a new user
        
        Returns:
            dict: {"success": bool, "message": str, "user": dict or None}
        """
        if not self.enabled:
            return {
                "success": False, 
                "message": "Authentication not configured. Check your .env file.",
                "user": None
            }
        
        try:
            # Sign up with Supabase Auth
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if response.user:
                # Create user profile in database
                profile_data = {
                    "user_id": response.user.id,
                    "email": email,
                    "display_name": display_name or email.split("@")[0],
                    "created_at": datetime.utcnow().isoformat(),
                }
                
                self.supabase.table("user_profiles").insert(profile_data).execute()
                
                return {
                    "success": True,
                    "message": "Account created! Please check your email to verify your account.",
                    "user": response.user
                }
            else:
                return {
                    "success": False,
                    "message": "Could not create account. Please try again.",
                    "user": None
                }
                
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower():
                return {
                    "success": False,
                    "message": "This email is already registered. Please login instead.",
                    "user": None
                }
            return {
                "success": False,
                "message": f"Error: {error_msg}",
                "user": None
            }
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login existing user
        
        Returns:
            dict: {"success": bool, "message": str, "user": dict or None}
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "Authentication not configured. Check your .env file.",
                "user": None
            }
        
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            
            if response.user:
                # Get user profile
                profile = self.supabase.table("user_profiles")\
                    .select("*")\
                    .eq("user_id", response.user.id)\
                    .single()\
                    .execute()
                
                return {
                    "success": True,
                    "message": "Login successful!",
                    "user": response.user,
                    "profile": profile.data if profile else None
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid credentials.",
                    "user": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Login failed: {str(e)}",
                "user": None
            }
    
    def logout(self) -> Dict[str, Any]:
        """Logout current user"""
        if not self.enabled:
            return {"success": False, "message": "Authentication not enabled"}
        
        try:
            self.supabase.auth.sign_out()
            return {"success": True, "message": "Logged out successfully"}
        except Exception as e:
            return {"success": False, "message": f"Logout error: {str(e)}"}
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get currently logged-in user"""
        if not self.enabled:
            return None
        
        try:
            user = self.supabase.auth.get_user()
            return user.user if user else None
        except:
            return None
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        if not self.enabled:
            return {"success": False, "message": "Authentication not enabled"}
        
        try:
            self.supabase.auth.reset_password_for_email(email)
            return {
                "success": True,
                "message": "Password reset email sent! Check your inbox."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        if not self.enabled:
            return {"success": False, "message": "Authentication not enabled"}
        
        try:
            response = self.supabase.table("user_profiles")\
                .update(updates)\
                .eq("user_id", user_id)\
                .execute()
            
            return {
                "success": True,
                "message": "Profile updated successfully",
                "data": response.data
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating profile: {str(e)}"
            }


def init_session_state():
    """Initialize session state for authentication"""
    if "auth_initialized" not in st.session_state:
        st.session_state.auth_initialized = True
        st.session_state.user = None
        st.session_state.user_profile = None
        st.session_state.authenticated = False


def require_auth():
    """Decorator to require authentication for a page"""
    if not st.session_state.get("authenticated", False):
        st.warning("Please login to access this page")
        st.stop()

