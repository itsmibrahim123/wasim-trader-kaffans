# Sales, Outreach & Go-To-Market Strategy

## 1. Consolidated Project Architecture

All cold outreach, scraping, and landing page assets are now consolidated in this unified project workspace:
- `masjid_scrapper.py`: Automated discovery of Mosques, Islamic Centers, and Funeral Directors across USA, Australia, and New Zealand from Google Maps.
- `masjid_data.csv`: Curated database of 493 unique, validated Mosque email addresses across USA (400+), Australia (70+), and New Zealand (23+).
- `send_emails.py`: Modernized, rate-limited email engine with `--dry-run`, `--test <email>`, `--country`, `--limit`, and HTML preview generation.
- `index.html`: The central landing destination (`wasim-trader-kaffans.vercel.app`) linked in every email, providing institutional credibility, full sizing specs, photos, customer reviews, and immediate action buttons.
- `.env.example`: Template for secure SMTP and WhatsApp contact configuration.
- `email_log.csv`: Automatic tracking log to ensure no masjid is ever emailed twice across re-runs.

---

## 2. Target Customer Personas

### Persona A: The Mosque Imam / Janazah Committee Chair
- **Demographics**: Religious scholars, volunteer committee leaders, elderly trustees (ages 40–70).
- **Pain Points**:
  - Unpredictable Janazah requests requiring emergency fabric runs to local textile markets.
  - Inconsistent fabric quality (sheer, rough, or polyester blends).
  - High costs charged by commercial non-Muslim funeral homes ($100–$250+ per shroud).
  - Lack of storage space for massive raw fabric bolts.
- **Value Proposition**:
  - "Keep 10–25 pre-cut, sealed Sunnah-compliant sets in your masjid closet at $25 flat rate."
  - "Never scramble during an emergency Janazah."
  - "Support your masjid's community welfare fund through volume discounts or referral rebate."

### Persona B: The Grieving Family Member
- **Demographics**: Adult children, siblings, or spouses arranging burial for a recently deceased relative.
- **Pain Points**:
  - Overwhelmed by grief and time pressure (burial is sought within 24 hours).
  - Unsure what constitutes a valid Islamic kaffan or where to buy one.
  - Needs reassurance that the garments are 100% Sunnah-compliant and properly sized.
- **Value Proposition**:
  - "Complete pre-cut set with all 3 pieces (for men) or 5 pieces (for women) ready out of the box."
  - "Priced fairly at $25 without exploiting grief."
  - "Instant guidance and fast local dispatch."

### Persona C: The Community Donor / Sadaqah Jariyah Giver
- **Demographics**: Muslims seeking continuous ongoing charity (*Sadaqah Jariyah*).
- **Pain Points**:
  - Wants a tangible, highly beneficial deed that serves the community directly.
- **Value Proposition**:
  - "Donate 20 or 50 Kaffans to your local masjid to be used for indigent or underprivileged deceased."

---

## 3. Inbound Conversion Funnel on the Landing Page

```
[ Cold Outreach Email / Google Search / Word of Mouth ]
                          │
                          ▼
        [ Landing Page Hero & Bismillah ]
  (Builds instant religious trust & solemn dignity)
                          │
                          ▼
    [ Product Showcase + Real Visuals & Diagrams ]
 (High-res images KaffanImage, Kaffan3piece, TiedKaffan)
                          │
                          ▼
   [ Sizing & Fiqh Breakdown (Tabs & Measurements) ]
 (Transparent details, S/M/L/XL specs, 3-pc vs 5-pc)
                          │
                          ▼
     [ Interactive Live Cost & Quantity Calculator ]
 (User selects Men/Women/Bulk, Currency & Destination)
                          │
                          ▼
          [ Action / Inquiry Conversion ]
     ┌────────────────────┴────────────────────┐
     ▼                                         ▼
[ 1-Click WhatsApp Order ]              [ Direct Form / Email ]
(Pre-filled cart & delivery details)    (Opens mailto: or submission)
```

---

## 4. Key Metrics & Follow-Up Protocol

- **Target Response Time**: < 15 minutes for WhatsApp emergency inquiries; < 4 hours for email enquiries.
- **Tracking**: Log each incoming lead against `email_log.csv` and record whether it resulted in a sample request, single family order, or institutional mosque partnership.
- **Primary Channels**:
  - **Email**: `iwasimtrader@gmail.com`
  - **Website**: `https://wasim-trader-kaffans.vercel.app/`
  - **WhatsApp**: Click-to-chat integration with pre-filled order text.
