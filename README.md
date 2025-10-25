# 💆🏻‍♀️ PainReliefMap — Evidence Explorer + N‑of‑1 Tracker

A comprehensive Streamlit app that helps you **explore evidence-based therapies** (ClinicalTrials.gov + PubMed) and **track your personal health journey** with N‑of‑1 trials. Now with **user authentication**, **cloud database storage**, and **enhanced UI design**!

> **🆕 Latest Updates:** Complete database integration with Supabase, redesigned Quick Actions section with glass-card styling, and enhanced user authentication system!

---

## ✨ Features

### 🔐 User Authentication (New!)

  * **Secure signup & login** with email verification
  * **Password reset** via email
  * **Personal accounts** - your data stays private
  * **Demo mode** - try the app without signing up
  * **Cloud storage** - data persists across sessions
  * **Row-level security** - users only see their own data

### 📊 Personal Dashboard

  * **Latest entry snapshot** (pain, sleep, mood at a glance)
  * **14-day trend charts** with therapy start markers
  * **Key insights** - automated therapy effect detection
  * **Progress summary** - before vs after comparison
  * **Date filtering** - focus on specific time periods

### 🔬 Evidence Explorer

  * **Filter by condition and therapy** with multi-select
  * **Evidence direction** (Positive/Mixed/Negative/Unclear)
  * **Clinical trials count** from ClinicalTrials.gov
  * **PubMed articles count** with direct links
  * **Visual ranking** - therapies sorted by evidence strength
  * **Export to CSV** for sharing with healthcare providers

### 🌱 Daily Wellness Log (N‑of‑1)

  * **Quick logging** - takes 30 seconds per day
  * **Core metrics**: pain, stress, anxiety, mood, sleep
  * **Therapy tracking** - mark when you start new therapies
  * **Physical state**: movement, digestion, bowel habits
  * **Emotional symptoms** - comprehensive tracking
  * **Menstrual cycle** - optional hormone tracking
  * **"Duplicate yesterday"** for easier data entry
  * **Quick notes** and "good day" markers

### 📈 Therapy Effect Analysis (Enhanced!)

  * **Statistical analysis** with bootstrap confidence intervals
  * **Before/after comparison** for each therapy
  * **Timeline visualization** showing therapy periods
  * **Correlation matrix** - discover relationships between metrics
  * **Compare with research** - see how your results match clinical trials
  * **Percentage improvements** calculated automatically
  * **🎨 Beautiful gradient design** - purple-pink themed results cards
  * **Enhanced visualizations** - improved charts and data presentation

### ⚙️ Data Management

  * **Export to CSV** - download all your data
  * **Generate PDF reports** - shareable with doctors
  * **Import previous data** - restore from backups
  * **Data privacy** - you own your data, stored securely

### 🚀 Quick Actions (app_v17_final.py)

  * **Copy Yesterday** - duplicate previous day's entries with one click
  * **Add Note** - quick note-taking with popover interface
  * **Mark Good Day** - toggle good day status
  * **Track Cycle** - enable/disable menstrual cycle tracking
  * **Glass-card design** - modern white container with shadow/elevation
  * **Visual icons** - intuitive circular icons for each action
  * **Database persistence** - all actions saved to Supabase

---

## 🧭 Solution Architecture

### With Authentication (app_v17_final.py - Latest)

```
┌────────────────────────────────────────────────────────────────┐
│                         User Browser                           │
│  • Login/Signup Page → Personal Dashboard                      │
└────────────────────────────────────────────────────────────────┘
                   │  Streamlit UI + Plotly
                   ▼
┌────────────────────────────────────────────────────────────────┐
│              Streamlit App (app_v17_final.py)                    │
│  • Authentication Gate (login_ui.py)                           │
│  • Tabs: Dashboard | Evidence Explorer | Daily Log | Settings │
│  • User-specific data loading from database                    │
└────────────────────────────────────────────────────────────────┘
          │                         │
          │ Auth                    │ Data Operations
          ▼                         ▼
┌─────────────────────┐   ┌───────────────────────────────────┐
│   AuthManager       │   │   DatabaseManager                 │
│   (src/auth.py)     │   │   (src/db_operations.py)          │
│ • Signup/Login      │   │ • save_log()                      │
│ • Password Reset    │   │ • get_user_logs()                 │
│ • Session Mgmt      │   │ • get_user_stats()                │
└─────────────────────┘   └───────────────────────────────────┘
          │                         │
          │ Supabase                │ Supabase
          │ Auth API                │ Database API
          ▼                         ▼
┌────────────────────────────────────────────────────────────────┐
│                     Supabase Cloud                             │
│  ┌─────────────────────┐      ┌──────────────────────────┐    │
│  │  Authentication     │      │  PostgreSQL Database     │    │
│  │  • User Management  │      │  • user_profiles         │    │
│  │  • Email Verify     │      │  • user_logs (daily data)│    │
│  │  • Password Hash    │      │  • user_therapies        │    │
│  └─────────────────────┘      │  • Row Level Security    │    │
│                               └──────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
                   │
                   │ (optional: evidence data)
                   ▼
┌────────────────────────────────────────────────────────────────┐
│            Local Evidence CSV (read-only)                      │
│            • evidence_counts.csv                               │
│            • Shared across all users                           │
└────────────────────────────────────────────────────────────────┘
          ▲
          │ (one‑shot build / refresh)
┌────────────────────────────────────────────────────────────────┐
│ Evidence Builder (scripts/build_evidence_counts_aact.py)       │
│ • Reads AACT flat files from data/raw/                         │
│ • Counts trials per (condition, therapy)                       │
│ • Fetches PubMed counts via E‑utilities                        │
│ • Saves to data/raw/evidence_counts.csv                        │
└────────────────────────────────────────────────────────────────┘
```

### Without Authentication (app_v3.py)

The original app (`app_v3.py`) still works without authentication - data stored in session state only (temporary).

---

## 🌐 Data Sources

PainReliefMap combines **external scientific evidence** with **user-generated daily tracking data** to help users explore what works for them.

| Source Type                                   | Description                                                                                                                                                                                               | Access / API URL                                                                                                                                                                                                                                                                                                                                                                               | Used In                                                                                        |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 🧾 **ClinicalTrials.gov (AACT Flat Files)**   | Official U.S. registry of clinical trials. The AACT dataset (Aggregate Analysis of ClinicalTrials.gov) provides downloadable flat files of all registered trials, including conditions and interventions. | [https://aact.ctti-clinicaltrials.org/pipe_files](https://aact.ctti-clinicaltrials.org/pipe_files)                                                                                                                                                                                                                                                                                             | `build_evidence_counts_aact.py` — counts number of clinical trials per *(condition × therapy)* |
| 📚 **PubMed (NCBI E-Utilities API)**          | Biomedical literature database maintained by the U.S. National Library of Medicine. The E-Utilities API is used to fetch the number of published papers for each *(condition × therapy)* combination.     | **Docs:** [https://www.ncbi.nlm.nih.gov/books/NBK25499/](https://www.ncbi.nlm.nih.gov/books/NBK25499/) · **Example query:** [https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term=(Fibromyalgia)%20AND%20(Acupuncture)](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term=%28Fibromyalgia%29%20AND%20%28Acupuncture%29) | `build_evidence_counts_aact.py` — retrieves publication counts (`pubmed_n`)                    |
| 📅 **User Daily Wellness Logs (N-of-1 Data)** | Self-reported data entered directly in the Streamlit “Daily Wellness Log” tab. Includes pain, stress, sleep, movement, digestion, mood, and therapy usage.                                                | Local input via Streamlit UI; template at `data/templates/n_of_1_template.csv`                                                                                                                                                                                                                                                                                                                 | `app.py` — stores and visualizes daily well-being trends                                       |

### 📊 Output Datasets

| File                                 | Generated By                    | Description                                                                                                                 |
| ------------------------------------ | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `data/raw/evidence_counts.csv`       | `build_evidence_counts_aact.py` | Combined evidence summary for all condition × therapy pairs, with columns for `clinicaltrials_n`, `pubmed_n`, and metadata. |
| `data/templates/n_of_1_template.csv` | Manual / Streamlit              | Template for personal tracking data; used in N-of-1 analysis preparation.                                                   |

---

## 📦 What's in this repo

```
painreliefmap/
│
├── app/
│   ├── app_v3.py                    # ✨ Original app (no auth, session-only data)
│   ├── app_v4_auth.py               # 🔐 Authenticated app with database
│   ├── app_v16_final.py             # 🎨 Enhanced UI with gradient design
│   ├── app_v17_final.py             # 🚀 LATEST! Full database integration + Quick Actions redesign
│   ├── app_chat.py                  # Experimental chat interface
│   └── causal.py                    # Statistical analysis functions
│
├── src/
│   ├── __init__.py
│   ├── auth.py                      # 🔐 NEW! Authentication manager
│   ├── login_ui.py                  # 🔐 NEW! Login/signup UI components
│   ├── db_operations.py             # 🔐 NEW! Database CRUD operations
│   ├── causal.py                    # Bootstrap analysis for N-of-1
│   └── db.py                        # Database utilities (legacy)
│
├── scripts/
│   ├── create_user_tables.sql       # 🔐 NEW! Database schema for users
│   ├── build_evidence_counts_aact.py # Evidence builder (AACT + PubMed)
│   └── add_evidence_direction.py    # Add positive/negative labels
│
├── data/
│   ├── evidence_counts.csv          # Evidence summary (all users share)
│   ├── evidence_counts_with_direction.csv
│   ├── raw/                         # AACT flat files go here
│   └── templates/                   # CSV templates for tracking
│
├── docs/
│   └── AUTHENTICATION_ARCHITECTURE.md # 📚 Technical deep-dive
│
├── config.env.example               # 🔐 Environment variables template
├── setup_auth.py                    # 🔐 Interactive setup wizard
├── requirements.txt                 # Python dependencies
├── QUICKSTART_AUTH.md               # ⭐ 5-minute auth setup guide
├── AUTHENTICATION_SETUP.md          # 📖 Detailed auth guide
├── AUTHENTICATION_SUMMARY.md        # 📋 What's been built
└── README.md                        # This file
```

### Three App Versions

| File | Description | Data Storage | Use Case |
|------|-------------|--------------|----------|
| **app_v3.py** | Original app | Session state (temporary) | Quick testing, no signup needed |
| **app_v4_auth.py** | Authenticated app | Supabase database (permanent) | Personal use, multiple users, data persists |
| **app_v17_final.py** | 🚀 **LATEST!** Full database integration | Supabase database (permanent) | **Recommended** - complete auth + database + enhanced UI |
| **app_v16_final.py** | 🎨 Enhanced UI with gradient design | Supabase database (permanent) | Enhanced user experience with gradient design |

All apps share the same evidence database (CSV) and have the same features - the difference is user accounts, data persistence, and UI enhancements.

---

## 📚 File‑level details (aligned with your code)

### `app.py`

* Sets the page title **“Pain Relief Map — Evidence Explorer + N‑of‑1”**
* **CSV Locator**: looks for `evidence_counts.csv` in `data/`, then `data/raw/`, then repo **root**.
* **Filters** in the sidebar: condition, therapies, year range, evidence direction, study type, countries, quality, participant filters (sex, age), language, and sorting.
* **Evidence Direction chart**: percentage breakdown with sensible colours if the `evidence_direction` column exists.
* **Daily Log**: big form with sliders and multiselects; “Duplicate yesterday”, “Quick note”, “Mark good day”, and optional menstrual cycle block.

### `build_evidence_counts_aact.py`

* Expects **AACT flat files** under `data/raw/` (e.g., `studies*.txt*`, `conditions*.txt*`, `interventions*.txt*`).
* Computes `clinicaltrials_n` per (condition, therapy), fetches `pubmed_n`, builds **links**, stamps `last_updated`, and saves to `data/raw/evidence_counts.csv`.
* On success, prints a ✅ line with row count and output path.
* (Optional) Attempts `from src.db import upsert_pairs`. If you are using the **current** root‑level `db.py`, either move it to `src/db.py` or change the import in the builder to `import db as src_db` and call `src_db.upsert_pairs(...)`.

### `db.py`

* Uses `DATABASE_URL` to open a SQLAlchemy engine.
* Provides:

  * `upsert_pairs(df)`: upsert one row per `(condition, therapy)` into `evidence_pairs` (requires that table and an `on conflict (condition,therapy)` index).
  * `read_pairs()`: read the whole table to a DataFrame.
* If you keep `db.py` at the **root**, update the builder import as noted above.

### `requirements.txt`

Exact deps used by your code:

* streamlit, pandas, numpy, plotly, requests
* statsmodels, scikit‑learn (planned causal features)
* sqlalchemy, psycopg2‑binary, supabase (optional DB path)
* beautifulsoup4 (HTML fallback/scraping if needed)

---

## 🚀 Setup & Run

### Quick Start (No Authentication)

Want to try the app immediately without setup?

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app (no login required)
python -m streamlit run app/app_v3.py
```

Open: [http://localhost:8501](http://localhost:8501)

### Full Setup (With User Accounts)

#### 1) Install Dependencies

```bash
# Using conda
conda create -n painreliefmap312 python=3.12.6
conda activate painreliefmap312
pip install -r requirements.txt

# Or using pip directly
pip install -r requirements.txt
```

#### 2) Set Up Authentication (5 minutes)

**Option A: Interactive Setup Wizard**

```bash
python setup_auth.py
```

Follow the prompts to configure your Supabase credentials.

**Option B: Manual Setup**

1. Create a free Supabase account at https://supabase.com
2. Create a new project
3. Run the SQL schema:
   - Go to SQL Editor in Supabase dashboard
   - Copy-paste contents of `scripts/create_user_tables.sql`
   - Click "Run"
4. Get your credentials:
   - Go to Settings → API
   - Copy Project URL and anon key
5. Create `.env` file in project root:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

📖 **Detailed guide:** See [QUICKSTART_AUTH.md](QUICKSTART_AUTH.md)

#### 3) Provide Evidence Data

* Easiest: The app includes `data/evidence_counts.csv` (works out of the box)
* To **rebuild** from AACT + PubMed:
  1. Download AACT **Flat Text Files** and extract to `data/raw/`
  2. Run:
     ```bash
     python -u scripts/build_evidence_counts_aact.py
     ```

#### 4) Run the App

**Without Authentication:**
```bash
python -m streamlit run app/app_v3.py
```

**With Authentication (Recommended):**
```bash
python -m streamlit run app/app_v17_final.py
```

**With Authentication (Legacy):**
```bash
python -m streamlit run app/app_v4_auth.py
```

Open: [http://localhost:8501](http://localhost:8501)

#### 5) Create Your Account

1. Click "Sign Up" tab
2. Enter email, password, and display name
3. Check your email for verification link
4. Login and start tracking!

---

## 🧪 Notes on N‑of‑1

### Data Storage

* **app_v3.py**: Entries stored in **session state** (temporary - lost when browser closes)
* **app_v4_auth.py**: Entries saved to **Supabase database** (permanent - persists across sessions)

### Statistical Analysis

✅ **Now Implemented!** The app includes:

* **Bootstrap analysis** (`src/causal.py`) for calculating therapy effects
* **Pre/post comparison** with 95% confidence intervals
* **Automated insights** - the dashboard automatically shows therapy effects
* **Correlation matrix** - discover relationships between pain, sleep, stress, etc.
* **Timeline visualization** - see your progress over time

### Therapy Tracking

To analyze a therapy's effect:
1. Log your baseline symptoms for a few days
2. Check "Started new primary therapy today" when you begin
3. Continue logging daily
4. Go to "Daily Log" tab → "Therapy Effect Calculator"
5. See your statistical results with confidence intervals!

---

## 🔍 Troubleshooting

### General Issues

* **"I couldn't find evidence_counts.csv"**
  
  Place the file at `data/evidence_counts.csv` or `data/raw/evidence_counts.csv`. The app checks both locations.

* **App won't start**
  ```bash
  # Check if all dependencies are installed
  pip install -r requirements.txt
  
  # Try running directly
  python -m streamlit run app/app_v3.py
  ```

* **Charts show blanks for PubMed**
  
  Rebuild with the builder script to populate `pubmed_n`, or ensure the column exists in your CSV.

### Authentication Issues

* **"Authentication not configured"**
  
  Check that your `.env` file exists and has correct credentials:
  ```env
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-anon-key-here
  ```

* **Can't sign up / "Table doesn't exist"**
  
  Run the SQL schema in Supabase:
  1. Open SQL Editor in Supabase dashboard
  2. Copy-paste contents of `scripts/create_user_tables.sql`
  3. Click "Run"

* **Password reset not working**
  
  Check your spam folder for the reset email. If still not working, check Supabase Auth settings.

* **Data not saving**
  
  - Verify you're logged in (not demo mode)
  - Check browser console for errors
  - Verify RLS policies are enabled in Supabase

### Demo Mode

Want to test without setting up authentication? Use demo mode:
- Run `app_v4_auth.py`
- Click "Continue in Demo Mode"
- All features work, data is temporary

📚 **Full troubleshooting guide:** See [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md)

---

## 🗺️ Roadmap

### ✅ Recently Completed

* ✅ User authentication with Supabase
* ✅ Database storage for personal health logs
* ✅ Bootstrap pre/post effect analysis (`src/causal.py`)
* ✅ Therapy effect calculator with confidence intervals
* ✅ Interactive dashboard with automated insights
* ✅ Correlation matrix for discovering relationships
* ✅ Timeline visualization with therapy markers
* ✅ Export to CSV and HTML reports
* ✅ Row-level security for data privacy
* ✅ Demo mode for testing without signup
* ✅ **Enhanced UI design** - purple-pink gradient therapy results cards
* ✅ **Improved form layouts** - better spacing and visual hierarchy
* ✅ **Streamlined user interface** - cleaner, more modern design

### 🚧 In Progress

* Mobile app optimization
* Enhanced data visualization options
* Automated backup to user's cloud storage

### 🔮 Future Plans

* **Social Features**
  - Share anonymized results with healthcare providers
  - Team/family accounts (share data with doctor)
  - Community insights (anonymized aggregate data)

* **Advanced Analysis**
  - AI-powered pattern detection
  - Predictive models for symptom forecasting
  - Multi-therapy comparison

* **Integrations**
  - Wearable device import (Fitbit, Apple Watch, Oura)
  - Calendar integration for therapy reminders
  - Export to health apps (Apple Health, Google Fit)

* **Features**
  - Two-factor authentication (2FA)
  - Social login (Google, Apple)
  - Offline mode with sync
  - Mobile app (React Native + Supabase)

---

## 📄 License

MIT (choose your preferred OSS license if different)

---

## 🎯 Use Cases

### For Individuals
- Track chronic pain symptoms daily
- Test if therapies actually work for you
- Share data-driven insights with doctors
- Discover what correlates with your symptoms

### For Healthcare Providers
- Give patients structured tracking tools
- Review patient data during appointments
- Make evidence-based treatment adjustments
- Support shared decision-making

### For Researchers
- Collect N-of-1 trial data
- Study therapy effectiveness in real-world settings
- Analyze symptom correlations
- Aggregate anonymized data for studies

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART_AUTH.md](QUICKSTART_AUTH.md) | ⭐ 5-minute authentication setup guide |
| [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) | Detailed authentication and integration guide |
| [AUTHENTICATION_SUMMARY.md](AUTHENTICATION_SUMMARY.md) | Complete overview of authentication system |
| [AUTHENTICATION_ARCHITECTURE.md](docs/AUTHENTICATION_ARCHITECTURE.md) | Technical deep-dive into system architecture |
| [README.md](README.md) | This file - general project overview |

---

## 🙏 Acknowledgements

* **Data Sources**: ClinicalTrials.gov (AACT) and PubMed E‑utilities
* **Frontend**: Streamlit, Plotly
* **Backend**: Supabase (Auth & PostgreSQL), SQLAlchemy
* **Analysis**: Pandas, NumPy, SciPy, statsmodels, scikit-learn
* **Community**: Open-source contributors and users providing feedback