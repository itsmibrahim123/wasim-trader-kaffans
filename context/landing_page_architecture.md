# Landing Page Architecture & Frontend Design System (B2B Optimized)

## 1. Information Architecture & Section Hierarchy

The landing page (`index.html`) is architected specifically for high-conversion B2B and institutional cold outreach (targeting Mosque Imams, Shura Boards, Funeral Committees, and Distributors across the USA, Australia, and New Zealand):

```
┌────────────────────────────────────────────────────────┐
│ 1. Sticky Navigation Bar                                │
│    - Brand Logo ("Wasim Trader Kaffans")                │
│    - Navigation Links (Offerings, Fabric, Sizing,       │
│      Packaging, Sunnah Guide, Masjid Hub, Samples, FAQ) │
│    - Currency Selector (USD $, AUD A$, NZD NZ$, GBP £)  │
│    - Primary Action ("Request Sample Kit")              │
├────────────────────────────────────────────────────────┤
│ 2. Hero Section (Overhauled B2B Conversion Engine)     │
│    - Left Column:                                      │
│      • Bismillah & Islamic Framing                     │
│      • Headline: "Reliable, Sunnah-Compliant Kaffan     │
│        Supplies for Masjids & Funeral Committees"       │
│      • Subheadline: Pre-cut, 100% white cotton burial   │
│        garments crafted for community readiness...     │
│      • 3 Trust Pills:                                   │
│        1. "100% Pure White Cotton"                      │
│        2. "Sunnah-Compliant Pre-Cut Dimensions"         │
│        3. "Ready-to-Use Protective Packaging"           │
│      • Primary CTA: "Request a Free Masjid Sample Kit"  │
│      • Secondary CTA: "View Wholesale Pricing & Sizing" │
│    - Right Column:                                     │
│      • Prominent Product Showcase (`KaffanImage.jpeg`)  │
│      • Floating Badge: "$25 Flat Individual / Wholesale │
│        Cartons Available"                              │
├────────────────────────────────────────────────────────┤
│ 3. Sacred Trust Badges Strip                           │
│    - 100% Sunnah Compliant (3-pc Men / 5-pc Women)     │
│    - Pre-Cut & Ready (Zero Cutting Hassle in Grief)     │
│    - 100% Pure White Cotton (Opaque & Breathable)      │
│    - Direct Dispatch to USA, Australia & New Zealand   │
├────────────────────────────────────────────────────────┤
│ 4. Product Offerings & Tiered Wholesale Cards          │
│    - Men's Set ($25): `Kaffan3piece.jpeg`              │
│      • 3 pieces + pre-cut tie ribbons                  │
│    - Women's Set ($25): `TiedKaffan.jpeg`              │
│      • 5 pieces + pre-cut tie ribbons                  │
│    - Masjid Bulk Cartons ("Wholesale Tiered Rates"):   │
│      • Photo: `Unstitched.jpeg`                        │
│      • Tiers: 20 sets ($22/ea), 50 sets ($20/ea),      │
│        100 sets ($18/ea)                               │
│      • Copy: "Shipping calculated based on destination  │
│        and carton volume."                             │
├────────────────────────────────────────────────────────┤
│ 5. Fabric & Quality Showcase (Texture & Opacity)       │
│    - Visuals: `macroTexture.jpeg` & `Unstitched.jpeg`   │
│    - Close-ups of weave density, non-transparency,     │
│      and pre-cut neat hems                             │
├────────────────────────────────────────────────────────┤
│ 6. Packaging & Dignity Section (Cleanliness & Ties)    │
│    - Visuals: `KaffanImage.jpeg` & `TiedKaffan.jpeg`   │
│    - Dust-proof sealed packaging ready for storage     │
│    - Pre-cut tie ribbons (Ribat) included              │
├────────────────────────────────────────────────────────┤
│ 7. Audited Sizing Matrix & Anatomy Breakdown           │
│    - Men's Sizing Table (S: 100", M: 108", L: 116",    │
│      XL: 126" — logically scaling)                     │
│    - Women's Sizing Table (Universal Generous Fit)     │
│    - Visual diagrams: `KaffansMan.png` &               │
│      `KaffanLadies.png` beside tables                  │
│    - Units Toggle: Inches (in) / Centimeters (cm)      │
├────────────────────────────────────────────────────────┤
│ 8. The Sunnah of Takfeen (4-Step Theological Guide)   │
│    - Step 1: Preparation & Perfuming (Ithr / Camphor)  │
│    - Step 2: Laying Out the Layers                     │
│    - Step 3: Sequential Wrapping & Awrah Modesty       │
│    - Step 4: Fastening with Cotton Tie Ribbons         │
├────────────────────────────────────────────────────────┤
│ 9. Institutional Masjid Partnership Hub                │
│    - Consignment & on-site reserve storage models      │
│    - Community fund rebate/commission program          │
│    - Emergency hotline for funeral directors           │
├────────────────────────────────────────────────────────┤
│ 10. Live Quantity & Cost Estimator                     │
│     - Interactive selector with carton pricing logic   │
│     - Destination country dropdown                     │
│     - 1-click WhatsApp & Email dispatch                │
├────────────────────────────────────────────────────────┤
│ 11. Institutional Sample Request Form (`#sample-request`)│
│     - Fields: Masjid Name, Contact & Role, Email,      │
│       Phone/WhatsApp, Shipping City/State/Country      │
│     - Dropdown: [1 Free Sample Kit, Bulk Carton Quote, │
│       Distributor Partnership]                         │
│     - Button: "Request Sample Kit"                     │
├────────────────────────────────────────────────────────┤
│ 12. Testimonials, FAQ Accordion & Footer               │
│     - Institutional endorsements (Auckland, LA, Melb)  │
│     - Semantic `<details>` FAQ accordion               │
│     - Direct WhatsApp (`wa.me/?text=...`) & Email bar  │
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
