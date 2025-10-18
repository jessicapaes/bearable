# 🚀 Quick Start: Add User Accounts in 5 Minutes

This guide gets you from "no authentication" to "working user login" in 5 minutes.

## ✅ What You Need

- [ ] A Supabase account (free at https://supabase.com)
- [ ] 5 minutes of time
- [ ] Your Pain Relief Map code

## 🎯 Step-by-Step

### 1️⃣ Create Supabase Project (2 min)

1. Go to https://supabase.com → **Start your project**
2. Create new project:
   - Name: `painreliefmap`
   - Database password: (save this!)
   - Region: Closest to you
3. Wait for setup to complete (~2 min)

### 2️⃣ Set Up Database (1 min)

1. In Supabase, click **SQL Editor** (left sidebar)
2. Click **New Query**
3. Copy-paste entire contents of `scripts/create_user_tables.sql`
4. Click **Run** ▶️
5. See "Success. No rows returned" ✅

### 3️⃣ Get Your Credentials (30 sec)

1. Click **Settings** ⚙️ (bottom left)
2. Click **API** 
3. Copy these:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public** key: `eyJhb...` (long string)

### 4️⃣ Configure Your App (30 sec)

1. In project root, create file named `.env`
2. Paste this (replace with your values):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOi...your-key-here
```

3. Save file

### 5️⃣ Install & Run (1 min)

```bash
# Install new dependency
pip install python-dotenv

# Run authenticated app
python -m streamlit run app/app_v4_auth.py
```

## 🎉 Done!

You should now see a **login page** when you open the app!

### Test It:

1. Click **Sign Up** tab
2. Enter:
   - Display name: Test User
   - Email: your@email.com
   - Password: (at least 8 characters)
   - Confirm password
3. Check "I agree to store my health data securely"
4. Click **Create Account**
5. Check your email for verification link
6. After verifying, go back and **Login**

### Or Try Demo Mode:

Click **Continue in Demo Mode** to test without signup.

## 🐛 Having Issues?

### "Authentication not configured"
- **Check**: Does `.env` file exist?
- **Check**: Are URLs/keys correct?
- **Fix**: Copy `.env` from `config.env.example` template

### "Failed to import dotenv"
```bash
pip install python-dotenv
```

### "Table doesn't exist"
- **Check**: Did you run the SQL in Step 2?
- **Fix**: Go to Supabase SQL Editor → Paste `create_user_tables.sql` → Run

### Can't signup
- **Check**: Email format is correct
- **Check**: Password is at least 8 characters
- **Check**: Check spam folder for verification email

## 📚 What Next?

### Want to integrate into your existing app_v3.py?

See full guide: [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)

### Want to customize?

Edit these files:
- `src/auth.py` - Authentication logic
- `src/login_ui.py` - Login page design  
- `src/db_operations.py` - Database operations
- `scripts/create_user_tables.sql` - Add custom fields

### Ready to deploy?

See deployment section in [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)

## 💡 Key Features You Now Have

✅ Secure user registration  
✅ Email verification  
✅ Password reset  
✅ Personal data storage  
✅ Row-level security (users only see their data)  
✅ Demo mode for testing  
✅ Export your data anytime  

## 🔐 Security Notes

- Passwords are hashed (never stored plain-text)
- Each user only sees their own data
- All managed by Supabase (enterprise-grade security)
- Your app never sees the actual password
- Data encrypted in transit and at rest

## 📞 Need Help?

- **Supabase Docs**: https://supabase.com/docs
- **Streamlit + Auth Tutorial**: https://blog.streamlit.io/streamlit-authenticator
- **Check**: [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) for detailed troubleshooting

---

**Total time**: ~5 minutes  
**Lines of code you wrote**: 3 (in .env file)  
**Users can now**: Create accounts, login, and save their health logs permanently! 🎉

