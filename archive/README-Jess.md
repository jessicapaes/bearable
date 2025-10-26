# 🐻 Bearable - Health Tracking & Pain Management App

A comprehensive health tracking application built with Streamlit that helps users monitor their daily health metrics, pain levels, and discover evidence-based therapies.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 📋 Features

### 🌱 Daily Health Logging
- Quick 30-second daily log entry
- Track pain levels (1-10 scale)
- Monitor sleep quality and duration
- Log physical activity and exercise
- Track therapy usage and effectiveness
- Record menstrual cycle data
- Mood and stress level monitoring

### 📊 Interactive Dashboard
- Visual pain trend analysis with interactive charts
- Sleep quality correlation insights
- Therapy effectiveness tracking
- Statistical analysis with confidence intervals
- **🔬 Causal Analysis using Difference-in-Differences (DiD)**
- Personalized health insights

### 🔬 Evidence Explorer
- Database of 15+ evidence-based pain therapies
- Research-backed information (PubMed articles, clinical trials)
- Evidence level ratings (Strong/Moderate/Emerging)
- Detailed therapy descriptions and use cases

### 👤 Account Management
- Secure authentication system
- Profile editing (name, email)
- Password change functionality
- Account deletion option
- Demo mode for trying the app

### 🎨 Modern UI/UX
- Glass-morphism design
- Responsive layout
- Sticky header navigation
- Interactive visualizations with Plotly
- Clean, intuitive interface

## 🚀 Live Demo

Try the app: [https://your-username-bearable.streamlit.app](https://your-username-bearable.streamlit.app)

**Demo Credentials:**
- Username: `demo`
- Password: `demo`

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Data Visualization**: Plotly, Pandas
- **Data Analysis**: NumPy, SciPy
- **Authentication**: Custom session-based auth
- **Storage**: JSON (accounts), CSV (user data)

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/painreliefmap.git
cd painreliefmap
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run bearable.py
```

4. Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
painreliefmap/
├── bearable.py              # Main application file
├── requirements.txt         # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── data/
│   └── accounts.json       # User accounts (gitignored)
├── app/
│   └── bear_icon.svg       # App icon
└── README.md               # This file
```

## 🔒 Security Notes

- Passwords are hashed using SHA-256
- Session-based authentication
- User data stored locally (not in git)
- Add `data/accounts.json` to `.gitignore` before deploying

## 📊 Data Model

### Health Log Entry
```python
{
    "date": "2025-10-23",
    "pain_level": 5,
    "sleep_hours": 7.5,
    "sleep_quality": "Good",
    "activity_level": "Moderate",
    "therapies_used": ["Yoga", "Meditation"],
    "mood": "Positive",
    "stress_level": "Low"
}
```

### User Account
```python
{
    "email": "user@example.com",
    "name": "User Name",
    "password": "hashed_password",
    "username": "user@example.com"
}
```

## 🎯 Assessment Requirements Met

✅ **Data Pipeline** - Demo data generation and user data collection
✅ **Interactive Dashboard** - Streamlit with multiple tabs and visualizations
✅ **EDA** - Comprehensive exploratory data analysis with statistical insights
✅ **Data Storytelling** - Clear insights in Evidence Explorer and Dashboard
✅ **Causal Analysis** - **Difference-in-Differences (DiD)** for therapy effectiveness
✅ **Deployment** - Live on Streamlit Cloud

### Future Enhancements
- 🔄 **SQL Integration** - PostgreSQL for scalable data storage
- 🔄 **Advanced ML** - Predictive models for personalized recommendations
- 🔄 **Mobile App** - Native iOS/Android versions

## 🐛 Known Issues

- Footer white space on some browsers (cosmetic only)
- Dropdown auto-minimize feature in development

## 🤝 Contributing

This is an academic project for AI Tech Institute. Contributions welcome after October 28, 2025.

## 📝 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

**Jessica Paes**  
AI Tech Institute Course Project  
Presentation Date: October 28, 2025

## 🙏 Acknowledgments

- Health data insights based on real research
- UI/UX inspired by modern health apps
- Built with ❤️ using Streamlit

---

**Note**: This app is for educational and tracking purposes only. Always consult healthcare professionals for medical advice.
