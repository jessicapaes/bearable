# 🐻 Bearable - Evidence-Based Health Tracking

> **Track your health journey with science-backed insights. Explore evidence from 500,000+ clinical trials, track your symptoms, and discover what actually works for you.**

[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://github.com/jessicapaes/bearable)
[![Version](https://img.shields.io/badge/version-v27-blue)](https://github.com/jessicapaes/bearable/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🌐 NEW in v27: Live API Integration!

**Real-time evidence data** directly from ClinicalTrials.gov and PubMed APIs!

- 🔴 **Live Data:** Connect to official APIs for up-to-the-minute clinical trial and research counts
- ⚡ **Smart Caching:** 24-hour cache reduces API calls by 99% while keeping data fresh
- 🛡️ **Reliable:** Automatic fallback to CSV if APIs are unavailable
- 🆓 **Free:** No API keys or configuration required
- 📊 **Performance:** 2-5s first load, <100ms cached loads

See [V27_LIVE_API_INTEGRATION.md](docs/V27_LIVE_API_INTEGRATION.md) for complete details.

---

## ✨ What is Bearable?

Bearable is a comprehensive health tracking application that combines **evidence-based research** with **personal data tracking** to help you discover which natural therapies actually work for your health conditions.

### 🎯 Perfect For
- **Chronic pain management** - Track symptoms and therapy effectiveness
- **N-of-1 trials** - Run personal experiments with statistical analysis
- **Natural therapy research** - Explore evidence from clinical trials
- **Health optimization** - Discover patterns and correlations
- **Doctor consultations** - Share data-driven insights with providers

---

## 🚀 Quick Start

### Try Demo Mode (No Setup)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app (with live APIs!)
streamlit run app/app_v27_final.py

# 3. Click "Continue in Demo Mode"
```

Open [http://localhost:8501](http://localhost:8501) and start tracking!

### Full Setup (5 Minutes)
```bash
# 1. Clone and install
git clone https://github.com/jessicapaes/bearable.git
cd bearable
pip install -r requirements.txt

# 2. Set up Supabase (free tier)
python setup_auth.py  # Interactive wizard

# 3. Run the app (with live APIs!)
streamlit run app/app_v27_final.py
```

📖 **Detailed setup:** See [QUICKSTART_AUTH.md](docs/QUICKSTART_AUTH.md)

---

## 🌟 Key Features

### 🔐 Secure & Private
- **User authentication** with email verification
- **Password reset** via secure links
- **Row-level security** - your data is yours alone
- **Cloud storage** with Supabase (PostgreSQL)
- **GDPR compliant** - export or delete your data anytime

### 📊 Personal Dashboard
- **Health metrics** - pain, sleep, mood trends
- **Interactive charts** - 14-day visualizations with Plotly
- **Therapy analysis** - statistical before/after comparison
- **Correlation matrix** - discover what affects your symptoms
- **Timeline markers** - see when you started therapies
- **Automated insights** - AI-powered pattern detection

### 🔬 Evidence Explorer (NEW: Live API Data!)
- **🔴 Real-time data** from ClinicalTrials.gov API v2
- **🔴 Live PubMed counts** via E-utilities API
- **500,000+ clinical trials** - always up-to-date
- **30M+ research articles** - current counts
- **Evidence ratings** - Positive, Mixed, Negative
- **Filter by condition** - 30+ health conditions
- **Natural therapies** - yoga, acupuncture, supplements, and more
- **Smart caching** - fast loads with fresh data
- **Automatic fallback** - CSV backup if APIs unavailable

### 🌱 Daily Log (30 seconds/day)
- **Core metrics:** Pain (0-10), Sleep (hours), Mood (0-10)
- **Physical state:** Movement, digestion, bowel habits
- **Emotional symptoms:** Anxiety, stress levels
- **Therapy tracking:** Mark when you start/stop therapies
- **Menstrual cycle:** Optional hormone tracking
- **Quick actions:** Duplicate yesterday, add notes, mark good days
- **Auto-save:** Data syncs to cloud automatically

### 📈 N-of-1 Analysis
- **Statistical rigor** - Bootstrap confidence intervals
- **Before/after comparison** - 3 days before, 10 days after minimum
- **Effect size** - Cohen's d calculation
- **P-value** - statistical significance testing
- **Visual results** - beautiful gradient cards with insights
- **Plain English** - no statistics degree needed

### ⚙️ Data Management
- **CSV export** - download all your data
- **PDF reports** - shareable with healthcare providers
- **Data import** - restore from backups
- **Account settings** - update profile, change password
- **Secure deletion** - remove your account anytime

---

## 📱 Screenshots

### Dashboard
![Dashboard](https://placehold.co/800x400/667eea/FFFFFF?text=Health+Dashboard)

*Track pain, sleep, and mood trends with interactive visualizations*

### Evidence Explorer
![Evidence Explorer](https://placehold.co/800x400/764ba2/FFFFFF?text=Evidence+Explorer)

*Explore evidence for natural therapies across 30+ health conditions*

### Daily Log
![Daily Log](https://placehold.co/800x400/f093fb/FFFFFF?text=Daily+Wellness+Log)

*Log your symptoms in 30 seconds with an intuitive interface*

---

## 🏗️ Tech Stack

### Frontend
- **Streamlit** - Rapid web app development
- **Plotly** - Interactive data visualizations
- **HTML/CSS** - Custom styling and responsive design

### Backend  
- **Supabase** - Authentication & PostgreSQL database
- **Python 3.12** - Core application logic
- **Pandas/NumPy** - Data processing
- **SciPy** - Statistical analysis

### Data Sources
- **ClinicalTrials.gov API v2** - Live clinical trials data (NEW in v27!)
- **PubMed E-Utilities API** - Live research article counts (NEW in v27!)
- **Supabase PostgreSQL** - User health tracking data
- **CSV Fallback** - Offline/backup evidence data

---

## 📂 Project Structure

```
bearable/
├── README.md                     # 📖 You are here
├── requirements.txt              # Python dependencies  
├── runtime.txt                   # Python version for deployment
├── setup_auth.py                 # 🚀 Interactive setup wizard
│
├── app/                          # Streamlit applications
│   ├── app_v27_final.py          # 🚀 LATEST - Live APIs + Production
│   ├── app_v26_final.py          # Previous stable version
│   └── bear_icon.svg             # App icon
│
├── src/                          # Core modules
│   ├── auth.py                   # Authentication manager
│   ├── db_operations.py          # Database CRUD operations
│   ├── causal.py                 # Statistical analysis
│   └── login_ui.py               # Login UI components
│
├── scripts/                      # Utility scripts
│   ├── create_user_tables.sql    # Database schema
│   ├── build_evidence_counts.py  # Evidence data builder
│   ├── test_app.py               # Application tests
│   └── verify_setup.py           # Setup verification
│
├── data/                         # Data files
│   ├── evidence_counts.csv       # Clinical trials evidence
│   └── templates/                # CSV templates for tracking
│
├── docs/                         # 📚 Documentation
│   ├── QUICKSTART_AUTH.md        # ⭐ 5-min setup guide
│   ├── AUTHENTICATION_SETUP.md   # Detailed auth guide
│   ├── V27_LIVE_API_INTEGRATION.md  # 🌐 Live API docs
│   ├── V26_COMPREHENSIVE_AUDIT_FINDINGS.md  # Security audit
│   └── ...                       # Version changelogs & guides
│
├── config/                       # Configuration files
│   ├── config.env.example        # Environment variables template
│   └── env_template.txt          # Alternative env template
│
├── deployment/                   # Deployment scripts
│   ├── run_app.bat               # Windows batch script
│   └── run_app.ps1               # PowerShell script
│
└── archive/                      # Archived/legacy files
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root (or copy from `config/config.env.example`):

   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

**Security Note:** Never commit `.env` to version control!

📁 **Example file:** See `config/config.env.example` for a template

### Database Schema

The app requires these Supabase tables:
- `user_profiles` - User account information
- `user_logs` - Daily health tracking data
- `app_users` - Quick lookup table (optional)

Run `scripts/create_user_tables.sql` in Supabase SQL Editor to create them.

---

## 🧪 Testing

### Automated Tests
```bash
# Run linter
python -m pylint app/app_v26_final.py

# Check for security issues
python -m bandit -r app/
```

### Manual Testing Checklist
- ✅ Create account → Verify email → Login
- ✅ Log 7 days of data → View dashboard charts
- ✅ Start therapy → Log 10 more days → See analysis
- ✅ Export data to CSV → Verify content
- ✅ Change password → Login with new password
- ✅ Test on mobile (responsive design)

---

## 🚢 Deployment

### Streamlit Cloud (Recommended)
1. Fork this repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add environment variables in dashboard
4. Deploy! 🎉

### Self-Hosted
```bash
# Using Docker
docker build -t bearable .
docker run -p 8501:8501 --env-file .env bearable

# Using systemd
sudo systemctl enable bearable.service
sudo systemctl start bearable
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART_AUTH.md](docs/QUICKSTART_AUTH.md) | ⭐ 5-minute authentication setup |
| [AUTHENTICATION_SETUP.md](docs/AUTHENTICATION_SETUP.md) | Detailed integration guide |
| [V27_LIVE_API_INTEGRATION.md](docs/V27_LIVE_API_INTEGRATION.md) | 🌐 **NEW!** Live API documentation |
| [V26_COMPREHENSIVE_AUDIT_FINDINGS.md](docs/V26_COMPREHENSIVE_AUDIT_FINDINGS.md) | Security audit report |
| [AUTHENTICATION_ARCHITECTURE.md](docs/AUTHENTICATION_ARCHITECTURE.md) | Technical architecture |

---

## 🔐 Security & Privacy

### Security Features
- ✅ SQL injection protection (parameterized queries)
- ✅ XSS protection (input sanitization)
- ✅ Password hashing (bcrypt via Supabase)
- ✅ JWT session tokens (httpOnly cookies)
- ✅ Row-level security (RLS policies)
- ✅ Environment variable protection
- ✅ Rate limiting (Supabase Auth)

### Privacy Commitment
- Your health data is **never shared** without your consent
- Data is encrypted **at rest and in transit**
- You can **export or delete** your data anytime
- We don't sell or monetize your personal information
- Open-source code - verify for yourself!

📄 **Full security audit:** [V26_COMPREHENSIVE_AUDIT_FINDINGS.md](docs/V26_COMPREHENSIVE_AUDIT_FINDINGS.md)

---

## 🗺️ Roadmap

### ✅ v27 (Current)
- [x] 🌐 **Live API integration** - ClinicalTrials.gov & PubMed
- [x] Real-time evidence data fetching
- [x] 24-hour intelligent caching
- [x] Automatic CSV fallback
- [x] Rate limiting protection

### ✅ v26 (Previous)
- [x] Comprehensive security audit
- [x] Mobile responsive design
- [x] Enhanced Evidence Explorer UX
- [x] Scroll-to-top navigation
- [x] Production-ready documentation

### 🚧 v28 (Next)
- [ ] NCBI API key support (10 req/sec for PubMed)
- [ ] Parallel API requests for bulk loading
- [ ] Email validation & password strength meter
- [ ] Data export compression (ZIP)
- [ ] Batch data import from CSV

### 🔮 Future
- [ ] Mobile app (React Native)
- [ ] Wearable device integration
- [ ] AI-powered insights
- [ ] Multi-language support
- [ ] Social features (share with doctor)
- [ ] Dark mode

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
git clone https://github.com/jessicapaes/bearable.git
cd bearable
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
streamlit run app/app_v26_final.py
```

---

## 🐛 Troubleshooting

### Common Issues

**"Supabase connection failed"**
- Check your `.env` file exists with correct credentials
- Verify URL format: `https://xxx.supabase.co` (no trailing slash)

**"Table doesn't exist"**
- Run `scripts/create_user_tables.sql` in Supabase SQL Editor
- Check that tables were created successfully

**"App won't start"**
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.9+ required)

**"Data not saving"**
- Verify you're logged in (not demo mode)
- Check RLS policies are enabled in Supabase
- Check browser console for errors

📚 **More help:** See [AUTHENTICATION_SETUP.md](docs/AUTHENTICATION_SETUP.md)

---

## 📊 Stats

- **📝 Lines of Code:** 4,000+
- **🔬 Clinical Trials:** 500,000+
- **📚 PubMed Articles:** 30M+
- **🏥 Health Conditions:** 30+
- **🌿 Natural Therapies:** 24+
- **⭐ User Rating:** Production Ready

---

## 💡 Use Cases

### For Individuals
- Track chronic pain and discover triggers
- Test if therapies work with statistical rigor
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
- **PubMed** - E-Utilities API
- **National Library of Medicine** - Research access

### Technologies
- **Streamlit** - Web framework
- **Supabase** - Backend infrastructure
- **Plotly** - Data visualization
- **Python** - Scientific computing ecosystem

### Community
- Open-source contributors
- Beta testers and early users
- Healthcare professionals providing feedback

---

## 📞 Support

- **📧 Email:** support@bearable.app (coming soon)
- **💬 GitHub Issues:** [Report a bug](https://github.com/jessicapaes/bearable/issues)
- **📖 Documentation:** [View docs](https://github.com/jessicapaes/bearable/tree/main/docs)
- **🌐 Website:** bearable.app (coming soon)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## ⭐ Star History

If you find Bearable useful, please consider starring the repository! ⭐

Made with ❤️ for people managing chronic health conditions.

---

**Last Updated:** January 26, 2025  
**Version:** v27  
**Status:** Production Ready ✅  
**APIs:** Live & Operational 🟢
