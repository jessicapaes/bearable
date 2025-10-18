# 🔐 Authentication Setup Guide for Pain Relief Map

This guide will help you add user authentication and database storage to your Pain Relief Map app.

## 📋 Overview

The authentication system includes:
- **User login/signup** with email verification
- **Secure password handling** via Supabase Auth
- **Database storage** for user-specific health logs
- **Row-level security** (users only see their own data)
- **Demo mode** for testing without signup

## 🚀 Quick Start (5 steps)

### Step 1: Create Supabase Account

1. Go to https://supabase.com and sign up (free tier available)
2. Click "New Project"
3. Fill in:
   - **Project Name**: `painreliefmap`
   - **Database Password**: (save this!)
   - **Region**: Choose closest to you
4. Wait 2-3 minutes for project to initialize

### Step 2: Set Up Database Tables

1. In your Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy the entire contents of `scripts/create_user_tables.sql`
4. Paste into the SQL editor
5. Click **Run** (bottom right)
6. You should see "Success" - tables are now created!

### Step 3: Get Your API Credentials

1. In Supabase dashboard, go to **Settings** → **API**
2. Find these two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public key** (long string starting with `eyJ...`)
3. Keep these safe - you'll need them next

### Step 4: Configure Environment Variables

1. Copy `config.env.example` to `.env` in your project root
2. Open `.env` and fill in your credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

3. Save the file

### Step 5: Install Required Package (if needed)

```bash
pip install python-dotenv
```

### Step 6: Run the Authenticated App

```bash
python -m streamlit run app/app_v4_auth.py
```

Or use the new version integrated into app_v3.py (see integration guide below).

## 🔧 Integration into Existing App

To add authentication to your existing `app_v3.py`:

### Option A: Use the Pre-Built Authenticated App

Simply run:
```bash
python -m streamlit run app/app_v4_auth.py
```

This is a complete version with authentication already integrated.

### Option B: Manually Integrate into app_v3.py

Add these lines at the beginning of `app_v3.py` (after imports):

```python
# Add after existing imports
import os
from dotenv import load_dotenv
from src.auth import AuthManager, init_session_state
from src.login_ui import require_authentication, show_user_menu
from src.db_operations import DatabaseManager

# Load environment variables
load_dotenv()

# Initialize auth and database
auth_manager = AuthManager()
db_manager = DatabaseManager()

# Initialize session state
init_session_state()

# Require authentication (shows login page if not logged in)
if not require_authentication(auth_manager):
    st.stop()  # Stop rendering rest of app until logged in

# Show user menu in sidebar
show_user_menu(auth_manager)
```

Then update the data loading section to load from database:

```python
# Replace session_state data loading with database loading
if not st.session_state.get("demo_mode"):
    user_id = st.session_state.user.get("id")
    st.session_state.n1_df = db_manager.get_user_logs(user_id)
else:
    # Demo mode: use session state as before
    if "n1_df" not in st.session_state:
        st.session_state.n1_df = pd.DataFrame(columns=DEFAULT_COLS)
```

Update the data saving function:

```python
def _append_row(row: dict):
    if not st.session_state.get("demo_mode"):
        # Save to database
        user_id = st.session_state.user.get("id")
        result = db_manager.save_log(user_id, row)
        
        if result["success"]:
            # Reload data from database
            st.session_state.n1_df = db_manager.get_user_logs(user_id)
        else:
            st.error(f"Error saving: {result['message']}")
    else:
        # Demo mode: use session state (original code)
        rec = {
            "date": pd.to_datetime(row["date"]),
            # ... rest of original code
        }
        st.session_state.n1_df = pd.concat([...])
```

## 📊 Database Schema

Your Supabase database will have these tables:

### `user_profiles`
- `id` - Auto-increment primary key
- `user_id` - UUID from Supabase Auth
- `email` - User's email
- `display_name` - How user wants to be called
- `created_at` - Account creation timestamp

### `user_logs`
- `id` - Auto-increment primary key
- `user_id` - Links to auth user
- `log_date` - Date of entry (unique per user per day)
- `pain_score`, `stress_score`, etc. - All health metrics
- `condition_today` - Conditions felt
- `therapy_used` - Therapies used
- `therapy_on`, `therapy_name` - For N-of-1 tracking

### `user_therapies`
- `id` - Auto-increment primary key
- `user_id` - Links to auth user
- `therapy_name` - Name of therapy
- `start_date`, `end_date` - Therapy period
- `is_active` - Whether therapy is ongoing

## 🔒 Security Features

### Row Level Security (RLS)
- Automatic: Users can **only access their own data**
- Implemented at database level (Supabase)
- Cannot be bypassed from client-side code

### Password Security
- Passwords hashed with bcrypt
- Managed by Supabase Auth
- Your app never sees plain-text passwords

### Email Verification
- New users receive verification email
- Prevents spam registrations
- Can be required before full access

## 🎭 Demo Mode

Demo mode allows users to try the app without creating an account:
- Data stored in session state only (not database)
- Disappears when browser is closed
- Perfect for testing or public demos
- Users can "upgrade" to real account anytime

## 📁 File Structure

```
painreliefmap/
├── app/
│   ├── app_v3.py              # Original app (no auth)
│   └── app_v4_auth.py         # New app with auth
├── src/
│   ├── auth.py                # Authentication logic
│   ├── login_ui.py            # Login/signup UI components
│   ├── db_operations.py       # Database CRUD operations
│   └── db.py                  # Original database module
├── scripts/
│   └── create_user_tables.sql # Database schema
├── config.env.example         # Template for credentials
├── .env                       # Your credentials (create this)
└── AUTHENTICATION_SETUP.md    # This file
```

## 🐛 Troubleshooting

### "Authentication not configured" error
**Fix**: Check your `.env` file exists and has correct credentials

### "Failed to fetch" or import errors
**Fix**: Install missing package:
```bash
pip install python-dotenv supabase
```

### "Table doesn't exist" error
**Fix**: Run the SQL schema in Supabase SQL Editor again

### Users can't sign up
**Fix**: Check Supabase Auth settings:
1. Go to **Authentication** → **Providers**
2. Make sure **Email** is enabled
3. Check **Email Confirmations** setting

### Data not saving
**Fix**: 
1. Check RLS policies are created (in the SQL schema)
2. Verify `SUPABASE_KEY` is the **anon** key, not service key
3. Check browser console for errors

## 🔄 Migration from Session State to Database

To migrate existing users' data:

1. Export current session data to CSV
2. User logs in for first time
3. Show "Import Previous Data" option
4. Let user upload their CSV
5. Import data with `db_manager.save_log()` for each row

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Click "New app"
4. Select your repo
5. Add secrets in dashboard:
   - Go to **Advanced settings** → **Secrets**
   - Add:
   ```toml
   SUPABASE_URL = "your-url"
   SUPABASE_KEY = "your-key"
   ```

### Deploy to other platforms (Heroku, Railway, etc.)

Set environment variables in platform's dashboard:
- `SUPABASE_URL`
- `SUPABASE_KEY`

## 📚 API Reference

### AuthManager

```python
auth = AuthManager()

# Sign up new user
result = auth.signup(email, password, display_name)

# Login
result = auth.login(email, password)

# Logout
auth.logout()

# Get current user
user = auth.get_current_user()

# Reset password
result = auth.reset_password(email)
```

### DatabaseManager

```python
db = DatabaseManager()

# Save log entry
result = db.save_log(user_id, log_data_dict)

# Get user's logs as DataFrame
df = db.get_user_logs(user_id, start_date, end_date)

# Delete log
result = db.delete_log(user_id, log_date)

# Get statistics
stats = db.get_user_stats(user_id)
```

## 💡 Tips

1. **Start with demo mode** to test everything works
2. **Backup database** regularly (Supabase has automatic backups)
3. **Monitor usage** in Supabase dashboard (free tier has limits)
4. **Add custom fields** by modifying SQL schema
5. **Export data** before major changes

## 🆘 Need Help?

- Supabase Docs: https://supabase.com/docs
- Streamlit Docs: https://docs.streamlit.io
- Check issues in GitHub repository

## 🎉 You're Done!

Your app now has:
✅ Secure user authentication
✅ Database storage for each user  
✅ Privacy with row-level security  
✅ Demo mode for testing  
✅ Export/import functionality

Users can now create accounts and their symptom logs will be saved permanently!

