# 🐻 Bearable - Evidence-Based Health Tracking

> **Track your health journey with science-backed insights. Explore evidence from 500,000+ clinical trials, track your symptoms, and discover what actually works for you.**

[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://github.com/jessicapaes/bearable)
[![Version](https://img.shields.io/badge/version-v28-purple)](https://github.com/jessicapaes/bearable/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-9%2F9%20passing-brightgreen)](TEST_REPORT_V28_FINAL.md)

---

## ✨ What is Bearable?

Bearable is a comprehensive, evidence-based health tracking application that combines **real-time clinical research** with **personal data tracking** to help you discover which natural therapies actually work for your health conditions.

### 🎨 Beautiful Purple Branding
- **Gradient purple buttons** - Modern, cohesive UI design
- **Professional color scheme** - Purple (#667eea → #764ba2), Pink (#ec4899 → #f472b6), Blue accents
- **Glass morphism** - Sleek, modern card designs
- **Responsive design** - Perfect on desktop, tablet, and mobile

### 🎯 Perfect For
- **Chronic pain management** - Track symptoms and therapy effectiveness
- **N-of-1 trials** - Run personal experiments with statistical analysis
- **Natural therapy research** - Explore evidence from 500,000+ clinical trials
- **Health optimization** - Discover patterns and correlations in your data
- **Doctor consultations** - Share data-driven insights with healthcare providers

---

## 🚀 Quick Start

### Try Demo Mode (No Setup Required)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app/app_v28_final.py

# 3. Click "START FREE DEMO" on the landing page
```

Open [http://localhost:8501](http://localhost:8501) and start exploring!

### Full Setup (5 Minutes)
```bash
# 1. Clone and install
git clone https://github.com/jessicapaes/bearable.git
cd bearable
pip install -r requirements.txt

# 2. Set up Supabase (free tier)
python setup_auth.py  # Interactive wizard

# 3. Run the app
streamlit run app/app_v28_final.py
```

📖 **Detailed setup:** See [QUICKSTART_AUTH.md](docs/QUICKSTART_AUTH.md)

---

## 🌟 Key Features

### 🔐 Secure & Private
- **User authentication** with email/password and secure sessions
- **Password reset** via secure email links
- **Row-level security** - your data is yours alone
- **Cloud storage** with Supabase (PostgreSQL)
- **GDPR compliant** - export or delete your data anytime

### 📊 Personal Dashboard
- **Interactive gauges** - Visual health metrics (Pain, Sleep, Mood)
- **Trend charts** - 30-day visualizations with Plotly
- **Therapy analysis** - Statistical before/after comparison
- **Correlation insights** - Discover what affects your symptoms
- **Timeline markers** - See when you started natural therapies
- **Automated pattern detection** - AI-powered insights

### 🔬 Evidence Explorer (Live API Data!)
- **🔴 Real-time data** from ClinicalTrials.gov API v2
- **🔴 Live PubMed counts** via E-utilities API
- **500,000+ clinical trials** - always up-to-date
- **30M+ research articles** - current counts
- **Evidence ratings** - Positive ✅, Mixed ⚠️, Negative ❌
- **Filter by condition** - 30+ health conditions
- **Natural therapies** - yoga, acupuncture, supplements, and more
- **Smart caching** - fast loads with fresh data

### 🌱 Daily Log (30 seconds/day)
- **Core metrics:** Pain (0-10), Sleep (hours), Mood (0-10)
- **Physical state:** Movement, digestion, bowel habits
- **Emotional symptoms:** Anxiety, stress levels
- **Therapy tracking:** Mark when you start/stop therapies
- **Menstrual cycle:** Optional hormone tracking
- **Quick actions:** Copy yesterday, add notes, mark good days
- **Auto-save:** Data syncs to cloud automatically

### 📈 Statistical Analysis (N-of-1 Trials)
- **Bootstrap confidence intervals** - Statistical rigor
- **Before/after comparison** - 3 days before, 10 days after minimum
- **Effect size** - Cohen's d calculation
- **P-value** - Statistical significance testing
- **Visual results** - Beautiful gradient cards with insights
- **Plain English** - no statistics degree needed

### ⚙️ Data Management
- **CSV export** - Download all your data
- **JSON export** - Structured data format
- **Data import** - Restore from backups
- **Account settings** - Update profile, change password
- **Secure deletion** - Remove your account anytime

---

## 📱 Screenshots

### Dashboard with Health Metrics
![Dashboard](https://placehold.co/800x400/667eea/FFFFFF?text=Interactive+Dashboard)

*Track pain, sleep, and mood trends with beautiful visualizations*

### Evidence Explorer (Live Data!)
![Evidence Explorer](https://placehold.co/800x400/764ba2/FFFFFF?text=Evidence+Explorer)

*Explore evidence from 500,000+ clinical trials*

### Daily Log
![Daily Log](https://placehold.co/800x400/ec4899/FFFFFF?text=Daily+Logging)

*Log your symptoms in 30 seconds*

---

## 🏗️ Tech Stack

### Frontend
- **Streamlit** - Rapid web app development
- **Plotly** - Interactive data visualizations
- **HTML/CSS** - Custom purple gradient styling and responsive design
- **JavaScript** - Smooth scroll and UI interactions

### Backend  
- **Supabase** - Authentication & PostgreSQL database
- **Python 3.12** - Core application logic
- **Pandas/NumPy** - Data processing
- **SciPy** - Statistical analysis

### Data Sources
- **ClinicalTrials.gov API v2** - Live clinical trials data
- **PubMed E-utilities API** - Live research article counts
- **Supabase PostgreSQL** - User health tracking data

---

## 📂 Project Structure

```
bearable/
├── README.md                     # 📖 You are here
├── requirements.txt              # Python dependencies  
├── runtime.txt                   # Python version
├── setup_auth.py                 # 🚀 Interactive setup wizard
│
├── app/                          # Streamlit applications
│   ├── app_v28_final.py          # 🚀 LATEST - All features + testing
│   ├── app_v27_final.py          # Previous version
│   └── bear_icon.svg             # Bearable bear icon
│
├── src/                          # Core modules
│   ├── auth.py                   # Authentication manager
│   ├── db_operations.py          # Database CRUD operations
│   ├── causal.py                 # Statistical analysis
│   └── login_ui.py               # Login UI components
│
├── scripts/                      # Utility scripts
│   ├── comprehensive_test.py     # Automated test suite
│   ├── create_test_users.py      # Generate test data
│   └── ...                       # Other utilities
│
├── data/                         # Data files
│   ├── evidence_counts.csv       # Clinical trials evidence
│   ├── test_users.json           # Test users (20 users, 90 days each)
│   └── templates/                # CSV templates
│
├── docs/                         # 📚 Documentation
│   ├── BEARABLE_BRAND_GUIDE.md   # Brand guidelines
│   ├── TEST_PLAN_V28.md          # Test plan
│   ├── TEST_REPORT_V28_FINAL.md  # Test results
│   └── ...                       # Other docs
│
└── .streamlit/                   # Streamlit config
    └── secrets.toml              # Environment variables
```

---

## 🧪 Testing

### Comprehensive Test Suite
We've run **comprehensive automated testing** with **100% pass rate**!

```bash
# Run automated tests
python scripts/comprehensive_test.py

# Create test users (20 users with 90 days of data each)
python scripts/create_test_users.py
```

### Test Results: ✅ 9/9 Tests Passing (100%)
- ✅ File existence and structure validation
- ✅ Test user data generation (20 users, 90 days each)
- ✅ Therapy tracking functionality
- ✅ Multiple therapies per user
- ✅ Before/after therapy data analysis
- ✅ CSV/JSON export functionality
- ✅ Date range validation
- ✅ Data integrity checks

See [TEST_REPORT_V28_FINAL.md](TEST_REPORT_V28_FINAL.md) for complete results.

---

## 🚢 Deployment

### Streamlit Cloud (Recommended)
1. Fork this repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add environment variables in dashboard
4. Deploy! 🎉

### Self-Hosted
```bash
# Using Python directly
pip install -r requirements.txt
streamlit run app/app_v28_final.py

# Using Docker (optional)
docker build -t bearable .
docker run -p 8501:8501 --env-file .env bearable
```

---

## 🔧 Configuration

### Environment Variables

Create a `.streamlit/secrets.toml` file:

```toml
[SUPABASE]
url = "https://your-project.supabase.co"
key = "your-anon-key-here"
```

**Security Note:** Never commit secrets to version control!

---

## 🔐 Security & Privacy

### Security Features
- ✅ SQL injection protection (parameterized queries)
- ✅ XSS protection (input sanitization)
- ✅ Password hashing (bcrypt via Supabase)
- ✅ JWT session tokens (httpOnly cookies)
- ✅ Row-level security (RLS policies)
- ✅ Environment variable protection

### Privacy Commitment
- Your health data is **never shared** without your consent
- Data is encrypted **at rest and in transit**
- You can **export or delete** your data anytime
- We don't sell or monetize your personal information
- Open-source code - verify for yourself!

---

## 🗺️ Version History

### ✅ v28 (Current) - October 2025
- [x] 🎨 **Beautiful purple branding** - Gradient buttons, cohesive design
- [x] ✅ **Comprehensive testing** - 9/9 tests passing, 20 test users, 90 days of data
- [x] 🐛 **Bug fixes** - Add Note, Evidence Explorer dropdown z-index
- [x] 📊 **Improved gauges** - Better value formatting
- [x] 🔧 **Code quality** - Cleaner, more maintainable codebase

### ✅ v27 (Previous)
- [x] 🌐 **Live API integration** - ClinicalTrials.gov & PubMed
- [x] Real-time evidence data fetching
- [x] 24-hour intelligent caching
- [x] Automatic CSV fallback

### 🔮 Future
- [ ] Mobile app (React Native)
- [ ] Wearable device integration
- [ ] Enhanced AI insights
- [ ] Multi-language support
- [ ] Dark mode

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch
3. **Commit** your changes
4. **Push** to the branch
5. **Open** a Pull Request

---

## 📊 Stats

- **📝 Lines of Code:** 4,600+
- **🔬 Clinical Trials:** 500,000+
- **📚 PubMed Articles:** 30M+
- **🏥 Health Conditions:** 30+
- **🌿 Natural Therapies:** 24+
- **🧪 Tests:** 9/9 passing (100%)
- **👥 Test Users:** 20 users with 90 days of data

---

## 💡 Use Cases

### For Individuals
- Track chronic pain and discover triggers
- Test if natural therapies work with statistical rigor
- Optimize sleep, stress, and mood
- Share data-driven insights with doctors

### For Healthcare Providers
- Give patients structured tracking tools
- Review objective symptom data
- Make evidence-based treatment decisions
- Support shared decision-making

### For Researchers
- Collect N-of-1 trial data
- Study real-world therapy effectiveness
- Analyze symptom correlations
- Aggregate anonymized data

---

## 🙏 Acknowledgements

### Data Sources
- **ClinicalTrials.gov** - AACT database
- **PubMed** - E-utilities API
- **National Library of Medicine** - Research access

### Technologies
- **Streamlit** - Web framework
- **Supabase** - Backend infrastructure
- **Plotly** - Data visualization
- **Python** - Scientific computing ecosystem

---

## 📞 Support

- **💬 GitHub Issues:** [Report a bug](https://github.com/jessicapaes/bearable/issues)
- **📖 Documentation:** [View docs](https://github.com/jessicapaes/bearable/tree/main/docs)
- **⭐ Star us:** Help others discover Bearable!

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ⭐ Star History

If you find Bearable useful, please consider starring the repository! ⭐

Made with ❤️ and 🐻 for people managing chronic health conditions.

---

**Last Updated:** October 27, 2025  
**Version:** v28  
**Status:** Production Ready ✅  
**Tests:** 9/9 Passing (100%) 🎉  
**APIs:** Live & Operational 🟢
