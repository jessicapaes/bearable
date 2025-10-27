# 🧪 Start Here: End-to-End Testing Guide

**Quick Start:** Follow these 3 simple steps to test your Bearable app!

---

## 📁 Your Testing Files

| File | Purpose | Open This... |
|------|---------|--------------|
| **`TESTING_SUMMARY_E2E.md`** | 📊 Overview & Results | To understand what was tested |
| **`MANUAL_TEST_PLAN_E2E.md`** | ✅ Step-by-Step Guide | **TO ACTUALLY DO THE TESTING** |
| **`test_e2e_user_journey.py`** | 🤖 Automated Script | (Already ran - see results) |
| **`TEST_REPORT_E2E_*.md`** | 📄 Auto Test Results | For technical details |

---

## 🚀 3 Steps to Complete Testing

### Step 1: Read the Summary (5 min)
```bash
# Open this to understand what's being tested
open TESTING_SUMMARY_E2E.md
```

**What you'll learn:**
- What was tested automatically (40%)
- What needs manual testing (60%)
- Expected results for each test
- How long it will take (~2-3 hours)

---

### Step 2: Execute the Manual Tests (2-3 hours)
```bash
# This is your main test plan - follow it step by step
open MANUAL_TEST_PLAN_E2E.md
```

**What you'll do:**
1. Create 2 user accounts
2. Log 66 entries for User 1 (Yoga therapy)
3. Log 66 entries for User 2 (Acupuncture therapy)
4. Verify all features work
5. Check data isolation between users

**Tips:**
- Use 2 real email addresses you can access
- Set aside 2-3 hours of uninterrupted time
- Check off each box as you complete it
- Take screenshots of key features
- Make notes of any issues

---

### Step 3: Review & Sign Off (15 min)
When done, complete the sign-off section at the end of the manual test plan:
- Count total tests passed/failed
- Document any issues found
- Attach screenshots
- Export CSV files for verification

---

## 🎯 Quick Reference

### Test Objectives
- ✅ 132 total log entries (66 per user)
- ✅ Baseline period (30 days, no therapy)
- ✅ Therapy period (36 days, with therapy)
- ✅ Therapy effectiveness analysis
- ✅ Data isolation (RLS)
- ✅ Evidence Explorer APIs
- ✅ Data export

### What's Already Done
- ✅ Supabase configured
- ✅ RLS policies installed
- ✅ App running
- ✅ Test plan created
- ✅ Test data patterns defined

### What You Need to Do
- ⏳ Manual testing (follow the plan)
- ⏳ Document results
- ⏳ Sign off

---

## 📊 Expected Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| **Preparation** | 10 min | Read summary & plan |
| **User 1 Setup** | 10 min | Create account, verify email |
| **User 1 Baseline** | 45 min | Log 30 baseline entries |
| **User 1 Therapy** | 50 min | Log 36 therapy entries |
| **User 1 Review** | 10 min | Check dashboard & analysis |
| **User 2 Setup** | 10 min | Create account, verify email |
| **User 2 Baseline** | 45 min | Log 30 baseline entries |
| **User 2 Therapy** | 50 min | Log 36 therapy entries |
| **User 2 Review** | 10 min | Check dashboard & analysis |
| **Final Testing** | 20 min | Evidence Explorer, export, RLS |
| **Documentation** | 15 min | Complete sign-off |
| **TOTAL** | **~4 hours** | |

**Note:** Times are estimates. You can speed up by using "Copy Yesterday" feature!

---

## 🎬 Getting Started Now

### 1. Make sure app is running:
```bash
streamlit run app/app_v27_final.py
```
**Open:** http://localhost:8502

### 2. Open the test plan:
```bash
# Windows
start MANUAL_TEST_PLAN_E2E.md

# Mac
open MANUAL_TEST_PLAN_E2E.md

# Linux
xdg-open MANUAL_TEST_PLAN_E2E.md
```

### 3. Follow the checklist!
Start with **Test Case 1.1: Account Creation** and work your way down.

---

## 💡 Pro Tips

### Speed Up Testing
1. **Use "Copy Yesterday"** button to duplicate entries quickly
2. **Batch similar entries** - log same values for multiple days
3. **Take breaks** between users to avoid fatigue
4. **Screenshots as you go** - don't wait until the end

### Data Entry Shortcuts
```
Baseline Template (copy-paste):
Pain: 7-8
Sleep: 5-6 hours
Mood: 4-5
Stress: 7-8
Movement: Minimal
Notes: "Baseline day X/30"

Therapy Template (copy-paste):
Pain: 4-5
Sleep: 7-8 hours
Mood: 7-8
Stress: 4-5
Movement: Active
Therapy: Yoga (or Acupuncture)
Notes: "Week X - feeling better!"
```

---

## ❓ FAQ

**Q: Do I really need 132 entries?**  
A: Yes! 60+ per user is needed to properly test therapy analysis (30 baseline + 36 therapy).

**Q: Can I use fake emails?**  
A: No, Supabase will send verification emails. Use real emails you can access.

**Q: How long does this really take?**  
A: 2-4 hours depending on your speed. Use shortcuts to go faster!

**Q: What if I find bugs?**  
A: Document them in the "Issues Found" section of the manual test plan.

**Q: Can I test in multiple sessions?**  
A: Yes! The app saves your data. You can logout and come back later.

---

## ✅ Success Criteria

### You're done when:
- ☐ Both users have 60+ entries each
- ☐ Dashboard shows clear therapy effects
- ☐ Both therapies show improvement (30%+ pain reduction)
- ☐ Users can't see each other's data
- ☐ CSV exports work correctly
- ☐ Evidence Explorer loads live data
- ☐ All test cases marked PASS or FAIL
- ☐ Final sign-off completed

---

## 🆘 Need Help?

### If something doesn't work:
1. Check `SUPABASE_SETUP_COMPLETE.md` - is everything configured?
2. Check browser console (F12) for errors
3. Try logging out and back in
4. Restart the Streamlit app

### Common Issues:
- **"Can't login"** → Check email verification
- **"Data not saving"** → Check RLS policies are installed
- **"Can't see dashboard"** → Need at least 3 days of data
- **"Analysis not showing"** → Need at least 10 days after therapy start

---

## 🎉 Ready to Test!

**Your mission:** Validate that Bearable can track health data, analyze therapy effectiveness, and maintain user privacy.

**Time required:** 2-4 hours  
**Difficulty:** Easy (just follow the checklist)  
**Reward:** A fully tested, production-ready health tracking app! 🐻💜

---

**👉 START HERE:** Open `MANUAL_TEST_PLAN_E2E.md` and begin with Test Case 1.1!

Good luck! 🚀

