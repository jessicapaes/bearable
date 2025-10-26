# Deploying Bearable to Streamlit Cloud

## 🚀 Quick Deployment Guide

### Step 1: Prepare Your Repository

Ensure your GitHub repository is up to date:
```bash
git push origin main
```

### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository: `jessicapaes/bearable`
5. Choose branch: `main`
6. Set main file path: `app/app_v27_final.py`

### Step 3: Add Supabase Credentials (IMPORTANT!)

This is the critical step that fixes the "⚠️ Supabase credentials not found" error:

1. Before clicking "Deploy", click **"Advanced settings"**
2. Scroll to **"Secrets"** section
3. Add your Supabase credentials in TOML format:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key-here"
```

**Where to find these values:**
- Login to [supabase.com](https://supabase.com)
- Select your project
- Go to **Settings** → **API**
- Copy:
  - **Project URL** → Use as `SUPABASE_URL`
  - **anon public** key → Use as `SUPABASE_KEY`

### Step 4: Deploy!

1. Click **"Deploy"**
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## 🔧 Post-Deployment Configuration

### Updating Secrets After Deployment

If you need to change your Supabase credentials:

1. Go to your app on Streamlit Cloud
2. Click the **⚙️ Settings** button (top right)
3. Select **"Secrets"**
4. Update your credentials
5. Save → App will automatically restart

### Custom Domain (Optional)

1. Go to app settings
2. Select **"General"**
3. Add your custom domain
4. Follow DNS configuration instructions

---

## 📊 Monitoring Your Deployed App

### View Logs

1. Click **"Manage app"** on Streamlit Cloud
2. Select **"Logs"** tab
3. View real-time application logs

### Check Resource Usage

1. Go to app dashboard
2. View:
   - Active users
   - Memory usage
   - CPU usage
   - Request count

---

## 🐛 Troubleshooting

### "Supabase credentials not found"

**Cause:** Secrets not configured or incorrectly formatted

**Solution:**
1. Go to App Settings → Secrets
2. Verify format is TOML (not JSON or ENV):
   ```toml
   SUPABASE_URL = "https://..."
   SUPABASE_KEY = "eyJ..."
   ```
3. No extra spaces or quotes issues
4. Save and app will restart

### "Module not found"

**Cause:** Missing dependency in `requirements.txt`

**Solution:**
1. Update `requirements.txt` locally
2. Commit and push:
   ```bash
   git add requirements.txt
   git commit -m "Add missing dependency"
   git push origin main
   ```
3. Streamlit Cloud will auto-redeploy

### "App is sleeping"

**Cause:** Free tier apps sleep after inactivity

**Solution:**
- Click "Wake up" button
- Or upgrade to paid tier for always-on hosting

### "Out of memory"

**Cause:** App exceeds free tier limits (1GB RAM)

**Solution:**
1. Optimize data loading (use caching)
2. Reduce session state size
3. Consider upgrading to paid tier (more resources)

---

## 🔐 Security Best Practices

### Do NOT:
- ❌ Commit `.env` file to Git
- ❌ Share Streamlit secrets publicly
- ❌ Use admin/service role keys (use anon key only)
- ❌ Hardcode credentials in code

### Do:
- ✅ Use Streamlit secrets for deployment
- ✅ Use `.env` for local development only
- ✅ Add `.env` to `.gitignore`
- ✅ Use Supabase Row Level Security (RLS)
- ✅ Rotate keys if compromised

---

## 📈 Scaling & Performance

### Free Tier Limits
- **RAM:** 1 GB
- **CPU:** Shared
- **Apps:** 1 public app
- **Uptime:** Sleeps after inactivity

### Paid Tier Benefits
- **RAM:** Up to 16 GB
- **CPU:** Dedicated
- **Apps:** Unlimited
- **Uptime:** Always-on
- **Custom domains**
- **Priority support**

### Performance Tips

1. **Use Caching:**
   ```python
   @st.cache_data(ttl=3600)
   def load_data():
       # Expensive operation
   ```

2. **Optimize Database Queries:**
   - Use indexes in Supabase
   - Limit result sets
   - Cache frequent queries

3. **Lazy Load Data:**
   - Don't load everything on page load
   - Load data when tabs are selected
   - Paginate large datasets

---

## 🔄 Continuous Deployment

Streamlit Cloud automatically redeploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Streamlit Cloud auto-deploys in ~2 minutes
```

**Watch the deployment:**
1. Go to Streamlit Cloud dashboard
2. See deployment status in real-time
3. View logs for any errors

---

## 📱 Mobile Optimization

Your app is already mobile-responsive (v26+), but test on deployment:

1. Open your deployed app on mobile
2. Test all tabs and features
3. Check touch interactions
4. Verify responsive layouts

---

## 🎯 Production Checklist

Before going live:

- [ ] Supabase credentials added to Streamlit secrets
- [ ] Database tables created and migrated
- [ ] Row Level Security (RLS) enabled in Supabase
- [ ] Test signup/login flow
- [ ] Test daily log submission
- [ ] Test Evidence Explorer with live APIs
- [ ] Test on mobile devices
- [ ] Set up error monitoring
- [ ] Add Google Analytics (optional)
- [ ] Configure custom domain (optional)
- [ ] Set up backup strategy

---

## 📞 Support

**Streamlit Cloud Support:**
- Documentation: https://docs.streamlit.io/streamlit-community-cloud
- Community: https://discuss.streamlit.io
- Status: https://streamlitstatus.com

**Supabase Support:**
- Documentation: https://supabase.com/docs
- Community: https://github.com/supabase/supabase/discussions

**App-Specific Issues:**
- GitHub Issues: https://github.com/jessicapaes/bearable/issues

---

## 🎉 You're Live!

Once deployed, share your app:
- **URL:** `https://your-app-name.streamlit.app`
- **Share button:** Built into Streamlit UI
- **Embed:** Use iframe on your website
- **API:** No API, but you can integrate with Supabase directly

---

**Last Updated:** January 26, 2025  
**Version:** v27  
**Status:** Production Ready ✅

