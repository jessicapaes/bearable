"""
Database operations for Pain Relief Map
Handles CRUD operations for user logs
"""
import os
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from supabase import create_client, Client


class DatabaseManager:
    """Manages database operations for user logs"""
    
    def __init__(self):
        """Initialize database connection"""
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        
        if not supabase_url or not supabase_key:
            self.supabase = None
            self.enabled = False
        else:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.enabled = True
    
    def is_enabled(self) -> bool:
        """Check if database is enabled"""
        return self.enabled
    
    def save_log(self, user_id: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save or update a daily log entry
        
        Args:
            user_id: User's UUID
            log_data: Dictionary containing log data
            
        Returns:
            dict: {"success": bool, "message": str, "data": dict or None}
        """
        if not self.enabled:
            return {"success": False, "message": "Database not configured"}
        
        try:
            # Prepare data for database
            db_data = {
                "user_id": user_id,
                "log_date": log_data.get("date"),
                "pain_score": int(log_data.get("pain_score", 0)),
                "stress_score": int(log_data.get("stress_score", 0)),
                "anxiety_score": int(log_data.get("anxiety_score", 0)),
                "patience_score": int(log_data.get("patience_score", 0)),
                "mood_score": int(log_data.get("mood_score", 0)),
                "sleep_hours": float(log_data.get("sleep_hours", 0)),
                "sex_at_birth": log_data.get("sex_at_birth", ""),
                "condition_today": ", ".join(log_data.get("condition_today", [])) if isinstance(log_data.get("condition_today"), list) else log_data.get("condition_today", ""),
                "therapy_used": ", ".join(log_data.get("therapy_used", [])) if isinstance(log_data.get("therapy_used"), list) else log_data.get("therapy_used", ""),
                "movement": ", ".join(log_data.get("movement", [])) if isinstance(log_data.get("movement"), list) else log_data.get("movement", ""),
                "bowel_movements_n": int(log_data.get("bowel_movements_n", 0)),
                "digestive_sounds": log_data.get("digestive_sounds", ""),
                "stool_consistency": log_data.get("stool_consistency", ""),
                "physical_symptoms": ", ".join(log_data.get("physical_symptoms", [])) if isinstance(log_data.get("physical_symptoms"), list) else log_data.get("physical_symptoms", ""),
                "emotional_symptoms": ", ".join(log_data.get("emotional_symptoms", [])) if isinstance(log_data.get("emotional_symptoms"), list) else log_data.get("emotional_symptoms", ""),
                "cravings": ", ".join(log_data.get("cravings", [])) if isinstance(log_data.get("cravings"), list) else log_data.get("cravings", ""),
                "menstruating_today": log_data.get("menstruating_today", False) in ["Yes", True],
                "cycle_day": int(log_data.get("cycle_day", 0)) if log_data.get("cycle_day") else None,
                "flow": log_data.get("flow", ""),
                "pms_symptoms": ", ".join(log_data.get("pms_symptoms", [])) if isinstance(log_data.get("pms_symptoms"), list) else log_data.get("pms_symptoms", ""),
                "therapy_on": int(log_data.get("therapy_on", 0)),
                "therapy_name": log_data.get("therapy_name", ""),
                "good_day": bool(log_data.get("good_day", False)),
                "notes": log_data.get("notes", ""),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            # Use upsert to insert or update if date already exists
            response = self.supabase.table("user_logs")\
                .upsert(db_data, on_conflict="user_id,log_date")\
                .execute()
            
            return {
                "success": True,
                "message": "Log saved successfully",
                "data": response.data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error saving log: {str(e)}",
                "data": None
            }
    
    def get_user_logs(self, user_id: str, start_date: Optional[date] = None, 
                     end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Retrieve user's logs as a DataFrame
        
        Args:
            user_id: User's UUID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            DataFrame: User's logs
        """
        if not self.enabled:
            return pd.DataFrame()
        
        try:
            query = self.supabase.table("user_logs")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("log_date", desc=False)
            
            if start_date:
                query = query.gte("log_date", start_date.isoformat())
            if end_date:
                query = query.lte("log_date", end_date.isoformat())
            
            response = query.execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                # Rename log_date to date to match app expectations
                if "log_date" in df.columns:
                    df["date"] = pd.to_datetime(df["log_date"])
                    df = df.drop(columns=["log_date"])
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error retrieving logs: {str(e)}")
            return pd.DataFrame()
    
    def delete_log(self, user_id: str, log_date: date) -> Dict[str, Any]:
        """
        Delete a specific log entry
        
        Args:
            user_id: User's UUID
            log_date: Date of log to delete
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        if not self.enabled:
            return {"success": False, "message": "Database not configured"}
        
        try:
            response = self.supabase.table("user_logs")\
                .delete()\
                .eq("user_id", user_id)\
                .eq("log_date", log_date.isoformat())\
                .execute()
            
            return {
                "success": True,
                "message": "Log deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting log: {str(e)}"
            }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a user
        
        Args:
            user_id: User's UUID
            
        Returns:
            dict: User statistics
        """
        if not self.enabled:
            return {}
        
        try:
            df = self.get_user_logs(user_id)
            
            if df.empty:
                return {
                    "total_logs": 0,
                    "avg_pain": 0,
                    "avg_stress": 0,
                    "avg_sleep": 0,
                    "first_log": None,
                    "last_log": None
                }
            
            return {
                "total_logs": len(df),
                "avg_pain": df["pain_score"].mean() if "pain_score" in df else 0,
                "avg_stress": df["stress_score"].mean() if "stress_score" in df else 0,
                "avg_sleep": df["sleep_hours"].mean() if "sleep_hours" in df else 0,
                "first_log": df["date"].min() if "date" in df else None,
                "last_log": df["date"].max() if "date" in df else None,
            }
            
        except Exception as e:
            print(f"Error getting user stats: {str(e)}")
            return {}
    
    def save_therapy(self, user_id: str, therapy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a therapy record
        
        Args:
            user_id: User's UUID
            therapy_data: Dictionary containing therapy data
            
        Returns:
            dict: {"success": bool, "message": str, "data": dict or None}
        """
        if not self.enabled:
            return {"success": False, "message": "Database not configured"}
        
        try:
            db_data = {
                "user_id": user_id,
                "therapy_name": therapy_data.get("therapy_name"),
                "start_date": therapy_data.get("start_date"),
                "end_date": therapy_data.get("end_date"),
                "is_active": therapy_data.get("is_active", True),
                "notes": therapy_data.get("notes", ""),
            }
            
            response = self.supabase.table("user_therapies")\
                .insert(db_data)\
                .execute()
            
            return {
                "success": True,
                "message": "Therapy saved successfully",
                "data": response.data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error saving therapy: {str(e)}",
                "data": None
            }
    
    def get_active_therapies(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's active therapies
        
        Args:
            user_id: User's UUID
            
        Returns:
            list: Active therapies
        """
        if not self.enabled:
            return []
        
        try:
            response = self.supabase.table("user_therapies")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("is_active", True)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error getting active therapies: {str(e)}")
            return []

