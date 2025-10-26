# 🚀 Deployment Guide - Bearable App

## 📋 Pre-Deployment Checklist

Before deploying to Streamlit Cloud, ensure you have:

- [x] Tested app locally (`streamlit run bearable.py`)
- [x] Created `requirements.txt`
- [x] Created `.streamlit/config.toml`
- [x] Created `.gitignore` (protects sensitive data)
- [x] Written comprehensive README.md
- [ ] Pushed code to GitHub
- [ ] Set up Streamlit Cloud account

---

## 🎯 Option 1: Streamlit Cloud (RECOMMENDED)

### Why Streamlit Cloud?
✅ **Free tier sufficient**  
✅ **10-minute deployment**  
✅ **No cold starts** (instant for demos!)  
✅ **Auto-deploys on git push**  
✅ **Perfect for academic projects**

### Step-by-Step Deployment

#### 1. Prepare Your GitHub Repository

```bash
# Navigate to your project
cd C:\Users\jessp\OneDrive\Education\AI Tech Institute Course\Repositories\painreliefmap

# Check git status
git status

# Add deployment files
git add bearable.py
git add requirements.txt
git add .streamlit/config.toml
git add .gitignore
git add README.md
git add DEPLOYMENT.md
git add app/bear_icon.svg

# Commit
git commit -m "Prepare Bearable for Streamlit Cloud deployment

- Add production-ready bearable.py
- Add requirements.txt with dependencies
- Add Streamlit config for theme
- Add comprehensive README
- Add deployment guide
- Update .gitignore to protect user data"

# Push to GitHub
git push origin main
```

#### 2. Deploy to Streamlit Cloud

1. **Go to:** https://share.streamlit.io

2. **Sign in with GitHub**
   - Click "Sign in with GitHub"
   - Authorize Streamlit Cloud

3. **Create New App**
   - Click "New app" button
   - Select your repository: `painreliefmap`
   - Branch: `main`
   - Main file path: `bearable.py`
   - App URL: Choose your custom URL (e.g., `bearable-health`)

4. **Click "Deploy!"** 🚀

5. **Wait 2-3 minutes** for initial build

6. **Your app is live!** 🎉
   - URL will be: `https://your-username-bearable-health.streamlit.app`

#### 3. Test Your Deployed App

- [ ] Home page loads correctly
- [ ] Login with demo/demo works
- [ ] Daily Log form submits
- [ ] Dashboard shows charts
- [ ] Evidence Explorer displays therapies
- [ ] Settings tab loads
- [ ] Logout button works
- [ ] Mobile responsive (check on phone)

#### 4. Update Your README

Once deployed, update your README.md with the actual URL:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-actual-url.streamlit.app)

## 🚀 Live Demo

Try the app: [https://your-actual-url.streamlit.app](https://your-actual-url.streamlit.app)
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Add missing package to `requirements.txt`

### Issue: "File not found: data/accounts.json"
**Solution:** The app creates this automatically on first run. Not an error.

### Issue: App is slow to load
**Solution:** 
- First load is always slower (Streamlit Cloud wakes up)
- Subsequent loads are instant
- This is normal behavior

### Issue: Changes not reflecting
**Solution:**
```bash
git add .
git commit -m "Update app"
git push origin main
# Wait 1-2 minutes for auto-deploy
```

### Issue: "Repository is private"
**Solution:** 
- Go to GitHub repo settings
- Change visibility to Public
- Or add Streamlit Cloud to collaborators

---

## 📊 Monitoring Your App

### View Logs
1. Go to https://share.streamlit.io
2. Click on your app
3. Click "Manage app"
4. View logs in real-time

### Check Analytics
- Streamlit Cloud shows you:
  - Number of visitors
  - App uptime
  - Resource usage

---

## 🔄 Updating Your Deployed App

Every time you push to GitHub, Streamlit Cloud auto-deploys:

```bash
# Make changes to bearable.py
# Test locally first!
streamlit run bearable.py

# Commit and push
git add bearable.py
git commit -m "Add new feature"
git push origin main

# Streamlit Cloud auto-deploys in 1-2 minutes!
```

---

## 🎓 For Your Presentation (Oct 28)

### Before Presentation Day:

1. **Test on multiple devices**
   - Your laptop
   - Your phone
   - A friend's computer

2. **Record backup video** (in case of internet issues)
   ```bash
   # Use OBS Studio or your phone
   # Record 3-minute demo walkthrough
   ```

3. **Prepare talking points:**
   - "This is Bearable, a health tracking app..."
   - "Let me log into the demo account..."
   - "Here's the dashboard showing pain trends..."
   - "Evidence Explorer shows research-backed therapies..."
   - "Everything is deployed on Streamlit Cloud..."

4. **Have backup plan:**
   - Backup video ready
   - Local version running (`streamlit run bearable.py`)
   - Screenshots in a PowerPoint

### During Presentation:

1. **Show live URL** (don't log in yet)
2. **Explain the problem** you're solving
3. **Log in with demo/demo**
4. **Walk through each tab** (Dashboard → Daily Log → Evidence)
5. **Show one data entry** in Daily Log
6. **Highlight technical achievements:**
   - "Real-time data visualization with Plotly"
   - "Secure authentication system"
   - "Deployed on Streamlit Cloud"
   - "Responsive design works on mobile"

---

## 📝 Deployment Checklist for Oct 28

- [ ] **Day 1 (Today)**: Deploy to Streamlit Cloud
- [ ] **Day 2**: Test thoroughly, fix any bugs
- [ ] **Day 3**: Update README with live URL
- [ ] **Day 4-5**: Add causal analysis (if time)
- [ ] **Day 6**: Record backup demo video
- [ ] **Day 7-8**: Practice presentation (out loud!)
- [ ] **Day 9**: Final testing, relax

---

## 🆘 Need Help?

### Streamlit Community
- Forum: https://discuss.streamlit.io
- Docs: https://docs.streamlit.io

### Common Commands

```bash
# Test locally
streamlit run bearable.py

# Check requirements
pip list

# Update package
pip install --upgrade streamlit

# Check Git status
git status

# View commit history
git log --oneline
```

---

## ✅ Final Verification

Before your presentation, verify:

- [x] App is live and accessible
- [x] Demo credentials work (demo/demo)
- [x] All features functional
- [x] README has live URL
- [x] GitHub repo is public
- [x] No sensitive data committed (.gitignore working)
- [x] Backup video recorded
- [x] Presentation practiced

---

**Good luck with your presentation! 🎉**

You've built an amazing app. Now go show it off! 🐻✨
