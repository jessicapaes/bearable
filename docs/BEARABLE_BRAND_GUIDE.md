# Bearable - Brand & Design System Guide

## 🎨 Brand Identity

### Brand Name
**Bearable**

### Tagline
"Evidence-Based Health Tracking"

### Mission Statement
Transform personal health tracking into personal health science through evidence-based insights and statistical rigor.

---

## 🎨 Color Palette

### Primary Colors

#### Purple Gradient (Main Brand)
- **Light Purple**: `#667eea` (RGB: 102, 126, 234)
- **Dark Purple**: `#764ba2` (RGB: 118, 75, 162)
- **Gradient**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Usage**: Primary buttons, headers, key UI elements, tabs, main branding

#### Pink Accent (Interactive Elements)
- **Light Pink**: `#f472b6` (RGB: 244, 114, 182)
- **Dark Pink**: `#ec4899` (RGB: 236, 72, 153)
- **Gradient**: `linear-gradient(135deg, #ec4899 0%, #f472b6 100%)`
- **Usage**: Login button, Quick Actions, secondary CTAs, DEMO MODE badge

### Secondary Colors

#### Text & Neutrals
- **Primary Text**: `#1a202c` (Dark Gray)
- **Secondary Text**: `#334155` (Medium Gray)
- **Tertiary Text**: `#64748b` (Light Gray)
- **Subtle Text**: `#94a3b8` (Very Light Gray)

#### Background & Surfaces
- **White**: `#ffffff`
- **Off-White**: `#f7fafc`
- **Light Gray**: `#f1f5f9`
- **Border Gray**: `#e2e8f0`
- **Divider**: `#cbd5e1`

#### Semantic Colors
- **Success Green**: `#10b981` (Positive evidence, success states)
- **Warning Orange**: `#f59e0b` (Mixed evidence, warnings)
- **Error Red**: `#ef4444` (Negative evidence, errors)
- **Info Blue**: `#3b82f6` (Informational states)

### Background Gradient
- **Main App Background**: `linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe)`
- **Background Size**: `400% 400%`
- **Background Position**: `0% 50%`

---

## 🔤 Typography

### Font Family
**Primary Font**: Inter
- **Weights Available**: 300, 400, 500, 600, 700, 800, 900
- **Import**: `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');`
- **Fallback**: `-apple-system, BlinkMacSystemFont, sans-serif`

### Font Sizes & Usage

#### Headings
- **H1 (Hero)**: 2.5rem (40px) - Font Weight: 900
- **H2 (Section)**: 2rem (32px) - Font Weight: 800
- **H3 (Subsection)**: 1.75rem (28px) - Font Weight: 800
- **H4 (Card Title)**: 1.4rem (22px) - Font Weight: 800
- **H5 (Small Heading)**: 1.2rem (19px) - Font Weight: 700

#### Body Text
- **Large Body**: 1.125rem (18px) - Font Weight: 500
- **Body**: 1rem (16px) - Font Weight: 500
- **Small Body**: 0.95rem (15px) - Font Weight: 500
- **Caption**: 0.875rem (14px) - Font Weight: 500
- **Tiny**: 0.75rem (12px) - Font Weight: 600

#### UI Elements
- **Button Text**: 15-16px - Font Weight: 700
- **Tab Text**: 16px - Font Weight: 700
- **Label Text**: 14px - Font Weight: 600
- **Input Text**: 15px - Font Weight: 500

---

## 🎭 Logo & Icons

### Logo Elements
**Bear Icon** (SVG):
- White bear face with simple geometric shapes
- Two circular ears (r=18)
- Two eyes (circles, r=18)
- Main face (circle, r=35)
- Chin area (ellipse)
- **Colors**: White (`#ffffff`) on gradient background

### Emoji Icons Usage
- **Dashboard**: 📊
- **Daily Log**: 📝
- **Evidence Explorer**: 🔬
- **Settings**: ⚙️
- **Login**: 🔐
- **Therapy**: 🧘🏻‍♀️
- **Pain**: 😣
- **Sleep**: 😴
- **Mood**: 😊
- **Success**: ✅
- **Alert**: ⚠️
- **Bear**: 🐻

---

## 🎨 UI Component Styles

### Buttons

#### Primary Button (Purple/Blue)
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
border-radius: 12px;
padding: 12px 24px;
font-weight: 700;
color: white;
border: none;
box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
transition: all 0.3s ease;
```
**Hover**: Slightly darker gradient, translateY(-2px)

#### Secondary Button (Pink Accent)
```css
background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
border-radius: 12px;
padding: 12px 24px;
font-weight: 700;
color: white;
border: none;
box-shadow: 0 4px 12px rgba(236, 72, 153, 0.3);
```

#### Tertiary Button (Outlined)
```css
background: white;
border: 2px solid #667eea;
border-radius: 12px;
padding: 12px 24px;
font-weight: 600;
color: #667eea;
```

### Cards (Glass Effect)

```css
background: rgba(255, 255, 255, 0.95);
backdrop-filter: blur(20px);
border-radius: 25px;
padding: 30px;
box-shadow: 0 20px 60px rgba(0,0,0,0.15);
border: 1px solid rgba(255, 255, 255, 0.8);
```

### Tabs

#### Active Tab
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
border-radius: 8px;
padding: 15px 30px;
font-weight: 700;
box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
```

#### Inactive Tab
```css
background: transparent;
color: #334155;
border-radius: 8px;
padding: 15px 30px;
font-weight: 600;
```

### Input Fields

```css
border-radius: 12px;
border: 2px solid #e2e8f0;
padding: 16px 18px;
font-size: 15px;
font-weight: 500;
background: white;
transition: all 0.3s ease;
```
**Focus**: Border color changes to `#667eea`, adds shadow

### Multiselect Pills

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
border-radius: 8px;
padding: 6px 12px;
font-weight: 600;
font-size: 14px;
box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
```

---

## 📐 Spacing & Layout

### Spacing Scale
- **xs**: 0.25rem (4px)
- **sm**: 0.5rem (8px)
- **md**: 1rem (16px)
- **lg**: 1.5rem (24px)
- **xl**: 2rem (32px)
- **2xl**: 3rem (48px)
- **3xl**: 4rem (64px)

### Border Radius
- **Small**: 8px (pills, tags)
- **Medium**: 12px (buttons, inputs)
- **Large**: 20-25px (cards)
- **Circle**: 50% (avatars, icon containers)

### Shadows
- **Subtle**: `0 2px 8px rgba(0, 0, 0, 0.08)`
- **Medium**: `0 4px 12px rgba(102, 126, 234, 0.2)`
- **Strong**: `0 20px 60px rgba(0,0,0,0.15)`
- **Button**: `0 4px 12px rgba(102, 126, 234, 0.3)`
- **Button Hover**: `0 6px 20px rgba(102, 126, 234, 0.4)`

---

## 🎯 Key UI Patterns

### Hero Section
- **Background**: Purple gradient
- **Padding**: 40px
- **Border Radius**: 30px
- **Text**: White, center-aligned
- **Shadow**: `0 30px 80px rgba(102, 126, 234, 0.4)`

### Section Headers
- **Background**: Purple gradient
- **Padding**: 1rem 1.5rem
- **Border Radius**: 12px
- **Text**: White, 1.4rem, Font Weight: 700
- **Icon**: Emoji, 3rem size

### Quick Action Cards
- **Icon Container**: 80px circle with 10% opacity background
- **Icon Size**: 3rem emoji
- **Button**: Full width, pink gradient
- **Spacing**: Centered with 1rem bottom margin

### Evidence Cards
- **Background**: White glass effect
- **Border**: Gradient left border (6px)
- **Padding**: 2rem
- **Border Radius**: 24px
- **Shadow**: `0 20px 60px rgba(0,0,0,0.12)`

---

## 🎨 Demo Mode Badge

```css
background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%);
color: white;
padding: 0.25rem 0.75rem;
border-radius: 20px;
font-size: 0.75rem;
font-weight: 700;
box-shadow: 0 2px 8px rgba(236, 72, 153, 0.3);
```

---

## 📱 Responsive Breakpoints

- **Desktop**: 1400px+ (Default styling)
- **Tablet**: 768px - 1399px
- **Mobile**: < 768px
- **Small Mobile**: < 480px

### Mobile Adjustments
- Reduce padding: 1rem instead of 3rem
- Smaller font sizes: -2px to -4px
- Stack columns vertically
- Increase touch targets to 44px minimum
- Simplify gradients for performance

---

## 🎬 Animation & Transitions

### Standard Transition
```css
transition: all 0.3s ease;
```

### Button Hover
```css
transform: translateY(-2px);
transition: all 0.3s ease;
```

### Card Hover
```css
transform: translateY(-8px) scale(1.01);
transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
```

---

## 🖼️ Data Visualization

### Chart Colors
- **Pain Line**: `#ec4899` (Pink)
- **Sleep Line**: `#3b82f6` (Blue)
- **Mood Line**: `#10b981` (Green)
- **Therapy Marker**: Purple gradient

### Evidence Indicators
- **Positive**: Green `#10b981` with ✅
- **Mixed**: Orange `#f59e0b` with ~
- **Negative**: Red `#ef4444` with ❌

---

## 📄 Content Guidelines

### Tone of Voice
- **Friendly but professional**: Approachable yet authoritative
- **Clear and concise**: No medical jargon
- **Empowering**: Focus on user control and insights
- **Evidence-based**: Always reference data sources

### Writing Style
- Use active voice
- Short paragraphs (2-3 sentences max)
- Bullet points for lists
- Numbers for statistics
- Emojis for visual hierarchy (sparingly)

### Call-to-Action Text
- "START FREE DEMO" (not "Get Started")
- "SIGN IN" (not "Log In")
- "CREATE FREE ACCOUNT" (not "Sign Up")
- "SAVE ENTRY" (not "Submit")

---

## 🎯 Brand Applications

### Marketing Materials
- **Primary Color**: Purple gradient
- **Accent Color**: Pink gradient
- **Background**: White or light gradient
- **Text**: Dark gray `#1a202c`

### Social Media
- **Profile Colors**: Purple gradient background
- **Post Style**: Clean, minimal, data-focused
- **Hashtags**: #EvidenceBasedHealth #PersonalHealthScience

### Documentation
- **Code Blocks**: Dark theme with purple accents
- **Headers**: Purple gradient
- **Links**: Blue `#3b82f6`

---

## 🚀 Export Formats

### Color Formats
- **Hex**: For web/design tools
- **RGB**: For print materials
- **RGBA**: For transparency effects

### Logo Formats
- **SVG**: For scalable web use (preferred)
- **PNG**: For social media (1200x630 for OG images)
- **Favicon**: 32x32, 180x180 (PNG)

---

## 📋 Brand Checklist

For any new design, ensure:
- [ ] Uses Inter font family
- [ ] Purple/blue gradient as primary color
- [ ] Pink accent for interactive elements
- [ ] Rounded corners (12-25px)
- [ ] Consistent shadows
- [ ] Proper color contrast (WCAG AA)
- [ ] Mobile responsive
- [ ] Smooth transitions
- [ ] Clear hierarchy
- [ ] On-brand emojis

---

**Version**: 1.0  
**Last Updated**: January 26, 2025  
**Maintained By**: Bearable Design Team

---

## 🎨 Quick Reference Card

```
PRIMARY GRADIENT: #667eea → #764ba2
ACCENT GRADIENT:  #ec4899 → #f472b6
FONT: Inter (Google Fonts)
BORDER RADIUS: 12px (buttons), 25px (cards)
SHADOW: 0 4px 12px rgba(102, 126, 234, 0.3)
SPACING: 1rem base unit
```

**Use this guide to maintain consistent branding across all Bearable materials! 🐻**


