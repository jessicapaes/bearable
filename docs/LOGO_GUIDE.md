# 🎨 Bearable Logo & Branding Guide

## Logo Variations

### Full Logos (Icon + Text)

1. **`bearable_logo_purple.svg`** - Purple logo for light backgrounds
   - Bear icon: #667eea
   - Text: #7c3aed
   - Use on: White/Light backgrounds

2. **`bearable_logo_white.svg`** - White logo for dark backgrounds
   - Bear icon: #ffffff
   - Text: #ffffff
   - Use on: Purple/Dark backgrounds

3. **`bearable_logo_gradient.svg`** - Gradient logo (modern)
   - Bear icon: Gradient (#667eea → #764ba2)
   - Text: Same gradient
   - Use on: Any background for premium feel

### Icon Only (No Text)

4. **`bear_icon_purple.svg`** - Purple bear icon only
   - Color: #667eea
   - Muzzle: #a5b4fc
   - Use for: Favicons, app icons, social media

5. **`bear_icon_white.svg`** - White bear icon only
   - Color: #ffffff
   - Muzzle: #f3f4f6
   - Use for: Dark backgrounds, watermarks

6. **`bear_icon_gradient.svg`** - Gradient bear icon only
   - Gradient: #667eea → #764ba2
   - Use for: Modern applications, premium branding

## Brand Colors

### Primary Purple
- **Light Purple**: `#667eea` (RGB: 102, 126, 234)
- **Dark Purple**: `#764ba2` (RGB: 118, 75, 162)
- **Gradient**: Use both for modern gradient effects

### Secondary Pink
- **Pink**: `#ec4899` (RGB: 236, 72, 153)
- **Light Pink**: `#f472b6` (RGB: 244, 114, 182)

### Accent Colors
- **Light Purple Accent**: `#a5b4fc` (RGB: 165, 180, 252)
- **Light Gray**: `#f3f4f6` (RGB: 243, 244, 246)

## Usage Guidelines

### When to Use Each Logo

**Purple Logo** (`bearable_logo_purple.svg`)
- ✅ White or light backgrounds
- ✅ Light mode interfaces
- ✅ Printed materials
- ✅ Social media avatars

 Leads

**White Logo** (`bearable_logo_white.svg`)
- ✅ Purple gradient backgrounds
- ✅ Dark mode interfaces
- ✅ Overlays on images
- ✅ Footer sections with colored backgrounds

**Gradient Logo** (`bearable_logo_gradient.svg`)
- ✅ Premium features
- ✅ Marketing materials
- ✅ Landing pages
- ✅ App headers

**Icon Only**
- ✅ Favicon (`bear_icon_gradient.svg` 32x32 or 64x64)
- ✅ App icons (all sizes)
- ✅ Social media profile pictures
- ✅ Watermarks
- ✅ Small spaces where full logo won't fit

## Technical Specifications

### SVG Advantages
- ✅ **Transparent backgrounds** - Work on any color
- ✅ **Scalable** - Perfect at any size
- ✅ **Lightweight** - Small file sizes
- ✅ **Crisp** - Vector graphics always sharp

### Dimensions
- **Full Logo**: 200x80px (169x80mm at 300dpi)
- **Icon Only**: 100x100px (84.7x84.7mm at 300dpi)
- **Minimum Size**: 
  - Full logo: 160x64px
  - Icon: 40x40px

### Clear Space
- Maintain **minimum 20px** clear space around logos
- For icons: **minimum 10px** clear space

## File Locations

All logos are in the `app/` directory:
```
app/
├── bearable_logo_purple.svg        # Purple full logo
├── bearable_logo_white.svg         # White full logo
├── bearable_logo_gradient.svg      # Gradient full logo
├── bear_icon_purple.svg            # Purple icon only
├── bear_icon_white.svg             # White icon only
├── bear_icon_gradient.svg          # Gradient icon only
└── bear_icon.svg                   # Original (white bear)
```

## Usage Examples

### Website Header
```html
<img src="bearable_logo_gradient.svg" alt="Bearable" width="150">
```

### Dark Background
```html
<img src="bearable_logo_white.svg" alt="Bearable" width="150">
```

### Favicon
```html
<link rel="icon" type="image/svg+xml" href="bear_icon_gradient.svg">
```

### Social Media Profile
Use `bear_icon_gradient.svg` at 512x512px

## License

All logos are part of the Bearable project and follow the same MIT License as the codebase.

*Last Updated: October 27, 2025*

