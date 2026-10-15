---
name: arabic-rtl-review
description: Verify and audit Arabic Right-to-Left (RTL) interface direction, mixed Arabic/English bidirectional (BiDi) text rendering, punctuation flow, responsive layout at 360px viewport width, accessibility (WCAG AA), and mobile usability for the Opportunities Portal.
---

# Arabic RTL & Mobile Usability Review Skill

Use this skill when auditing, testing, or reviewing the Opportunities Portal interface for Arabic RTL rendering, bidirectional text handling, mobile responsiveness at 360px width, and accessibility.

---

## 1. Core Audit Dimensions

### A. RTL Direction & Layout Alignment
- **Root Direction**: Verify `dir="rtl"` and `lang="ar"` on the root `<html>` tag.
- **CSS Logical Properties**: Ensure layout and spacing use logical properties instead of physical left/right:
  - `margin-inline-start` / `margin-inline-end` (not `margin-left` / `margin-right`)
  - `padding-inline-start` / `padding-inline-end` (not `padding-left` / `padding-right`)
  - `text-align: start` (defaults to right in RTL, prevents text from clinging left)
  - `inset-inline-start` / `inset-inline-end` for absolute positioning.
- **Icon Orientation**: Directional icons (arrows, chevrons, pagination) must point left for forward progression. Symmetric icons (search magnifying glass, favorite heart, calendar) should not be flipped.
- **Flexbox & Grid**: Flex directions naturally flow from right to left under RTL. Confirm ordering of badges, buttons, and card headers matches Arabic reading order.

### B. Mixed Arabic / English (BiDi) Text & Punctuation
- **Proper Isolation**: Mixed text containing English proper names, university names, or technical terms (e.g., DAAD, Chevening, Google, Full-Stack, Python, IELTS) must not disrupt Arabic phrase order.
- **Inline Isolation Tags**: Wrap English brand names, acronyms, and codes in `<bdi>` or `<span dir="ltr">`:
  ```html
  <span>منحة <bdi>DAAD</bdi> للدراسات العليا</span>
  ```
- **Punctuation Attachment**: Ensure trailing punctuation (periods, colons, exclamation marks, closing parentheses) attaches to the logical end of the Arabic sentence and does not jump to the right/left boundary inappropriately.
- **Numeric & Date Displays**: Verify dates (e.g., `2026-11-01` or localized Arabic dates) and numbers render consistently without digit reordering.

### C. Responsive Layout at 360px Width
- **Zero Horizontal Overflow**: Inspect the page at `360px` viewport width (standard budget smartphone screen). Confirm that:
  - `document.documentElement.scrollWidth <= 360`
  - No horizontal scrollbars appear on the viewport or individual cards.
- **Fluid Grid & Card Layout**: Cards and filter chips must wrap cleanly without text truncation or clipping.
- **Touch Target Sizes**: All interactive controls (buttons, favorite toggles, modal close buttons, filter chips) must have a minimum clickable area of **44×44px**.
- **Arabic Typography Scale**: Arabic script requires sufficient vertical clearance for accents and ligatures. Ensure:
  - Minimum body font size: `15px` to `16px` (`0.95rem` to `1rem`).
  - Line height (`line-height`): between `1.6` and `1.8` to prevent diacritic clipping.

### D. Accessibility (WCAG 2.1 AA)
- **Contrast Ratios**: Normal text must achieve a minimum contrast ratio of `4.5:1` against background colors.
- **Urgency Badge Verification**: Check color-coding and contrast for all three Arabic deadline status badges:
  - `"متاحة"` (Active) — High contrast green theme.
  - `"تغلق قريبًا"` (Closing soon, < 14 days) — High contrast amber/orange theme.
  - `"منتهية"` (Expired) — High contrast muted gray theme.
- **ARIA & Screen Readers**:
  - Icon-only buttons (such as bookmark toggles and close buttons) must include descriptive Arabic `aria-label` attributes (e.g., `aria-label="إضافة إلى المفضلة"` or `aria-label="إغلاق النافذة"`).
  - Search input must have an accessible label or `aria-label="البحث عن الفرص"`.
- **Keyboard Navigation**: Clear `:focus-visible` styling with high contrast focus rings.

### E. Low-Bandwidth & Mobile Usability
- **Self-Contained Styling**: Confirm zero CDN dependencies (`cdnjs`, `google fonts`, etc.). All font definitions and icons must use local SVG or system fonts.
- **Touch Ergonomics**: Key actions (search, filter, card clicking) must be easy to trigger with one hand on mobile screens.

---

## 2. Review Procedure & Commands

When conducting an audit, follow this step-by-step checklist:

1. **Static Markup Audit**:
   - Inspect `index.html` (or template) for `dir="rtl"` and `lang="ar"`.
   - Scan CSS rules for physical properties (`float: left`, `margin-left`, `padding-right`) and verify conversion to logical properties.
2. **Text & BiDi Audit**:
   - Verify that listings with mixed English/Arabic strings use `<bdi>` or proper span isolation.
   - Inspect status tags to verify exact spelling: `"متاحة"`, `"تغلق قريبًا"`, `"منتهية"`.
3. **Viewport Stress Test (360px)**:
   - Test layout at 360px width.
   - Ensure card padding is balanced (`padding: 12px` to `16px`).
   - Check modal/dialog behavior on mobile to verify it does not exceed screen dimensions.
4. **Summary & Audit Output**:
   - Document any visual defects, overflow issues, or contrast failures.
   - Report pass/fail status across the 5 dimensions.
