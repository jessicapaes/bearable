# Bearable: Evidence-Based Health Tracking
## 10-Minute Investor Presentation

---

# 🎨 DESIGN INSTRUCTIONS FOR GAMMA

**IMPORTANT: Apply these design settings to all slides**

## Color Scheme
- **Primary Background**: Purple gradient `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Accent Color**: Pink gradient `linear-gradient(135deg, #ec4899 0%, #f472b6 100%)`
- **Text on Purple**: White (#FFFFFF)
- **Text on White**: Dark Gray (#1a202c)
- **Buttons/CTAs**: Pink gradient (#ec4899 to #f472b6)

## Logo & Icons
- **Bear Logo**: Use white bear icon on purple gradient backgrounds
- **Icon Style**: Simple, rounded, modern emoji style (🐻, 🔬, 📊, 📈)
- **Logo Placement**: Top center or left corner on title slides

## Typography
- **Font Family**: Inter (Google Fonts) - clean, modern, professional
- **Title Slides**: 48pt Bold, white text on purple gradient
- **Section Headers**: 36pt Bold
- **Body Text**: 24pt Regular, clear line spacing
- **Accent Text**: Use pink color for emphasis

## Slide Backgrounds
- **Title/Hero Slides**: Full purple gradient background
- **Content Slides**: White or light gray background with purple accents
- **CTA Slides**: Purple gradient with white text
- **Data Slides**: Clean white with purple/pink charts

## Visual Style
- Clean, minimal, professional
- Rounded corners on cards and buttons (12-25px radius)
- Subtle shadows for depth
- High contrast for readability
- Modern healthcare/tech aesthetic

## Bear Icon SVG (White version for purple backgrounds):
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" style="width: 80px; height: 80px;">
    <circle cx="28" cy="28" r="18" fill="#ffffff"/>
    <circle cx="72" cy="28" r="18" fill="#ffffff"/>
    <circle cx="50" cy="55" r="35" fill="#ffffff"/>
    <ellipse cx="50" cy="68" rx="20" ry="15" fill="#f0f0f0"/>
</svg>
```

**Apply this theme consistently throughout the presentation!**

---

# The Challenge

**1 in 2 adults have chronic health conditions**

When they try new therapies:

- ❌ Overwhelmed by 500,000+ clinical trials
- ❌ No systematic way to track effectiveness
- ❌ Can't distinguish real effects from placebo
- ❌ Relying on memory alone

---

# Bearable Solves All Three

## 🔬 Live Evidence
Real-time data from 500,000+ clinical trials
ClinicalTrials.gov + PubMed APIs

## 📊 Personal Tracking
30-second daily logs
Pain, sleep, mood, therapies
Cloud-synced, secure

## 📈 Statistical Proof
Bootstrap analysis
95% confidence intervals
Know what actually works

---

# Demo: Welcome & How It Works

**📹 VIDEO: Homepage Demo (30 seconds)**

*This video should show:*
- Landing page with "Welcome to Bearable" hero section
- The 4-step "How It Works" section
- Scrolling to "START FREE DEMO" button
- Clicking the button and entering demo mode
- Quick tour of the main navigation tabs

**Key moments to highlight:**
- Clean, professional interface
- Purple/pink gradient branding
- One-click demo access (no signup required)
- Main navigation: Dashboard, Daily Log, Evidence Explorer, Settings

---

# Live Scientific Evidence

**📹 VIDEO: Evidence Explorer Demo (45 seconds)**

*This video should show:*
- Clicking on "Evidence Explorer" tab
- Selecting condition: "Chronic Pain" (or "Low Back Pain")
- Showing multiple therapy options with evidence levels
- Clicking on a therapy card (e.g., Acupuncture)
- Highlighting the live API data:
  - Clinical trials count: 487
  - PubMed articles: 2,300+
  - Evidence level badge: Positive ✅
- Scrolling to show therapy definition
- Clicking "View Studies" link

**Key features demonstrated:**
- Real-time API queries to ClinicalTrials.gov and PubMed
- Multiple filter options (30+ conditions, 24+ therapies)
- Clean, professional data presentation
- Direct research links
- Evidence-based recommendations

---

# Evidence at Your Fingertips

**Each therapy card shows:**

- Therapy name and clinical definition
- Number of clinical trials
- Number of published research articles
- Evidence level (Positive/Mixed/Negative)
- Direct links to ClinicalTrials.gov
- Direct links to PubMed studies

**Users can filter and compare therapies instantly**

---

# 30-Second Daily Tracking

**Daily Log Features:**

✅ Pain score (0-10 slider)
✅ Sleep hours tracked
✅ Mood score
✅ Physical symptoms
✅ Emotional state
✅ Therapies used today

**The Magic Feature:**
🎯 "Started new primary therapy today" checkbox

This enables true N-of-1 trials with before/after comparison

---

# Personal Experiments with Statistical Rigor

**N-of-1 Trial Process:**

**Before Therapy** → **Start** → **After Therapy**
(7 days data) → (Check the box) → (23 days data)

Average Pain: 7/10 → **Therapy Begins** → Average Pain: 4.8/10

↓

**Statistical Analysis**
- Bootstrap confidence intervals
- Effect size calculation (Cohen's d)
- Significance testing

↓

**Result: 32% Pain Reduction**
**95% Confident This Is Real** ✅

---

# Personal Health Science

**Dashboard Features:**

📊 Real-time health metrics
- Pain level gauge
- Sleep hours tracker
- Mood score visualization

📈 14-day trend analysis
- Pain trajectory over time
- Sleep quality patterns
- Mood correlations

🧘🏻‍♀️ Therapy effectiveness cards
- Exact day therapy started (marked)
- Before vs. After comparison
- Statistical confidence rating

---

# Statistical Certainty, Not Guesswork

**Therapy Effect Analysis Shows:**

- **Effect Size**: -2.2 points (Substantial improvement)
- **Pain Reduction**: 32% decrease
- **Reliability**: ✅ Results Look Reliable
- **Data Points**: 7 days before, 23 days after
- **Confidence**: 95% certain this is real, not placebo
- **Method**: Bootstrap analysis with confidence intervals

**This is scientific proof of what works for YOU**

---

# Production-Ready Architecture

## Frontend
**Streamlit (Python)**
Web framework, mobile-ready

## Live APIs
**ClinicalTrials.gov + PubMed**
Real-time data with 24-hour caching

## Backend
**Supabase (PostgreSQL)**
Row-level security, JWT authentication

## Analytics Engine
**SciPy/NumPy/Pandas**
Bootstrap analysis, correlations, statistical computing

---

# Scale & Impact

## 500,000+
Clinical Trials Indexed

## 30M+
PubMed Articles Searchable

## 30+
Health Conditions Tracked

---

## 24+
Natural Therapies Catalogued

## <100ms
Cached Response Time

## 99%
API Call Reduction via Intelligent Caching

---

# Enterprise-Grade Security

✅ **Row-Level Security** - Database-level isolation
✅ **JWT Authentication** - Industry standard
✅ **Password Hashing** - bcrypt encryption
✅ **GDPR Compliant** - Export/delete on demand
✅ **Encryption** - At rest and in transit
✅ **Open Source** - Auditable by anyone

**Protected Against:**
- SQL Injection
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)

**Passed comprehensive security audit**

---

# What's Next

## v27 (NOW) ✅
- Live API integration
- Bootstrap statistical analysis
- Mobile responsive design
- Production ready

## v28 (30 days) 🔄
- NCBI API key (10x faster PubMed)
- Email validation
- Batch CSV import

## v29-30 (90 days) 🚀
- Wearable device integration
- AI-powered insights
- React Native mobile app
- Predictive modeling

## Future 🌍
- International expansion
- Multi-language support
- Team/family accounts
- Community insights

---

# Join Us

## 👥 For Users
**Try Bearable Free**
bearable.app
Open source, no credit card required

## 💼 For Partners
**Healthcare Providers & Research Institutions**
Let's collaborate on clinical implementations

## 💰 For Investors
**Seed Round Open**
Scaling to 1M+ users
Schedule a meeting

---

# Thank You

**🐻 [White Bear Logo - Place at Top Center]**

## **BEARABLE**
Evidence-Based Health Tracking

🌐 **bearable.app**
📧 **contact@bearable.app**
💻 **github.com/bearable/app**

**Transform Personal Health Tracking**
**Into Personal Health Science**

### Questions?

**Design Note:** This slide should have purple gradient background with white text and white bear logo at top

---

# Brand Guidelines

## Color Palette - APPLY TO ALL SLIDES

**Primary Purple Gradient (Main Brand):**
- Light: #667eea (RGB: 102, 126, 234)
- Dark: #764ba2 (RGB: 118, 75, 162)
- CSS: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Use for:** Title slides, headers, navigation, key UI elements

**Pink Accent Gradient (Interactive Elements):**
- Light: #f472b6 (RGB: 244, 114, 182)
- Dark: #ec4899 (RGB: 236, 72, 153)
- CSS: `linear-gradient(135deg, #ec4899 0%, #f472b6 100%)`
- **Use for:** CTAs, buttons, accent highlights, DEMO MODE badge

**Text Colors:**
- White (#FFFFFF) - on purple backgrounds
- Dark Gray (#1a202c) - on white backgrounds
- Medium Gray (#64748b) - secondary text

## Typography
**Font Family:** Inter (Google Fonts)
**Weights:** 300, 400, 500, 600, 700, 800, 900
**Import:** Use Google Fonts Inter for all text

## Logo Usage
**Bear Icon:** White bear on purple gradient or colored bear on white
**Placement:** Top center of title slides, top left of content slides
**Size:** 60-80px for main logo, 40px for header logo

---

# Design Specifications

## Slide Layout
- **Aspect Ratio:** 16:9 widescreen
- **Transitions:** Fade (0.3s)
- **Animations:** Appear (0.2s delay per element)

## Typography Hierarchy
- **Title Slides:** 48pt Bold
- **Section Headers:** 36pt Bold
- **Body Text:** 24pt Regular
- **Captions:** 18pt Regular

## Visual Style
- Purple gradient backgrounds for key slides
- White text on dark backgrounds
- Clean, minimal design
- Professional data visualization
- Consistent spacing and alignment

---

# Presentation Notes

**Total Duration:** 10 minutes
- 5 minutes: Core presentation
- 5 minutes: Q&A

**Key Emphasis Points:**
1. "Live" API data (real-time, not static)
2. Statistical confidence (95%, not guessing)
3. N-of-1 trials (personal experiments)
4. Security & privacy (GDPR, open source)
5. Production-ready (not a prototype)

**Presenter Tips:**
- Speak clearly, don't rush
- Make eye contact with audience
- Point to specific UI elements
- Show enthusiasm for the product
- Handle Q&A gracefully

---

# Appendix: Business Model

## Revenue Streams

**Freemium Model**
- Basic: Free forever
- Premium: $9.99/month

**Healthcare Partnerships**
- White-label for clinics
- Enterprise pricing

**Research Licensing**
- Anonymized aggregate data
- Academic partnerships

**API Access**
- Developer tier
- Usage-based pricing

---

# Appendix: Competitive Advantage

| Feature | Bearable | Competitor A | Competitor B |
|---------|----------|--------------|--------------|
| Live Scientific Data | ✅ | ❌ | ❌ |
| Statistical Analysis | ✅ | ~ | ❌ |
| N-of-1 Trials | ✅ | ❌ | ❌ |
| Open Source | ✅ | ❌ | ❌ |
| Real-time APIs | ✅ | ❌ | ❌ |
| GDPR Compliant | ✅ | ~ | ✅ |

**Bearable uniquely combines scientific evidence with personal tracking and statistical rigor**

---

# Contact & Resources

**Website:** bearable.app
**Email:** contact@bearable.app
**GitHub:** github.com/bearable/app
**Demo Account:** username: demo, password: demo

**Try it yourself - no signup required!**

---

**END OF PRESENTATION**

*This presentation was generated from the Bearable v27 specification*
*Last Updated: January 26, 2025*
*Version: 1.0*

