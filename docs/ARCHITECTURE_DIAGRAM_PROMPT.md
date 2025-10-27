# Architecture Diagram Prompt for Gamma

## Use This Prompt in Gamma:

Create a modern, professional architecture diagram showing a **medical/health tech application stack** with the following components arranged visually:

### Layout: Bottom to Top (Data Flow)

**Bottom Layer - Database:**
- Large blue box labeled "Supabase (PostgreSQL)"
- Include icon: 🔒 (lock)
- Features listed below:
  - Row-Level Security (RLS)
  - JWT Authentication
  - User Data Isolation

**Middle Layer - APIs:**
- Two side-by-side boxes:
  - Left: "ClinicalTrials.gov API" with icon: 🏥
  - Right: "PubMed API" with icon: 📚
- Both boxes same height, different shades of purple
- Arrow flowing UP from Supabase to both APIs
- Small text: "Real-time data with 24-hour caching"

**Top Layer - Application:**
- Large purple gradient box labeled "Streamlit Web App"
- Include icon: 🌐
- Smaller boxes inside showing:
  - Dashboard (📊)
  - Daily Log (📝)
  - Evidence Explorer (🔬)
- Python logo visible
- "Mobile-responsive" badge

**Security Layer (wrap around):**
- Thin border around entire diagram
- Label: "Enterprise-Grade Security"
- Small lock icons 🔒 at each layer

### Visual Style:
- Clean, minimalist design
- Purple gradient color scheme (#667eea to #764ba2)
- White text on colored backgrounds
- Arrows showing data flow
- Modern flat design (no 3D)
- Professional tech aesthetic

### Typography:
- Component names: Bold, 18pt
- Features: Regular, 12pt
- Subtext: Italic, 10pt

---

## Alternative Simplified Version:

If the above is too complex, use this simpler version:

**Three-Column Layout:**

Column 1: **Backend**
- Supabase logo
- PostgreSQL database icon
- "Row-Level Security"

Column 2: **APIs** (Center)
- ClinicalTrials.gov logo
- PubMed logo
- "Real-time Data"

Column 3: **Frontend**
- Streamlit logo
- Python icon
- "Mobile-Ready UI"

Connect columns with arrows → showing data flow

---

## For AI Image Generators (DALL-E, Midjourney):

"Create a clean, modern architecture diagram for a health tech application. Show a three-tier system from bottom to top: 1) Database layer with PostgreSQL/Supabase in blue, 2) API layer with ClinicalTrials.gov and PubMed in purple, 3) Application layer with Streamlit in gradient purple. Use minimalist flat design, purple color scheme #667eea to #764ba2, white text, arrows showing data flow upward. Professional tech aesthetic, no text labels visible - just icons and colored shapes"

---

## ASCII Architecture (for documentation):

```
                    ┌─────────────────────────────────┐
                    │   Streamlit Web Application     │
                    │   🌐 Python • Mobile-Ready      │
                    │                                 │
                    │  📊 Dashboard  📝 Daily Log     │
                    │  🔬 Evidence Explorer           │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
        ┌───────────▼───┐        ┌──────────▼──────┐
        │ClinicalTrials │        │   PubMed API    │
        │   .gov API    │        │                 │
        │      🏥       │        │      📚         │
        └───────────┬───┘        └──────────┬──────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Supabase (PostgreSQL) │
                    │         🔒             │
                    │  • Row-Level Security  │
                    │  • JWT Authentication  │
                    │  • User Isolation      │
                    └───────────────────────┘

        🔒 Enterprise-Grade Security Wrapper
```

---

## Quick Text Description for Slides:

**"Production-Ready Architecture"**

**Backend:** Supabase PostgreSQL with Row-Level Security  
**APIs:** Real-time data from ClinicalTrials.gov & PubMed  
**Frontend:** Streamlit web app (Python, mobile-responsive)  
**Security:** JWT authentication, encrypted in transit/at rest

---

**Use any of these formats in Gamma or other tools!**

