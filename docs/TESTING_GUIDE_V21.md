# Bearable v21 - Testing Guide

**Version:** v21_final  
**Date:** October 25, 2025  
**Purpose:** Comprehensive testing checklist for v21 implementation

---

## 🚀 PRE-TESTING SETUP

### 1. Database Setup
- [ ] Run SQL script: `scripts/create_user_logs_table.sql` in Supabase SQL Editor
- [ ] Verify table exists: Check Supabase Table Editor for `user_logs` table
- [ ] Verify RLS policies: Check "Policies" tab in Supabase

### 2. Environment Variables
Ensure these are set in your `.env` or `config.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_REDIRECT_URL=http://localhost:8501  # or your production URL
```

### 3. Supabase Auth Configuration
- [ ] Go to Supabase Dashboard → Authentication → Email Templates
- [ ] Verify "Reset Password" email template is configured
- [ ] Test email delivery (send test email)

### 4. Start the Application
```bash
streamlit run app/app_v21_final.py
```

---

## 🧪 TEST SUITE

### TEST 1: New User Account Creation + First Log Entry

**Steps:**
1. Navigate to homepage
2. Click "Login" or "CREATE FREE ACCOUNT" button
3. Fill in Create Account form:
   - Name: `Test User`
   - Email: `test-v21@example.com` (use real email if testing password reset)
   - Password: `testpass123`
   - Confirm: `testpass123`
4. Click "CREATE ACCOUNT"

**Expected Results:**
- ✅ Success message: "Account created successfully! Welcome, Test User!"
- ✅ Redirected to Daily Log tab
- ✅ Dashboard shows empty state welcome message
- ✅ Session state: `authenticated=True`, `user_id` set

**Database Verification:**
```sql
-- Check Supabase auth.users table
SELECT id, email, created_at FROM auth.users 
WHERE email = 'test-v21@example.com';
```

**Test Database Persistence:**
5. Go to Daily Log tab
6. Fill in first log entry:
   - Date: Today
   - Pain: 5/10
   - Sleep: 7 hours
   - Mood: 7/10
   - Stress: 5/10
   - Notes: "First entry - testing v21 database persistence"
7. Click "💾 SAVE TODAY'S LOG"

**Expected Results:**
- ✅ Success message: "Entry saved successfully!" + balloons 🎈
- ✅ Entry appears in "Recent Entries" section
- ✅ Entry saved to Supabase `user_logs` table

**Database Verification:**
```sql
-- Check user_logs table
SELECT * FROM user_logs 
WHERE user_id = 'YOUR_USER_ID' 
ORDER BY date DESC;
```

---

### TEST 2: Dashboard Empty State for New Users

**Steps:**
1. Using account from TEST 1 (with 0 entries, before logging)
2. Navigate to Dashboard tab

**Expected Results:**
- ✅ Beautiful gradient welcome banner visible
- ✅ Text: "👋 Welcome to Your Health Dashboard!"
- ✅ Call to action: "Go to Daily Log" button
- ✅ Pro tip: "Log for 7 consecutive days..."
- ✅ NO empty charts shown

**Test Progress Messaging:**
3. Log 3 entries (different dates)
4. Navigate to Dashboard

**Expected Results:**
- ✅ Progress message: "You've logged 3 day(s). Keep going for 4 more day(s)!"
- ✅ Charts show available data

---

### TEST 3: Data Persistence Across Sessions (CRITICAL)

**This is the most important test - verifies data doesn't disappear!**

**Steps:**
1. Log in as test user (from TEST 1)
2. Verify Daily Log has 1-3 entries visible
3. Click "Logout" button
4. Verify redirected to homepage
5. Click "Login" button
6. Sign in with same credentials:
   - Email: `test-v21@example.com`
   - Password: `testpass123`
7. Click "SIGN IN"

**Expected Results:**
- ✅ Success message: "Welcome back, Test User!"
- ✅ Spinner shown: "Loading your data..."
- ✅ Dashboard shows previously logged entries
- ✅ Daily Log "Recent Entries" shows historical data
- ✅ Calendar shows green dots for logged days

**Database Verification:**
```sql
-- Verify data still exists
SELECT date, pain_score, mood_score, created_at 
FROM user_logs 
WHERE user_id = 'YOUR_USER_ID' 
ORDER BY date DESC;
```

**FAIL CONDITION:** If data is lost after logout/login, database persistence is broken!

---

### TEST 4: Password Reset Flow

**Steps:**
1. On homepage, click "Login"
2. On Sign In form, click "Forgot?" button
3. Verify password reset form appears
4. Enter email: `test-v21@example.com` (must be real email)
5. Click "SEND RESET LINK"

**Expected Results:**
- ✅ Success message: "Password reset link sent! Check your email..."
- ✅ Info message about 1-hour expiration
- ✅ Email received in inbox (check spam folder)

**Email Testing:**
6. Open password reset email
7. Click reset link
8. Verify redirected to password reset page (Supabase hosted)
9. Enter new password
10. Submit password reset

**Return to App:**
11. Try logging in with NEW password
12. Verify login successful

**Expected Results:**
- ✅ Login works with new password
- ✅ Old password no longer works
- ✅ Historical data still intact

---

### TEST 5: Demo Mode (Verify Demo Data Not Saved)

**Steps:**
1. Logout if logged in
2. On homepage, click "TRY DEMO" button
3. Navigate to Daily Log tab
4. Try adding a log entry
5. Click "💾 SAVE TODAY'S LOG"

**Expected Results:**
- ✅ Entry saved to session state (visible immediately)
- ✅ No database save attempt (demo_mode=True)
- ✅ Dashboard shows demo data + new entry

**Logout and Database Check:**
6. Click "Exit Demo"
7. Verify demo data disappears (expected behavior)

**Database Verification:**
```sql
-- Verify no entries saved with null user_id or demo user_id
SELECT * FROM user_logs 
WHERE user_id IS NULL OR user_id = 'demo';
-- Should return 0 rows
```

---

### TEST 6: Multiple Entries Over Multiple Days

**Steps:**
1. Log in as test user
2. Add log entry for today
3. Add log entry for yesterday (manually change date if possible)
4. Add log entry for 5 days ago
5. Navigate to Dashboard

**Expected Results:**
- ✅ All entries visible in "Recent Entries"
- ✅ Charts show trend lines with multiple data points
- ✅ Calendar shows green dots for all logged days

**Database Verification:**
```sql
SELECT date, pain_score, sleep_hours, created_at 
FROM user_logs 
WHERE user_id = 'YOUR_USER_ID' 
ORDER BY date DESC;
```

---

### TEST 7: Dashboard 7-Day Milestone

**Steps:**
1. Log in as test user
2. Add 7 log entries (7 different dates)
3. Navigate to Dashboard

**Expected Results:**
- ✅ No more "keep logging" progress message
- ✅ Full trend analysis visible
- ✅ All charts populated with meaningful data
- ✅ Therapy effectiveness insights shown (if therapy logged)

---

### TEST 8: Error Handling - Database Unavailable

**Steps:**
1. Stop Supabase connection (change SUPABASE_URL to invalid value)
2. Restart app
3. Try creating account

**Expected Results:**
- ✅ Graceful error message
- ✅ App doesn't crash
- ✅ User sees: "Supabase connection not available"

**Restore and Test:**
4. Restore correct SUPABASE_URL
5. Restart app
6. Verify login works again

---

### TEST 9: Calendar View with Logged Data

**Steps:**
1. Log in with test user (with 3+ log entries)
2. Navigate to Calendar tab
3. Look for green dots on logged days
4. Click on a logged day

**Expected Results:**
- ✅ Green dots visible for days with entries
- ✅ Click shows entry details
- ✅ Days without entries are blank

---

### TEST 10: Settings Profile Update

**Steps:**
1. Log in as test user
2. Navigate to Settings tab
3. Go to Profile sub-tab
4. Update name: `Test User Updated`
5. Click "Save Changes"

**Expected Results:**
- ✅ Success message shown
- ✅ Name updated in Supabase user metadata
- ✅ Display name updated in app header

---

## 🔍 EDGE CASES TO TEST

### Edge Case 1: Duplicate Entry for Same Date
**Steps:**
1. Log entry for today
2. Try logging another entry for today
3. Expect: Warning or overwrite prompt

**Database Schema:** UNIQUE(user_id, date) should prevent duplicates

### Edge Case 2: Very Long Text in Notes
**Steps:**
1. Enter 5000+ characters in notes field
2. Save entry
3. Verify: Truncation or validation message

### Edge Case 3: Special Characters in Input
**Steps:**
1. Enter emojis, symbols, quotes in text fields
2. Save entry
3. Verify: Data saves and displays correctly

### Edge Case 4: Network Failure During Save
**Steps:**
1. Disconnect internet
2. Try saving log entry
3. Expect: Error message + data saved to session (fallback)

---

## ✅ SUCCESS CRITERIA

All tests pass if:

1. ✅ Users can create accounts and log in
2. ✅ Data saves to Supabase database (not just session state)
3. ✅ Data persists after logout/login
4. ✅ Password reset emails are sent and work
5. ✅ New users see helpful empty state messages
6. ✅ Demo mode doesn't save to database
7. ✅ Dashboard shows progress for 1-6 days, full analytics for 7+
8. ✅ No linter errors or console errors
9. ✅ Graceful error handling when database unavailable
10. ✅ All historical data loads correctly on login

---

## 🐛 BUG REPORTING TEMPLATE

If you find issues, report them with this format:

```
**Bug Title:** [Brief description]

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happened

**Error Messages:**
[Paste any error messages]

**Database State:**
[SQL query results if applicable]

**Screenshots:**
[Attach screenshots]

**Priority:** Critical / High / Medium / Low
```

---

## 📊 TESTING PROGRESS TRACKER

- [ ] TEST 1: New user account creation
- [ ] TEST 2: Dashboard empty state
- [ ] TEST 3: Data persistence (CRITICAL)
- [ ] TEST 4: Password reset flow
- [ ] TEST 5: Demo mode (no DB save)
- [ ] TEST 6: Multiple entries
- [ ] TEST 7: 7-day milestone
- [ ] TEST 8: Error handling
- [ ] TEST 9: Calendar view
- [ ] TEST 10: Settings update
- [ ] Edge Case 1: Duplicate entries
- [ ] Edge Case 2: Long text
- [ ] Edge Case 3: Special characters
- [ ] Edge Case 4: Network failure

---

## 🎉 WHEN ALL TESTS PASS

v21 is ready for production deployment!

**Next Steps:**
1. Update version number in production config
2. Deploy to hosting platform (Streamlit Cloud, etc.)
3. Announce to users
4. Monitor for issues in first 24 hours
5. Collect user feedback

---

**End of Testing Guide**

