# 🧪 Bearable App - Manual End-to-End Test Plan

**Test Date:** October 27, 2025  
**Test Environment:** Local Development → http://localhost:8502  
**Database:** Supabase Production  
**Objective:** Validate complete user journey with 60+ log entries per user

---

## 📋 Pre-Test Setup

### ✅ Prerequisites
- [ ] App running at http://localhost:8502
- [ ] Supabase credentials configured in `.streamlit/secrets.toml`
- [ ] RLS policies active (verified earlier)
- [ ] Email account accessible for verification

### 📧 Email Setup
You'll need access to 2 email addresses for testing:
- **User 1 Email:** ________________________
- **User 2 Email:** ________________________

---

## 👤 Test User 1: Yoga Therapy

### Test Case 1.1: Account Creation
**Objective:** Create new user account

**Steps:**
1. Open http://localhost:8502
2. Click **"🔐 Login"** or **"Create Account"**
3. Fill in signup form:
   - Display Name: `Test User 1 - Yoga`
   - Email: [Your email]
   - Password: `TestPass123!`
   - Confirm Password: `TestPass123!`
4. Check "I agree to store my health data securely"
5. Click **"CREATE FREE ACCOUNT"**

**Expected Result:**
- ✅ Account created successfully
- ✅ Verification email received
- ✅ Redirected to login or confirmation page

**Actual Result:** ☐ PASS ☐ FAIL  
**Notes:**
```

```

---

### Test Case 1.2: Email Verification
**Objective:** Verify email address

**Steps:**
1. Check email inbox for verification link from Supabase
2. Click the verification link
3. Email should be confirmed

**Expected Result:**
- ✅ Email verified successfully
- ✅ Can now login to app

**Actual Result:** ☐ PASS ☐ FAIL  
**Notes:**
```

```

---

### Test Case 1.3: First Login
**Objective:** Login with verified account

**Steps:**
1. Return to http://localhost:8502
2. Click **"🔐 Login"**
3. Enter:
   - Email: [Your email]
   - Password: `TestPass123!`
4. Click **"LOGIN"**

**Expected Result:**
- ✅ Logged in successfully
- ✅ See Dashboard with welcome message
- ✅ Navigation tabs visible (Dashboard, Daily Log, Evidence Explorer, Settings)

**Actual Result:** ☐ PASS ☐ FAIL  
**Notes:**
```

```

---

### Test Case 1.4: Baseline Period (Days 1-30)
**Objective:** Log 30 days of baseline data BEFORE starting therapy

**Instructions:**
Create 30 log entries with symptoms **WITHOUT therapy**. Use the data below as a guide.

#### Quick Entry Template (Copy & Paste for each day)
```
Date: [Previous 30 days, working backwards]
Pain: 7-9 (high pain)
Sleep: 5-6.5 hours (poor sleep)
Mood: 3-6 (low mood)
Stress: 7-9 (high stress)
Anxiety: 6-8 (elevated)
Movement: Minimal/Light
Therapy On: ☐ NO (unchecked)
Good Day: ☐ NO (rarely checked)
Notes: "Baseline period - no therapy"
```

**Detailed Steps:**
1. Click **"Daily Log"** tab
2. For each of the past 30 days:
   - **Select date** (start 30 days ago)
   - **Pain Score:** Enter 6-9 (vary each day)
   - **Sleep Hours:** Enter 4.5-6.5 hours
   - **Mood Score:** Enter 3-6
   - **Stress Score:** Enter 6-9
   - **Anxiety Score:** Enter 5-8
   - **Movement:** Select "Minimal" or "Light"
   - **Therapy Started Today:** ☐ LEAVE UNCHECKED
   - **Good Day:** ☐ Check only 20% of the time
   - **Notes:** "Baseline day [X]/30"
   - Click **"SAVE ENTRY"**
3. Repeat for all 30 days

**Progress Tracker:**
```
Days 1-5:   ☐☐☐☐☐
Days 6-10:  ☐☐☐☐☐
Days 11-15: ☐☐☐☐☐
Days 16-20: ☐☐☐☐☐
Days 21-25: ☐☐☐☐☐
Days 26-30: ☐☐☐☐☐
```

**Expected Result:**
- ✅ 30 entries saved successfully
- ✅ Dashboard shows data visualization
- ✅ Average pain 7-8/10
- ✅ Average sleep 5-6 hours
- ✅ Average mood 4-5/10

**Actual Result:** ☐ PASS ☐ FAIL  
**Entries Completed:** ___/30  
**Notes:**
```

```

---

### Test Case 1.5: Start Yoga Therapy (Day 31)
**Objective:** Mark the start of therapy

**Steps:**
1. Click **"Daily Log"** tab
2. Select **today's date** (or Day 31 from baseline start)
3. Fill in symptoms (similar to baseline):
   - Pain: 7/10
   - Sleep: 5.5 hours
   - Mood: 5/10
   - Stress: 7/10
4. **✅ CHECK "Started new therapy today"**
5. **Select therapy:** "Yoga" (or type it in)
6. Notes: "Day 1 of Yoga therapy - excited to try this!"
7. Click **"SAVE ENTRY"**

**Expected Result:**
- ✅ Entry saved with therapy marker
- ✅ Dashboard should show therapy start indicator
- ✅ "🧘🏻‍♀️" icon appears on date in visualizations

**Actual Result:** ☐ PASS ☐ FAIL  
**Notes:**
```

```

---

### Test Case 1.6: Therapy Period (Days 32-66)
**Objective:** Log 35 more days DURING therapy with gradual improvement

**Instructions:**
Log 35 days showing gradual improvement. Symptoms should get better over time.

#### Progressive Improvement Template

**Week 1 (Days 32-38):** Minimal improvement
```
Pain: 6-8 (slight decrease)
Sleep: 5.5-6.5 hours
Mood: 5-6
Stress: 6-8
Movement: Moderate
Therapy Used: Yoga
Good Day: 30% of the time
Notes: "Week 1 of yoga - getting used to it"
```

**Week 2 (Days 39-45):** Mild improvement
```
Pain: 5-7 (noticeable decrease)
Sleep: 6-7 hours
Mood: 6-7
Stress: 5-7
Movement: Moderate/Active
Therapy Used: Yoga
Good Day: 40% of the time
Notes: "Week 2 - starting to feel effects"
```

**Week 3 (Days 46-52):** Moderate improvement
```
Pain: 4-6 (clear improvement)
Sleep: 6.5-7.5 hours
Mood: 7-8
Stress: 4-6
Movement: Active
Therapy Used: Yoga
Good Day: 60% of the time
Notes: "Week 3 - definitely helping!"
```

**Week 4-5 (Days 53-66):** Strong improvement
```
Pain: 3-5 (significant reduction)
Sleep: 7-8 hours
Mood: 7-9
Stress: 3-5
Movement: Active/Very Active
Therapy Used: Yoga
Good Day: 70% of the time
Notes: "Week 4-5 - feeling much better!"
```

**Detailed Steps:**
For each day (35 total):
1. Click **"Daily Log"** tab
2. Select date (continuing from Day 31)
3. Fill in symptoms (use progressive improvement above)
4. **Therapy Used:** Type "Yoga"
5. **Good Day:** Check more frequently as you progress
6. Notes: Indicate week number and how you're feeling
7. Click **"SAVE ENTRY"**

**Progress Tracker:**
```
Week 1: ☐☐☐☐☐☐☐
Week 2: ☐☐☐☐☐☐☐
Week 3: ☐☐☐☐☐☐☐
Week 4: ☐☐☐☐☐☐☐
Week 5: ☐☐☐☐☐☐☐
```

**Expected Result:**
- ✅ 35 therapy entries saved
- ✅ Total entries: 66 (30 baseline + 1 start + 35 therapy)
- ✅ Dashboard shows improvement trends
- ✅ Pain declining from 7-8 to 3-5
- ✅ Sleep improving from 5-6hrs to 7-8hrs
- ✅ Mood improving from 4-5 to 7-9

**Actual Result:** ☐ PASS ☐ FAIL  
**Entries Completed:** ___/35  
**Notes:**
```

```

---

### Test Case 1.7: Dashboard Analysis
**Objective:** Verify therapy effect calculation

**Steps:**
1. Click **"Dashboard"** tab
2. Observe the data visualizations
3. Look for:
   - Pain/Sleep/Mood gauges
   - 14-day trend charts
   - Therapy effect analysis card
   - **"Therapy Effect Analysis"** section

**Expected Result:**
- ✅ Dashboard loads successfully
- ✅ Charts show 66 days of data
- ✅ Therapy start marker visible (🧘🏻‍♀️)
- ✅ **Therapy Effect Card shows:**
   - Therapy name: "Yoga"
   - Pain reduction: ~30-40%
   - Sleep improvement: ~30-40%
   - Mood improvement: ~50-70%
   - Confidence level: >80%
- ✅ Trend lines show clear improvement after therapy start

**Actual Result:** ☐ PASS ☐ FAIL  
**Screenshot:** [Attach if possible]  
**Metrics Observed:**
```
Pain Reduction: _____% 
Sleep Improvement: _____% 
Mood Improvement: _____%
Confidence: _____%
```

**Notes:**
```

```

---

### Test Case 1.8: Data Export
**Objective:** Export all user data

**Steps:**
1. Click **"Settings"** tab
2. Scroll to **"Data Management"** section
3. Click **"📥 Export Data (CSV)"** button
4. Save the CSV file
5. Open in Excel/Google Sheets

**Expected Result:**
- ✅ CSV downloads successfully
- ✅ File contains 66 rows (65 entries + header)
- ✅ All columns present (date, pain, sleep, mood, etc.)
- ✅ Therapy markers visible in "therapy_on" and "therapy_used" columns
- ✅ Data matches what was entered

**Actual Result:** ☐ PASS ☐ FAIL  
**File Size:** _____ KB  
**Row Count:** _____ rows  
**Notes:**
```

```

---

## 👤 Test User 2: Acupuncture Therapy

### Test Case 2.1: Create Second User
**Objective:** Test app with multiple users

**Steps:**
1. **Logout** from User 1 (click Logout button)
2. Click **"Create Account"**
3. Fill in signup form:
   - Display Name: `Test User 2 - Acupuncture`
   - Email: [Different email from User 1]
   - Password: `TestPass123!`
4. Verify email
5. Login

**Expected Result:**
- ✅ Second account created successfully
- ✅ Logged in as User 2
- ✅ Dashboard is empty (no data from User 1 visible)
- ✅ Data isolation working (RLS)

**Actual Result:** ☐ PASS ☐ FAIL  
**Notes:**
```

```

---

### Test Case 2.2: Baseline Period (Days 1-30)
**Repeat Test Case 1.4 for User 2**

**Progress Tracker:**
```
Days 1-5:   ☐☐☐☐☐
Days 6-10:  ☐☐☐☐☐
Days 11-15: ☐☐☐☐☐
Days 16-20: ☐☐☐☐☐
Days 21-25: ☐☐☐☐☐
Days 26-30: ☐☐☐☐☐
```

**Actual Result:** ☐ PASS ☐ FAIL  
**Entries Completed:** ___/30

---

### Test Case 2.3: Start Acupuncture (Day 31)
**Steps:**
1. Log Day 31 entry
2. **✅ Check "Started new therapy today"**
3. **Select therapy:** "Acupuncture"
4. Save entry

**Actual Result:** ☐ PASS ☐ FAIL

---

### Test Case 2.4: Therapy Period (Days 32-66)
**Repeat Test Case 1.6 for User 2 with Acupuncture**

Use similar improvement pattern but for Acupuncture therapy.

**Progress Tracker:**
```
Week 1: ☐☐☐☐☐☐☐
Week 2: ☐☐☐☐☐☐☐
Week 3: ☐☐☐☐☐☐☐
Week 4: ☐☐☐☐☐☐☐
Week 5: ☐☐☐☐☐☐☐
```

**Actual Result:** ☐ PASS ☐ FAIL  
**Entries Completed:** ___/35

---

### Test Case 2.5: Verify Data Isolation
**Objective:** Confirm users can't see each other's data

**Steps:**
1. As User 2, check Dashboard
2. Verify only User 2's data is visible
3. Logout
4. Login as User 1
5. Verify only User 1's data is visible

**Expected Result:**
- ✅ User 1 sees only Yoga therapy data (66 entries)
- ✅ User 2 sees only Acupuncture therapy data (66 entries)
- ✅ No cross-contamination of data
- ✅ RLS policies working correctly

**Actual Result:** ☐ PASS ☐ FAIL  
**Notes:**
```

```

---

## 🔬 Test Case 3: Evidence Explorer

### Test Case 3.1: Browse Live Research Data
**Objective:** Verify API integration

**Steps:**
1. Click **"Evidence Explorer"** tab
2. Select condition: **"Low Back Pain"**
3. Observe therapy cards load
4. Click on **"Yoga"** therapy card
5. Note the numbers:
   - Clinical Trials count
   - PubMed Articles count
   - Evidence level (Positive/Mixed/Negative)
6. Click **"View Studies"** link

**Expected Result:**
- ✅ Therapies load from live APIs
- ✅ Clinical trials count > 0
- ✅ PubMed articles count > 0
- ✅ Evidence badges display correctly
- ✅ Links open to ClinicalTrials.gov

**Actual Result:** ☐ PASS ☐ FAIL  
**Metrics Observed:**
```
Clinical Trials: _____
PubMed Articles: _____
Evidence Level: _____
```

---

## 📊 Final Summary

### Test Execution Summary

| Test Area | Total Cases | Passed | Failed | Notes |
|-----------|-------------|--------|--------|-------|
| User 1 - Account | 3 | __ | __ | |
| User 1 - Data Entry | 3 | __ | __ | |
| User 1 - Analysis | 2 | __ | __ | |
| User 2 - Account | 1 | __ | __ | |
| User 2 - Data Entry | 3 | __ | __ | |
| Multi-User | 1 | __ | __ | |
| Evidence Explorer | 1 | __ | __ | |
| **TOTAL** | **14** | **__** | **__** | |

### Data Entry Summary

| User | Baseline Entries | Therapy Entries | Total | Therapy Type |
|------|------------------|-----------------|-------|--------------|
| User 1 | ___/30 | ___/36 | ___/66 | Yoga |
| User 2 | ___/30 | ___/36 | ___/66 | Acupuncture |
| **TOTAL** | **___/60** | **___/72** | **___/132** | |

### Therapy Effectiveness Results

#### User 1 - Yoga
```
Baseline Average Pain: _____/10
Therapy Average Pain: _____/10
Pain Reduction: _____%

Baseline Average Sleep: _____ hours
Therapy Average Sleep: _____ hours
Sleep Improvement: _____%

Baseline Average Mood: _____/10
Therapy Average Mood: _____/10
Mood Improvement: _____%
```

#### User 2 - Acupuncture
```
Baseline Average Pain: _____/10
Therapy Average Pain: _____/10
Pain Reduction: _____%

Baseline Average Sleep: _____ hours
Therapy Average Sleep: _____ hours
Sleep Improvement: _____%

Baseline Average Mood: _____/10
Therapy Average Mood: _____/10
Mood Improvement: _____%
```

---

## ✅ Test Sign-Off

**Tester Name:** _____________________  
**Date Completed:** _____________________  
**Overall Result:** ☐ PASS ☐ FAIL ☐ PASS WITH ISSUES  

**Issues Found:**
```




```

**Recommendations:**
```




```

---

## 📸 Evidence & Artifacts

Please attach:
- [ ] Screenshots of Dashboard with 60+ entries
- [ ] Screenshot of Therapy Effect Analysis
- [ ] Exported CSV files for both users
- [ ] Screenshot of Evidence Explorer

---

**Test Plan Version:** 1.0  
**Last Updated:** October 27, 2025  
**Ready for Execution** ✅

