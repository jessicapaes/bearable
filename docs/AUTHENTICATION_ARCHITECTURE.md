# 🏗️ Authentication System Architecture

## Overview

The Pain Relief Map authentication system provides secure, multi-user support with personal data isolation. Each user has their own account and can only access their own health logs.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   Streamlit Frontend                        │ │
│  │  • Login/Signup UI (src/login_ui.py)                       │ │
│  │  • Dashboard, Daily Log, Settings                          │ │
│  └────────────┬──────────────────────────────────┬────────────┘ │
└───────────────┼──────────────────────────────────┼──────────────┘
                │                                  │
                │ Authentication                   │ Data Operations
                │ Requests                         │ (CRUD)
                ▼                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                     Python Backend                                │
│  ┌──────────────────────────┐    ┌─────────────────────────────┐ │
│  │   AuthManager            │    │   DatabaseManager           │ │
│  │   (src/auth.py)          │    │   (src/db_operations.py)    │ │
│  │                          │    │                             │ │
│  │  • signup()              │    │  • save_log()               │ │
│  │  • login()               │    │  • get_user_logs()          │ │
│  │  • logout()              │    │  • delete_log()             │ │
│  │  • reset_password()      │    │  • get_user_stats()         │ │
│  └────────────┬─────────────┘    └──────────────┬──────────────┘ │
└───────────────┼──────────────────────────────────┼────────────────┘
                │                                  │
                │ Supabase                         │ Supabase
                │ Auth API                         │ Database API
                ▼                                  ▼
┌───────────────────────────────────────────────────────────────────┐
│                         Supabase Cloud                            │
│  ┌──────────────────────────┐    ┌─────────────────────────────┐ │
│  │   Authentication         │    │   PostgreSQL Database       │ │
│  │                          │    │                             │ │
│  │  • User Management       │    │  • user_profiles            │ │
│  │  • Email Verification    │    │  • user_logs                │ │
│  │  • Password Hashing      │    │  • user_therapies           │ │
│  │  • Session Tokens        │    │  • Row Level Security (RLS) │ │
│  └──────────────────────────┘    └─────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Registration Flow

```
User fills signup form
    │
    ▼
login_ui.py validates input
    │
    ▼
AuthManager.signup(email, password, name)
    │
    ▼
Supabase Auth creates user
    │
    ├─► Sends verification email
    │
    ▼
DatabaseManager creates user_profile record
    │
    ▼
Success! User can now login (after email verification)
```

### 2. Login Flow

```
User enters credentials
    │
    ▼
AuthManager.login(email, password)
    │
    ▼
Supabase Auth verifies credentials
    │
    ▼
Returns user object + session token
    │
    ▼
Session state updated:
  • st.session_state.authenticated = True
  • st.session_state.user = user_object
    │
    ▼
App loads user's data from database
```

### 3. Data Logging Flow

```
User fills daily log form
    │
    ▼
Form submission triggers save_user_log()
    │
    ├─► Demo mode? ─Yes─► Save to session state
    │                     (temporary)
    │
    └─► Database mode
            │
            ▼
        DatabaseManager.save_log(user_id, log_data)
            │
            ▼
        Supabase inserts/updates record
            │
            ├─► RLS Policy checks user_id matches
            │
            ▼
        Success! Data saved to user_logs table
            │
            ▼
        Reload user data from database
```

### 4. Data Retrieval Flow

```
App needs to display user data
    │
    ▼
DatabaseManager.get_user_logs(user_id, start_date, end_date)
    │
    ▼
Supabase queries user_logs table
    │
    ├─► RLS Policy: WHERE user_id = auth.uid()
    │   (Only returns current user's data)
    │
    ▼
Returns DataFrame with user's logs
    │
    ▼
App displays data in dashboard/charts
```

## Security Layers

### 1. Client-Side (Streamlit)
- Input validation
- Session state management
- Requires authentication before showing app

### 2. Application Layer (Python)
- Auth tokens validated on each request
- User ID extracted from session
- All database calls include user_id parameter

### 3. Database Layer (Supabase)
- **Row Level Security (RLS)** enforced
- Policies ensure `user_id = auth.uid()`
- Cannot be bypassed from client
- Even with direct database access, users only see their data

### 4. Authentication Layer (Supabase Auth)
- Passwords hashed with bcrypt
- Email verification required
- Session tokens expire automatically
- Password reset via email only

## File Structure & Responsibilities

```
painreliefmap/
│
├── app/
│   ├── app_v3.py              # Original app (no auth)
│   └── app_v4_auth.py         # ✨ New! Authenticated version
│
├── src/
│   ├── __init__.py
│   ├── auth.py                # ✨ Authentication logic
│   │   └── AuthManager class
│   │       • Wraps Supabase Auth API
│   │       • Handles signup, login, logout
│   │       • Manages user sessions
│   │
│   ├── login_ui.py            # ✨ Login/signup UI
│   │   • show_login_page()
│   │   • show_user_menu()
│   │   • require_authentication()
│   │
│   ├── db_operations.py       # ✨ Database operations
│   │   └── DatabaseManager class
│   │       • save_log() - Create/update logs
│   │       • get_user_logs() - Retrieve logs
│   │       • delete_log() - Remove logs
│   │       • get_user_stats() - Calculate stats
│   │
│   ├── causal.py              # Existing: Statistical analysis
│   └── db.py                  # Existing: Evidence database
│
├── scripts/
│   └── create_user_tables.sql # ✨ Database schema
│       • user_profiles table
│       • user_logs table
│       • user_therapies table
│       • RLS policies
│       • Indexes & triggers
│
├── data/
│   └── templates/
│       └── n_of_1_demo.csv    # Demo data for testing
│
├── config.env.example         # ✨ Template for credentials
├── .env                       # ✨ Your actual credentials (create this)
│
└── docs/
    ├── QUICKSTART_AUTH.md     # ✨ 5-minute setup guide
    ├── AUTHENTICATION_SETUP.md # ✨ Detailed setup guide
    └── AUTHENTICATION_ARCHITECTURE.md # ✨ This file
```

## Database Schema

### Table: `user_profiles`

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Purpose**: Store additional user information beyond Supabase Auth

### Table: `user_logs`

```sql
CREATE TABLE user_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    log_date DATE NOT NULL,
    
    -- Core symptoms
    pain_score INT CHECK (pain_score BETWEEN 0 AND 10),
    stress_score INT CHECK (stress_score BETWEEN 0 AND 10),
    anxiety_score INT CHECK (anxiety_score BETWEEN 0 AND 10),
    mood_score INT CHECK (mood_score BETWEEN 0 AND 10),
    sleep_hours DECIMAL(3,1),
    
    -- Conditions & therapies
    condition_today TEXT,
    therapy_used TEXT,
    therapy_on INT DEFAULT 0,
    therapy_name VARCHAR(200),
    
    -- Other fields...
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, log_date)  -- One entry per user per day
);
```

**Purpose**: Store daily health logs for each user

### Table: `user_therapies`

```sql
CREATE TABLE user_therapies (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    therapy_name VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Purpose**: Track therapy sessions and their durations

## Row Level Security (RLS) Policies

### User Profiles

```sql
-- Users can view their own profile
CREATE POLICY "Users can view their own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = user_id);

-- Users can update their own profile
CREATE POLICY "Users can update their own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = user_id);
```

### User Logs

```sql
-- Users can only see their own logs
CREATE POLICY "Users can view their own logs"
    ON user_logs FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert logs with their user_id
CREATE POLICY "Users can insert their own logs"
    ON user_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);
```

**Key Point**: These policies are enforced at the database level and cannot be bypassed from the application code.

## Session Management

### Session State Variables

```python
st.session_state.authenticated     # Boolean: Is user logged in?
st.session_state.user               # Dict: User object from Supabase
st.session_state.user_profile       # Dict: User profile data
st.session_state.demo_mode          # Boolean: Is in demo mode?
st.session_state.n1_df              # DataFrame: User's health logs
```

### Session Lifecycle

1. **Initial State**: All variables are `None` or `False`
2. **After Login**: `authenticated` = `True`, `user` populated
3. **Data Loaded**: `n1_df` populated from database
4. **After Logout**: All cleared, redirect to login page

## API Integration

### Supabase Auth API

```python
# Create client
supabase = create_client(supabase_url, supabase_key)

# Sign up
response = supabase.auth.sign_up({
    "email": email,
    "password": password
})

# Sign in
response = supabase.auth.sign_in_with_password({
    "email": email,
    "password": password
})

# Sign out
supabase.auth.sign_out()

# Get current user
user = supabase.auth.get_user()
```

### Supabase Database API

```python
# Insert
response = supabase.table("user_logs").insert(data).execute()

# Update (upsert)
response = supabase.table("user_logs")\
    .upsert(data, on_conflict="user_id,log_date")\
    .execute()

# Select
response = supabase.table("user_logs")\
    .select("*")\
    .eq("user_id", user_id)\
    .gte("log_date", start_date)\
    .order("log_date")\
    .execute()

# Delete
response = supabase.table("user_logs")\
    .delete()\
    .eq("user_id", user_id)\
    .eq("log_date", log_date)\
    .execute()
```

## Demo Mode

Demo mode allows users to test the app without creating an account.

### How It Works

1. User clicks "Continue in Demo Mode"
2. `st.session_state.demo_mode = True`
3. Fake user object created: `{"id": "demo-user", ...}`
4. Data stored in session state instead of database
5. Data is lost when browser closes

### When to Use

- Testing the app
- Public demos
- Users want to try before signing up
- Development/debugging

## Environment Variables

```env
# Required for authentication
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOi...

# Optional
APP_MODE=production
DEBUG=False
DEMO_MODE=False
```

### How They're Loaded

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
```

## Error Handling

### Authentication Errors

- Invalid credentials → Show error message
- Email not verified → Prompt to check email
- Weak password → Show requirements
- Duplicate email → Suggest login instead

### Database Errors

- Connection failed → Show friendly message
- Duplicate entry → Use upsert to update instead
- Permission denied → Check RLS policies
- Timeout → Retry with exponential backoff

### User-Friendly Messages

```python
# Bad
"Error: 23505 duplicate key value violates unique constraint"

# Good
"You already have an entry for this date. Your entry has been updated!"
```

## Performance Optimizations

1. **Caching**: Use `@st.cache_data` for evidence data
2. **Lazy Loading**: Only load data when needed
3. **Pagination**: Load recent logs first
4. **Indexes**: Database indexes on `user_id` and `log_date`
5. **Session State**: Cache user data in session

## Deployment Considerations

### Streamlit Cloud

```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "eyJhbG..."
```

### Other Platforms (Heroku, Railway, etc.)

Set environment variables in platform dashboard:
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Security Checklist

- [ ] Use **anon** key (not service_role key)
- [ ] Enable RLS on all tables
- [ ] Require email verification
- [ ] Use HTTPS in production
- [ ] Set password strength requirements
- [ ] Rate limit authentication endpoints
- [ ] Monitor for suspicious activity
- [ ] Regular database backups

## Testing

### Manual Testing

1. **Sign Up Flow**
   - Valid email/password → Success
   - Duplicate email → Error message
   - Weak password → Error message

2. **Login Flow**
   - Valid credentials → Success
   - Wrong password → Error message
   - Unverified email → Prompt to verify

3. **Data Isolation**
   - Create two accounts
   - Add logs to each
   - Verify each only sees their own data

4. **Demo Mode**
   - Click demo mode
   - Add data
   - Close browser
   - Reopen → Data gone ✓

### Automated Testing

```python
# Example test
def test_user_can_only_see_own_data():
    # Create user 1
    user1 = create_test_user("user1@test.com")
    
    # Create user 2
    user2 = create_test_user("user2@test.com")
    
    # User 1 adds log
    add_log(user1.id, {"pain_score": 5})
    
    # User 2 queries logs
    logs = get_logs(user2.id)
    
    # Assert user 2 doesn't see user 1's data
    assert len(logs) == 0
```

## Future Enhancements

- [ ] Social login (Google, Apple)
- [ ] Two-factor authentication (2FA)
- [ ] Team/family accounts (share data with doctor/family)
- [ ] Export to PDF with charts
- [ ] Automated backup to user's cloud storage
- [ ] Mobile app (React Native + Supabase)
- [ ] Offline mode with sync
- [ ] Data encryption at rest (Supabase Pro feature)

## Resources

- Supabase Docs: https://supabase.com/docs
- Supabase Auth: https://supabase.com/docs/guides/auth
- Row Level Security: https://supabase.com/docs/guides/auth/row-level-security
- Streamlit Auth: https://blog.streamlit.io/streamlit-authenticator

---

**Questions?** Check [QUICKSTART_AUTH.md](../QUICKSTART_AUTH.md) or [AUTHENTICATION_SETUP.md](../AUTHENTICATION_SETUP.md)

