# Landing Page Architecture & Frontend Design System (Minimal & High-Contrast)

## 1. Information Architecture & Section Hierarchy

The landing page (`index.html`) is architected with a slick, minimal, and high-contrast aesthetic. It strictly adheres to the core image placement rule: **all product photography is confined exclusively to the `#offerings` Kaffans section**. Zero images appear in the Hero, Sizing Tables, Testimonials, or Footer.

```
┌────────────────────────────────────────────────────────┐
│ 1. Sticky Navigation Bar (Solid / High-Blur Backdrop)  │
│    - Brand Logo ("Wasim Trader Kaffans")                │
│    - Navigation Links (Kaffan Sets, Sizing, Sunnah,     │
│      Testimonials, Order / Sample, FAQ)                │
│    - Currency Selector (USD $, AUD A$, NZD NZ$, GBP £)  │
│    - Action Button ("Order Kaffan Set")                 │
├────────────────────────────────────────────────────────┤
│ 2. Hero Section (Minimalist, Centered, High-Contrast)  │
│    - Deep charcoal headline (#111827) on warm cream    │
│    - Subheadline: $25/set including delivery (min 100) │
│    - 3 Trust Pills with clean CSS emerald dots:         │
│      • 100% Pure White Cotton                          │
│      • Sunnah-Compliant Pre-Cut Dimensions             │
│      • $25 / Set (Delivery Included · Min. 100 pcs)    │
│    - Dual CTAs: "Order Kaffan Sets" & "View Sizing"    │
│    - WhatsApp rush courier link                        │
│    - ZERO IMAGES in Hero                               │
├────────────────────────────────────────────────────────┤
│ 3. Sacred Trust Badges Strip                           │
│    - 100% Sunnah Compliant (3-pc Men / 5-pc Women)     │
│    - Pre-Cut & Ready (Zero Cutting Hassle in Grief)     │
│    - 100% Pure White Cotton (Opaque & Breathable)      │
│    - Rapid Dispatch to USA, Australia & New Zealand    │
├────────────────────────────────────────────────────────┤
│ 4. Kaffan Sets / Offerings (THE ONLY IMAGE SECTION)     │
│    - Centered 2-Card Balanced Grid (max-width: 920px)  │
│    - Men's Set Card ($25 /set · Delivery Included):    │
│      • Photo wrap: aspect-ratio 1:1, object-fit: contain│
│      • Photo: `Kaffan3piece.jpeg`                      │
│      • Min order: 100 pcs (extra rush courier fees)    │
│      • 3 pieces + pre-cut tie ribbons                  │
│    - Women's Set Card ($25 /set · Delivery Included):  │
│      • Photo wrap: aspect-ratio 1:1, object-fit: contain│
│      • Photo: `TiedKaffan.jpeg`                        │
│      • Min order: 100 pcs (extra rush courier fees)    │
│      • 5 pieces + pre-cut tie ribbons                  │
│    - Identical card heights & aligned action buttons   │
├────────────────────────────────────────────────────────┤
│ 5. Audited Sizing Matrix                               │
│    - Men's Sizing Table (S: 100", M: 108", L: 116",    │
│      XL: 126" — logically scaling)                     │
│    - Women's Sizing Table (Universal Generous Fit)     │
│    - Ample cell padding (1.1rem 1.4rem)                │
│    - Units Toggle: Inches (in) / Centimeters (cm)      │
│    - ZERO IMAGES in Sizing                             │
├────────────────────────────────────────────────────────┤
│ 6. The Sunnah of Takfeen (4-Step Theological Guide)   │
│    - Step 1: Preparation & Perfuming (Ithr / Camphor)  │
│    - Step 2: Laying Out the Layers                     │
│    - Step 3: Sequential Wrapping & Awrah Modesty       │
│    - Step 4: Fastening with Cotton Tie Ribbons         │
├────────────────────────────────────────────────────────┤
│ 7. Testimonials (High-Contrast Quotes & Communities)   │
│    - High-contrast charcoal community names (#111827)  │
│    - Authentic endorsements (Auckland, LA, Melbourne)  │
├────────────────────────────────────────────────────────┤
│ 8. Order & Sample Request Form (`#sample-request`)     │
│    - Fields: Full Name / Organization, Email,          │
│      WhatsApp Number, Order Type / Needs               │
│    - Direct WhatsApp dispatch (`wa.me/?text=...`)      │
│    - Direct email link: `iwasimtrader@gmail.com`       │
├────────────────────────────────────────────────────────┤
│ 9. Semantic FAQ Accordion & Minimalist Footer          │
│    - Native `<details>` expandable items               │
│    - Clean high-contrast footer with direct links      │
└────────────────────────────────────────────────────────┘
```

---

## 2. Design Tokens & Styling System

```css
:root {
  --cream:        #f8f4ec;
  --cream-light:  #fdfbf7;
  --parchment:    #eee5d3;
  --parchment-2:  #e2d6be;
  --white:        #ffffff;
  
  --gold:         #b8973a;
  --gold-light:   #d8ba69;
  --gold-dark:    #917322;
  --gold-glow:    rgba(184, 151, 58, 0.16);
  
  --emerald:      #193828;
  --emerald-dark: #0f2419;
  --emerald-soft: rgba(25, 56, 40, 0.08);

  --dark:         #18140e;
  --dark-card:    #221d15;
  --text:         #2a241b;
  --text-soft:    #40372b;
  --muted:        #6b5e4c;
  --muted-light:  #948674;

  --border-gold:   rgba(184, 151, 58, 0.28);
  --border-subtle: rgba(42, 36, 27, 0.1);
  
  --shadow-sm:    0 4px 16px rgba(24, 20, 14, 0.06);
  --shadow-md:    0 12px 36px rgba(24, 20, 14, 0.09);
  --shadow-lg:    0 24px 64px rgba(24, 20, 14, 0.14);

  --font-serif:   'Cormorant Garamond', Georgia, serif;
  --font-arabic:  'Amiri', serif;
  --font-sans:    'Tajawal', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --transition:   all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}
```
