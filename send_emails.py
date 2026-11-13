#!/usr/bin/env python3
"""
Wasim Trader Kaffans — Masjid Cold Email Engine
================================================
Sends a captivating, modern, and respectful HTML cold email to masjids
from masjid_data.csv featuring the newly redesigned website and pricing structure.

Features:
- Beautiful high-contrast responsive HTML email template + plain-text fallback
- Safe rate limiting with randomized jitter delays (protects Gmail reputation)
- Resume & deduplication via email_log.csv (never sends twice to the same email)
- CLI controls:
    --dry-run             Generate email_preview.html and print recipient counts without sending
    --test <email>        Send a single test email to your personal address
    --country <name>      Filter recipients by country (e.g. 'New Zealand', 'Australia', 'USA')
    --limit <N>           Cap sends to N emails for the current session (recommended: 30-50/day)
    --delay <min>,<max>   Random delay range between sends in seconds (default: 20,40)

Setup:
1. Copy .env.example to .env
2. Add your GMAIL_ADDRESS and 16-character GMAIL_APP_PASSWORD
3. Test locally: python send_emails.py --dry-run
"""

import argparse
import csv
import logging
import os
import random
import re
import smtplib
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass


# ──────────────────────────────────────────────
# CONFIGURATION & DEFAULTS
# ──────────────────────────────────────────────
GMAIL_ADDRESS = (os.getenv("GMAIL_ADDRESS") or "iwasimtrader@gmail.com").strip()
# Automatically clean spaces from Google App Passwords (e.g., "abcd efgh ijkl mnop" -> "abcdefghijklmnop")
GMAIL_APP_PASSWORD = (os.getenv("GMAIL_APP_PASSWORD") or "").strip().replace(" ", "")
WEBSITE_URL = (os.getenv("WEBSITE_URL") or "https://wasim-trader-kaffans.vercel.app/").rstrip("/")
WHATSAPP_NUMBER = (os.getenv("WHATSAPP_NUMBER") or "03000418358").strip()

CSV_FILE = "masjid_data.csv"
LOG_FILE = "email_log.csv"
PREVIEW_FILE = "email_preview.html"

# Default subject line (respectful, community-focused, high open rate)
DEFAULT_SUBJECT = "Sunnah Kaffan Sets for {masjid_name} — $25 (Delivery Included · Min 100 Pcs)"

# Explicit Exclusions / Blacklist (User-Requested)
EXCLUDED_EMAILS = {
    "icreseda1@aol.com",
    "secretary@masjidannur.com",
    "info@masjidannur.org",
    "media@annurfoundation.org",
    "info@alnurmasjid.org",
}
EXCLUDED_KEYWORDS = ["reseda", "rasaeda", "an nur", "an-nur", "annur", "al nur"]

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("kaffan_emailer")

# ──────────────────────────────────────────────
# EMAIL VALIDITY CHECK
# ──────────────────────────────────────────────
INVALID_VALUES = {
    "", "not found", "no website", "site timeout", "error accessing site",
    "site unreachable", "social media only", "check facebook manually",
    "n/a", "none", "null", "undefined",
}
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def is_valid_email(email: str) -> bool:
    if not email:
        return False
    cleaned = email.strip().lower()
    if cleaned in INVALID_VALUES:
        return False
    return bool(EMAIL_RE.match(cleaned))


# ──────────────────────────────────────────────
# EMAIL TEMPLATE BUILDER
# ──────────────────────────────────────────────
def build_email_content(masjid_name: str, country: str) -> tuple[str, str, str]:
    """
    Returns (subject, html_body, plain_body)
    Generates a cool, modern, editorial, and captivating email designed
    specifically for Muslim community leaders, imams, and funeral committees.
    """
    clean_name = (masjid_name or "").strip() or "your respected masjid"
    if clean_name == "your respected masjid":
        subject = "Sunnah Kaffan Sets — $25 (Delivery Included · Min 100 Pcs)"
    else:
        subject = f"Sunnah Kaffan Sets for {clean_name} — $25 (Delivery Included · Min 100 Pcs)"

    # WhatsApp Link
    wa_text = f"As-salamu alaykum, I am inquiring about Kaffan sets for {clean_name}"
    import urllib.parse
    encoded_wa = urllib.parse.quote(wa_text)
    if WHATSAPP_NUMBER:
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_wa}"
    else:
        wa_url = f"https://wa.me/?text={encoded_wa}"

    footer_mention = clean_name if clean_name != "your respected masjid" else "your masjid"

    # HTML Body
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="color-scheme" content="light dark"/>
<meta name="supported-color-schemes" content="light dark"/>
<title>{subject}</title>
<style>
  /* Reset & Client Normalization */
  body, table, td, p, a, li, blockquote {{
    -webkit-text-size-adjust: 100%;
    -ms-text-size-adjust: 100%;
    margin: 0;
    padding: 0;
  }}
  table, td {{
    mso-table-lspace: 0pt;
    mso-table-rspace: 0pt;
  }}
  img {{
    -ms-interpolation-mode: bicubic;
    border: 0;
    height: auto;
    line-height: 100%;
    outline: none;
    text-decoration: none;
  }}
  body {{
    background-color: #F4F1EA;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1F2937;
    margin: 0;
    padding: 24px 12px;
  }}
  .container {{
    max-width: 600px;
    margin: 0 auto;
    background-color: #FFFFFF;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  }}
  /* Header */
  .header {{
    background-color: #111827;
    padding: 36px 28px 30px;
    text-align: center;
  }}
  .bismillah {{
    font-family: 'Amiri', 'Traditional Arabic', 'Times New Roman', serif;
    font-size: 20px;
    color: #D4AF37;
    margin-bottom: 12px;
    letter-spacing: 1px;
  }}
  .brand-title {{
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 24px;
    color: #FBF9F5;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }}
  .brand-title span {{
    color: #D4AF37;
  }}
  .brand-subtitle {{
    font-size: 11px;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 2px;
  }}
  .gold-divider {{
    height: 3px;
    background: linear-gradient(90deg, #111827 0%, #D4AF37 50%, #111827 100%);
  }}
  /* Body Content */
  .content {{
    padding: 36px 32px 28px;
  }}
  .salutation {{
    font-size: 15px;
    color: #6B7280;
    font-style: italic;
    margin-bottom: 18px;
  }}
  .headline {{
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 20px;
    color: #85500A;
    line-height: 1.4;
    margin-bottom: 16px;
    font-weight: 600;
  }}
  .body-text {{
    font-size: 14.5px;
    line-height: 1.7;
    color: #4A3515;
    margin-bottom: 18px;
  }}
  /* Product Cards Grid */
  .cards-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 12px 0;
    margin: 24px -12px;
  }}
  .card-td {{
    width: 50%;
    vertical-align: top;
    background-color: #FAF8F5;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 20px 16px;
    text-align: center;
  }}
  .card-badge {{
    display: inline-block;
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #85500A;
    background-color: rgba(133, 80, 10, 0.1);
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 10px;
  }}
  .card-name {{
    font-family: Georgia, serif;
    font-size: 16px;
    color: #85500A;
    font-weight: 600;
    margin-bottom: 6px;
  }}
  .card-price {{
    font-size: 26px;
    color: #85500A;
    font-weight: 700;
    font-family: Georgia, serif;
    margin-bottom: 12px;
  }}
  .card-price span {{
    font-size: 12px;
    color: #6B7280;
    font-weight: normal;
  }}
  .card-pieces {{
    font-size: 12px;
    color: #4B5563;
    line-height: 1.5;
    text-align: left;
    border-top: 1px solid #E5E7EB;
    padding-top: 10px;
  }}
  .card-pieces li {{
    margin-bottom: 4px;
    list-style: none;
  }}
  .card-pieces li::before {{
    content: "✓ ";
    color: #059669;
    font-weight: bold;
  }}
  /* Value Pillars */
  .pillars-table {{
    width: 100%;
    margin: 22px 0;
    border-collapse: collapse;
  }}
  .pillar-row td {{
    padding: 8px 0;
    font-size: 13.5px;
    color: #4A3515;
    vertical-align: top;
  }}
  .pillar-bullet {{
    width: 24px;
    color: #D4AF37;
    font-size: 14px;
    font-weight: bold;
  }}
  /* Primary Button */
  .cta-wrap {{
    text-align: center;
    margin: 30px 0 24px;
  }}
  .cta-btn {{
    display: inline-block;
    background-color: #85500A;
    color: #FFFFFF !important;
    text-decoration: none;
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 15px 32px;
    border-radius: 5px;
    box-shadow: 0 3px 10px rgba(133, 80, 10, 0.25);
  }}
  /* Footer */
  .footer {{
    background-color: #111827;
    padding: 28px 24px;
    text-align: center;
    color: #9CA3AF;
  }}
  .footer-links a {{
    color: #D4AF37;
    text-decoration: none;
    font-size: 12px;
    margin: 0 8px;
  }}
  .footer-links a:hover {{
    text-decoration: underline;
  }}
  .footer-text {{
    font-size: 11.5px;
    line-height: 1.6;
    margin-top: 12px;
    color: #6B7280;
  }}
  @media only screen and (max-width: 580px) {{
    .cards-table, .card-td {{
      display: block !important;
      width: 100% !important;
    }}
    .card-td {{
      margin-bottom: 12px !important;
    }}
    .content {{
      padding: 24px 18px !important;
    }}
  }}
  :root {{
    color-scheme: light dark;
    supported-color-schemes: light dark;
  }}
  @media (prefers-color-scheme: dark) {{
    body {{
      background-color: #0B0F17 !important;
      color: #E5D5B8 !important;
    }}
    .container {{
      background-color: #111827 !important;
      border-color: #2D3748 !important;
    }}
    .content {{
      background-color: #111827 !important;
    }}
    .headline {{
      color: #F3C64F !important;
    }}
    .salutation {{
      color: #BFA980 !important;
    }}
    .body-text {{
      color: #E5D5B8 !important;
    }}
    .card-td {{
      background-color: #161B22 !important;
      border-color: #2D3748 !important;
    }}
    .card-badge {{
      color: #F3C64F !important;
      background-color: rgba(243, 198, 79, 0.15) !important;
    }}
    .card-name {{
      color: #F3C64F !important;
    }}
    .card-price {{
      color: #F3C64F !important;
    }}
    .card-pieces {{
      color: #BFA980 !important;
      border-top-color: #2D3748 !important;
    }}
    .pillar-row td {{
      color: #E5D5B8 !important;
    }}
    .cta-btn {{
      background-color: #F3C64F !important;
      color: #0B0F17 !important;
      font-weight: 700 !important;
    }}
    .footer {{
      background-color: #0B0F17 !important;
    }}
    .gold-divider {{
      background: linear-gradient(90deg, #0B0F17 0%, #D4AF37 50%, #0B0F17 100%) !important;
    }}
  }}
  /* Outlook.com & Android app dark mode fallbacks */
  [data-ogsc] body {{ background-color: #0B0F17 !important; }}
  [data-ogsc] .container {{ background-color: #111827 !important; border-color: #2D3748 !important; }}
  [data-ogsc] .card-td {{ background-color: #161B22 !important; border-color: #2D3748 !important; }}
  [data-ogsc] .headline, [data-ogsc] .card-name, [data-ogsc] .card-price {{ color: #F3C64F !important; }}
  [data-ogsc] .card-badge {{ color: #F3C64F !important; background-color: rgba(243, 198, 79, 0.15) !important; }}
  [data-ogsc] .body-text, [data-ogsc] .pillar-row td {{ color: #E5D5B8 !important; }}
  [data-ogsc] .cta-btn {{ background-color: #F3C64F !important; color: #0B0F17 !important; }}
</style>
</head>
<body>

<div class="container">

  <!-- HEADER -->
  <div class="header">
    <div class="bismillah">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ</div>
    <div class="brand-title">Wasim Trader <span>Kaffans</span></div>
    <div class="brand-subtitle">Sunnah-Compliant Islamic Burial Garments · {country}</div>
  </div>
  <div class="gold-divider"></div>

  <!-- CONTENT -->
  <div class="content">

    <p class="salutation">As-salamu alaykum wa rahmatullahi wa barakatuh,</p>

    <div class="headline">Prepared with Reverence. Ready When Your Community Needs It Most.</div>

    <p class="body-text">
      We respectfully write to the leadership and funeral services committee of <strong>{clean_name}</strong>. During moments of grief and bereavement, families and volunteer committees should never face the added hardship of unrolling bulk textile bolts or searching for cutting shears.
    </p>

    <p class="body-text">
      <strong>Wasim Trader Kaffans</strong> provides 100% Sunnah-compliant, ready-to-use Islamic burial garments at <strong>$25 per complete set including standard delivery</strong> (minimum order: 100 pieces; mix &amp; match Men's and Women's sets and sizes). Every set is pre-cut to generous, audited dimensions from 100% pure white opaque cotton, complete with pre-cut cotton tie ribbons (Ribat). For emergency Janazah situations requiring expedited courier service, extra rush fees apply.
    </p>

    <!-- PRODUCT CARDS -->
    <table class="cards-table" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td class="card-td">
          <div class="card-badge">Men's Set</div>
          <div class="card-name">3-Piece Sunnah Set</div>
          <div class="card-price">$25 <span style="display:block; font-size:11px; color:#059669; font-weight:600; margin-top:2px;">✓ Delivery Included</span></div>
          <div style="font-size:10.5px; color:#6B7280; margin-top:-6px; margin-bottom:12px; font-weight:500;">Min. Order: 100 pcs (Mix &amp; Match)</div>
          <ul class="card-pieces">
            <li>Lifafa (Outer Shroud)</li>
            <li>Izar (Waist Wrap)</li>
            <li>Qamees (Chest Tunic)</li>
            <li>3-4 Pre-Cut Tie Ribbons</li>
          </ul>
        </td>
        <td class="card-td">
          <div class="card-badge">Women's Set</div>
          <div class="card-name">5-Piece Sunnah Set</div>
          <div class="card-price">$25 <span style="display:block; font-size:11px; color:#059669; font-weight:600; margin-top:2px;">✓ Delivery Included</span></div>
          <div style="font-size:10.5px; color:#6B7280; margin-top:-6px; margin-bottom:12px; font-weight:500;">Min. Order: 100 pcs (Mix &amp; Match)</div>
          <ul class="card-pieces">
            <li>Lifafa (Outer Shroud)</li>
            <li>Izar (Waist Wrap)</li>
            <li>Qamees (Tunic Garment)</li>
            <li>Khimar (Head Veil)</li>
            <li>Seenah-band (Chest Band)</li>
          </ul>
        </td>
      </tr>
    </table>

    <!-- KEY PILLARS -->
    <table class="pillars-table" cellpadding="0" cellspacing="0" border="0">
      <tr class="pillar-row">
        <td class="pillar-bullet">✦</td>
        <td><strong>$25 Including Delivery (Min. 100 pcs):</strong> Standard delivery is fully included in the $25 rate. Mix and match Men's &amp; Women's sets and sizes freely.</td>
      </tr>
      <tr class="pillar-row">
        <td class="pillar-bullet">✦</td>
        <td><strong>Emergency Rush Delivery:</strong> Extra fee charged for expedited priority air courier when Janazah supplies are needed immediately.</td>
      </tr>
      <tr class="pillar-row">
        <td class="pillar-bullet">✦</td>
        <td><strong>100% Pure White Cotton:</strong> Premium high-thread count weave, fully opaque and respectful.</td>
      </tr>
      <tr class="pillar-row">
        <td class="pillar-bullet">✦</td>
        <td><strong>Pre-Cut &amp; Ready:</strong> Zero cutting or measuring required during grief; neat pre-hemmed edges.</td>
      </tr>
    </table>

    <!-- CTA BUTTON -->
    <div class="cta-wrap">
      <a href="{WEBSITE_URL}" class="cta-btn" target="_blank">
        Explore Sizing &amp; Details on Our Website →
      </a>
    </div>

    <p class="body-text" style="margin-top:24px; font-size:13.5px;">
      May Allah (SWT) reward your masjid and volunteers for your dedicated service to the community.
    </p>

    <p style="margin-top:20px; font-size:14px; color:#85500A;">
      Warmest regards,<br/>
      <strong>Wasim</strong><br/>
      <span style="font-size:12px; color:#85500A;">Wasim Trader Kaffans</span><br/>
      <a href="mailto:{GMAIL_ADDRESS}" style="color:#785A28; font-size:12px; text-decoration:none;">{GMAIL_ADDRESS}</a>
    </p>

  </div>

  <!-- FOOTER -->
  <div class="gold-divider"></div>
  <div class="footer">
    <div style="font-family:Georgia,serif; font-size:15px; color:#FBF9F5; margin-bottom:8px;">
      Wasim Trader Kaffans
    </div>
    <div class="footer-links">
      <a href="{WEBSITE_URL}" target="_blank">Visit Website</a> ·
      <a href="{wa_url}" target="_blank">WhatsApp Inquiry</a> ·
      <a href="mailto:{GMAIL_ADDRESS}">Contact via Email</a>
    </div>
    <div class="footer-text">
      Serving Muslim communities and funeral committees across the USA, Australia, and New Zealand.<br/>
      You are receiving this outreach because {footer_mention} is listed as a focal Islamic institution in {country}.
    </div>
  </div>

</div>

</body>
</html>"""

    # Plain Text Fallback
    plain_body = f"""بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ

WASIM TRADER KAFFANS
Sunnah-Compliant Islamic Burial Garments
Website: {WEBSITE_URL}

As-salamu alaykum wa rahmatullahi wa barakatuh,

To the Respected Administration and Funeral Committee of {clean_name},

During moments of bereavement, community volunteers and grieving families should never face the distress of unrolling bulk fabric bolts or searching for cutting shears.

Wasim Trader Kaffans provides 100% Sunnah-compliant, ready-to-use Islamic burial garment sets at $25 per complete set including standard delivery (minimum order: 100 pieces; mix & match Men's and Women's sets):

• MEN'S 3-PIECE SET ($25 / set · Delivery Included · Min. 100 pcs):
  - Lifafa (Outer Shroud)
  - Izar (Waist Wrap)
  - Qamees (Tunic)
  - Pre-cut cotton tie ribbons (Ribat) included

• WOMEN'S 5-PIECE SET ($25 / set · Delivery Included · Min. 100 pcs):
  - Lifafa (Outer Shroud)
  - Izar (Waist Wrap)
  - Qamees (Tunic)
  - Khimar (Head Veil)
  - Seenah-band (Chest Band)
  - Pre-cut cotton tie ribbons included

PRICING & DELIVERY TERMS:
- $25 per set includes standard delivery (Minimum order: 100 pieces)
- Mix & Match Men's and Women's sets and sizes freely
- Expedited emergency courier available for an extra rush fee
- Rapid Dispatch to USA, Australia & New Zealand

VIEW SIZING & PRODUCT DETAILS:
{WEBSITE_URL}

To place an order, discuss community reserve stock, or inquire about expedited rush delivery, simply reply directly to this email or contact us on WhatsApp: {wa_url}

May Allah (SWT) reward your volunteers and community for your service.

Wasim
Wasim Trader Kaffans
Email: {GMAIL_ADDRESS}
Website: {WEBSITE_URL}
"""

    return subject, html_body, plain_body


# ──────────────────────────────────────────────
# CSV RECIPIENT LOADER
# ──────────────────────────────────────────────
def load_recipients(csv_path: str, country_filter: str = None) -> list[dict]:
    path = Path(csv_path)
    if not path.exists():
        log.error("CSV file not found: %s", csv_path)
        return []

    recipients = []
    seen_emails = set()
    skipped_invalid = 0
    skipped_duplicate = 0
    skipped_country = 0

    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_email = row.get("Email", "").strip()
            if not is_valid_email(raw_email):
                skipped_invalid += 1
                continue

            email = raw_email.lower()
            if email in seen_emails:
                skipped_duplicate += 1
                continue

            country = row.get("Country", "").strip()
            if country_filter and country_filter.lower() not in country.lower():
                skipped_country += 1
                continue

            name = row.get("Name", "").strip()
            name_lower = name.lower()
            if email in EXCLUDED_EMAILS or any(kw in name_lower for kw in EXCLUDED_KEYWORDS):
                skipped_invalid += 1
                continue

            seen_emails.add(email)
            recipients.append({
                "country": country or "International",
                "name": name,
                "email": email,
                "website": row.get("Website", "").strip(),
                "address": row.get("Address", "").strip().replace("\ue0c8\n", "").replace("\ue0c8", "").strip(),
            })

    log.info(
        "📋 Loaded %d valid recipients (Skipped: %d invalid, %d duplicates, %d other country)",
        len(recipients), skipped_invalid, skipped_duplicate, skipped_country
    )
    return recipients


# ──────────────────────────────────────────────
# EMAIL LOG DEDUPLICATION
# ──────────────────────────────────────────────
def load_already_sent(log_path: str) -> set[str]:
    path = Path(log_path)
    if not path.exists():
        return set()

    sent = set()
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Status") in ("SENT", "EXCLUDED", "BLOCKED"):
                email = row.get("Email", "").strip().lower()
                if email:
                    sent.add(email)
    return sent


# ──────────────────────────────────────────────
# PREVIEW GENERATOR (ALL MASJIDS FROM CSV)
# ──────────────────────────────────────────────
def generate_preview(recipients: list[dict]) -> str:
    """
    Generates a rich, interactive preview HTML file containing each of the
    masjids from the CSV. Includes real-time search, dropdown navigation,
    country filtering, and both single-inspector and continuous-feed modes.
    """
    import json
    out_path = Path(PREVIEW_FILE)
    if not recipients:
        recipients = [{"name": "Auburn Gallipoli Mosque", "country": "Australia",
                       "email": "info@gallipolimosque.org.au", "website": "http://www.gallipolimosque.org.au/",
                       "address": "15/19 Gelibolu Parade, Auburn NSW 2144, Australia"}]

    masjids_json = json.dumps(recipients, ensure_ascii=False)
    total_count = len(recipients)

    # Initial render for the first masjid
    first_subject, first_html, first_plain = build_email_content(recipients[0]["name"], recipients[0]["country"])

    preview_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Wasim Trader Kaffans — Email Campaign Preview ({total_count} Masjids)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:wght@600;700&family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background-color: #EFECE6;
    color: #1F2937;
    min-height: 100vh;
  }}

  /* STICKY TOP TOOLBAR */
  .preview-toolbar {{
    position: sticky;
    top: 0;
    z-index: 1000;
    background: #111827;
    color: #F9FAFB;
    border-bottom: 2px solid #D4AF37;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    padding: 12px 20px;
  }}
  .toolbar-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 10px;
  }}
  .toolbar-title {{
    font-family: Georgia, serif;
    font-size: 17px;
    font-weight: 600;
    color: #FBF9F5;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .toolbar-title span {{
    color: #D4AF37;
  }}
  .badge-count {{
    background: rgba(212, 175, 55, 0.2);
    color: #FBBF24;
    border: 1px solid rgba(212, 175, 55, 0.4);
    font-size: 11.5px;
    font-family: monospace;
    padding: 3px 10px;
    border-radius: 9999px;
    font-weight: 600;
  }}

  .mode-toggle {{
    display: flex;
    background: #1F2937;
    border-radius: 6px;
    padding: 3px;
    border: 1px solid #374151;
  }}
  .mode-btn {{
    background: none;
    border: none;
    color: #9CA3AF;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .mode-btn.active {{
    background: #D4AF37;
    color: #0B0F17;
  }}

  /* CONTROLS ROW */
  .toolbar-controls {{
    display: grid;
    grid-template-columns: 200px 1fr auto auto;
    gap: 10px;
    align-items: center;
  }}
  @media (max-width: 900px) {{
    .toolbar-controls {{
      grid-template-columns: 1fr;
    }}
  }}
  .search-input {{
    background: #1F2937;
    border: 1px solid #374151;
    color: #F9FAFB;
    padding: 8px 12px;
    font-size: 13px;
    border-radius: 5px;
    outline: none;
    width: 100%;
  }}
  .search-input:focus {{
    border-color: #D4AF37;
    box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2);
  }}
  .masjid-select {{
    background: #1F2937;
    border: 1px solid #374151;
    color: #F9FAFB;
    padding: 8px 12px;
    font-size: 13px;
    border-radius: 5px;
    outline: none;
    width: 100%;
    cursor: pointer;
  }}
  .masjid-select:focus {{
    border-color: #D4AF37;
  }}

  .nav-btn-group {{
    display: flex;
    gap: 6px;
  }}
  .nav-btn {{
    background: #374151;
    color: #F9FAFB;
    border: 1px solid #4B5563;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 5px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: all 0.15s ease;
  }}
  .nav-btn:hover:not(:disabled) {{
    background: #4B5563;
    border-color: #D4AF37;
    color: #D4AF37;
  }}
  .nav-btn:disabled {{
    opacity: 0.4;
    cursor: not-allowed;
  }}

  /* COUNTRY FILTER PILLS */
  .country-filter-pills {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    align-items: center;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }}
  .country-pill {{
    background: #1F2937;
    border: 1px solid #374151;
    color: #9CA3AF;
    font-size: 11.5px;
    padding: 3px 10px;
    border-radius: 9999px;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .country-pill:hover {{
    color: #FFFFFF;
    border-color: #6B7280;
  }}
  .country-pill.active {{
    background: rgba(212, 175, 55, 0.18);
    color: #FBBF24;
    border-color: #D4AF37;
    font-weight: 600;
  }}

  /* RECIPIENT METADATA CARD */
  .meta-card {{
    max-width: 680px;
    margin: 20px auto 14px;
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 10px 16px;
    font-size: 12.5px;
  }}
  .meta-item strong {{
    display: block;
    color: #6B7280;
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
  }}
  .meta-item span, .meta-item a {{
    color: #85500A;
    font-weight: 600;
    text-decoration: none;
    word-break: break-all;
  }}
  .meta-item a:hover {{
    color: #059669;
    text-decoration: underline;
  }}
  .meta-subject {{
    grid-column: 1 / -1;
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 5px;
    padding: 8px 12px;
    margin-top: 4px;
  }}
  .meta-subject strong {{
    color: #85500A;
  }}

  /* EMAIL PREVIEW FRAME */
  .email-frame-wrap {{
    max-width: 680px;
    margin: 0 auto 60px;
  }}

  /* CONTINUOUS FEED VIEW */
  .feed-view {{
    display: none;
    max-width: 680px;
    margin: 20px auto 80px;
  }}
  .feed-card {{
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    margin-bottom: 36px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  }}
  .feed-header {{
    background: #111827;
    color: #F9FAFB;
    padding: 12px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #D4AF37;
    font-size: 13px;
  }}
  .feed-header .feed-title {{
    font-weight: 600;
    color: #F3C64F;
  }}
  .feed-header .feed-email {{
    color: #D4AF37;
    font-family: monospace;
    font-size: 12px;
  }}
  .feed-content {{
    padding: 12px;
    background: #F4F1EA;
  }}

  /* PLAIN TEXT VIEW */
  .plain-view {{
    display: none;
    max-width: 680px;
    margin: 20px auto;
    background: #111827;
    color: #E5E7EB;
    border-radius: 8px;
    padding: 24px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre-wrap;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  }}
</style>
</head>
<body>

<!-- STICKY TOP TOOLBAR -->
<div class="preview-toolbar">
  <div class="toolbar-top">
    <div class="toolbar-title">
      Wasim Trader <span>Kaffans</span> · Masjid Cold Email Campaign Preview
      <span class="badge-count" id="badge-count">{total_count} Masjids</span>
    </div>

    <!-- VIEW MODE TOGGLES -->
    <div class="mode-toggle">
      <button class="mode-btn active" id="btn-mode-single" onclick="setMode('single')">🔍 Single Inspector</button>
      <button class="mode-btn" id="btn-mode-feed" onclick="setMode('feed')">📜 Continuous Feed (All)</button>
      <button class="mode-btn" id="btn-mode-plain" onclick="setMode('plain')">📝 Plain Text</button>
      <button class="mode-btn" id="btn-theme-preview" onclick="togglePreviewTheme()" style="border-left: 2px solid #4B5563; margin-left: 6px;">🌙 Dark Email Mode</button>
    </div>
  </div>

  <div class="toolbar-controls">
    <input type="text" id="searchInput" class="search-input" placeholder="🔍 Search by name, city, email..." oninput="handleSearch()"/>
    
    <select id="masjidSelector" class="masjid-select" onchange="handleSelectChange(this.value)">
      <!-- Populated via JS -->
    </select>

    <div class="nav-btn-group">
      <button class="nav-btn" id="prevBtn" onclick="navigateStep(-1)" title="Previous (Left Arrow)">◀ Prev</button>
      <button class="nav-btn" id="nextBtn" onclick="navigateStep(1)" title="Next (Right Arrow)">Next ▶</button>
      <button class="nav-btn" onclick="randomMasjid()" title="Jump to Random Masjid">🎲</button>
    </div>
  </div>

  <!-- COUNTRY FILTER PILLS -->
  <div class="country-filter-pills" id="countryPills">
    <!-- Populated via JS -->
  </div>
</div>

<!-- SINGLE INSPECTOR CONTAINER -->
<div id="single-view-container">
  <!-- RECIPIENT METADATA CARD -->
  <div class="meta-card">
    <div class="meta-grid">
      <div class="meta-item">
        <strong>Recipient Masjid</strong>
        <span id="meta-name">—</span>
      </div>
      <div class="meta-item">
        <strong>Target Email Address</strong>
        <a id="meta-email" href="#">—</a>
      </div>
      <div class="meta-item">
        <strong>Country / Territory</strong>
        <span id="meta-country">—</span>
      </div>
      <div class="meta-item">
        <strong>Physical Address</strong>
        <span id="meta-address">—</span>
      </div>
      <div class="meta-subject">
        <strong>Dispatched Subject:</strong> <span id="meta-subject">—</span>
      </div>
    </div>
  </div>

  <!-- RENDERED EMAIL CONTAINER -->
  <div class="email-frame-wrap" id="email-frame-wrap">
    <!-- Rendered dynamically -->
  </div>
</div>

<!-- CONTINUOUS FEED CONTAINER (ALL MASJIDS) -->
<div class="feed-view" id="feed-container">
  <!-- Rendered dynamically -->
</div>

<!-- PLAIN TEXT CONTAINER -->
<div class="plain-view" id="plain-container">
  <!-- Plain text rendered dynamically -->
</div>

<!-- DATA & SCRIPT -->
<script>
  const ALL_MASJIDS = {masjids_json};
  const WEBSITE_URL = "{WEBSITE_URL}";
  const GMAIL_ADDRESS = "{GMAIL_ADDRESS}";
  const WHATSAPP_NUMBER = "{WHATSAPP_NUMBER}";
  
  let filteredMasjids = [...ALL_MASJIDS];
  let currentIndex = 0;
  let currentMode = 'single';
  let activeCountry = 'ALL';
  let isDarkPreview = false;

  function togglePreviewTheme() {{
    isDarkPreview = !isDarkPreview;
    const btn = document.getElementById('btn-theme-preview');
    if (btn) {{
      btn.innerHTML = isDarkPreview ? '☀️ Light Email Mode' : '🌙 Dark Email Mode';
    }}
    if (currentMode === 'single') {{
      renderCurrentSingle();
    }} else if (currentMode === 'feed') {{
      renderFeed();
    }}
  }}

  // Generate Email HTML for a specific masjid
  function generateEmailHTML(m) {{
    const rawName = (m.name || '').trim();
    const cleanName = rawName || 'your respected masjid';
    const country = m.country || 'International';
    const subject = cleanName === 'your respected masjid' 
      ? 'Sunnah Kaffan Sets for Your Masjid — $25 (Delivery Included · Min 100 Pcs)'
      : `Sunnah Kaffan Sets for ${{cleanName}} — $25 (Delivery Included · Min 100 Pcs)`;

    const footerMention = cleanName === 'your respected masjid' ? 'your masjid' : cleanName;
    
    const waText = encodeURIComponent(`As-salamu alaykum, I am inquiring about Kaffan sets for ${{cleanName}}`);
    const waUrl = WHATSAPP_NUMBER 
      ? `https://wa.me/${{WHATSAPP_NUMBER}}?text=${{waText}}`
      : `https://wa.me/?text=${{waText}}`;

    const bgOuter = isDarkPreview ? '#0B0F17' : '#F4F1EA';
    const bgContainer = isDarkPreview ? '#111827' : '#FFFFFF';
    const borderColor = isDarkPreview ? '#2D3748' : '#E5E7EB';
    const textColor = isDarkPreview ? '#E5D5B8' : '#4A3515';
    const headlineColor = isDarkPreview ? '#F3C64F' : '#85500A';
    const salutationColor = isDarkPreview ? '#BFA980' : '#785A28';
    const cardBg = isDarkPreview ? '#161B22' : '#FAF8F5';
    const cardTitleColor = isDarkPreview ? '#F3C64F' : '#85500A';
    const cardPiecesColor = isDarkPreview ? '#BFA980' : '#4B5563';
    const badgeColor = isDarkPreview ? '#F3C64F' : '#85500A';
    const badgeBg = isDarkPreview ? 'rgba(243, 198, 79, 0.15)' : 'rgba(133, 80, 10, 0.1)';
    const ctaBg = isDarkPreview ? '#F3C64F' : '#85500A';
    const ctaColor = isDarkPreview ? '#0B0F17' : '#FFFFFF';
    const ctaWeight = isDarkPreview ? '700' : '600';
    const footerBg = isDarkPreview ? '#0B0F17' : '#111827';

    return `
    <div style="background-color: ${{bgOuter}}; padding: 24px 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; transition: background-color 0.2s ease;">
      <div style="max-width: 600px; margin: 0 auto; background-color: ${{bgContainer}}; border-radius: 8px; overflow: hidden; border: 1px solid ${{borderColor}}; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04); transition: all 0.2s ease;">
        
        <!-- HEADER -->
        <div style="background-color: #111827; padding: 36px 28px 30px; text-align: center;">
          <div style="font-family: 'Amiri', 'Traditional Arabic', 'Times New Roman', serif; font-size: 20px; color: #D4AF37; margin-bottom: 12px; letter-spacing: 1px;">
            بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ
          </div>
          <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 24px; color: #FBF9F5; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 6px;">
            Wasim Trader <span style="color: #D4AF37;">Kaffans</span>
          </div>
          <div style="font-size: 11px; color: #9CA3AF; text-transform: uppercase; letter-spacing: 2px;">
            Sunnah-Compliant Islamic Burial Garments · ${{country}}
          </div>
        </div>
        <div style="height: 3px; background: linear-gradient(90deg, #111827 0%, #D4AF37 50%, #111827 100%);"></div>

        <!-- CONTENT -->
        <div style="padding: 36px 32px 28px;">
          <p style="font-size: 15px; color: ${{salutationColor}}; font-style: italic; margin-bottom: 18px;">
            As-salamu alaykum wa rahmatullahi wa barakatuh,
          </p>

          <div style="font-family: Georgia, 'Times New Roman', serif; font-size: 20px; color: ${{headlineColor}}; line-height: 1.4; margin-bottom: 16px; font-weight: 600;">
            Prepared with Reverence. Ready When Your Community Needs It Most.
          </div>

          <p style="font-size: 14.5px; line-height: 1.7; color: ${{textColor}}; margin-bottom: 18px;">
            We respectfully write to the leadership and funeral services committee of <strong>${{cleanName}}</strong>. During moments of grief and bereavement, families and volunteer committees should never face the added hardship of unrolling bulk textile bolts or searching for cutting shears.
          </p>

          <p style="font-size: 14.5px; line-height: 1.7; color: ${{textColor}}; margin-bottom: 18px;">
            <strong>Wasim Trader Kaffans</strong> provides 100% Sunnah-compliant, ready-to-use Islamic burial garments at <strong>$25 per complete set including standard delivery</strong> (minimum order: 100 pieces; mix &amp; match Men's and Women's sets and sizes). Every set is pre-cut to generous, audited dimensions from 100% pure white opaque cotton, complete with pre-cut cotton tie ribbons (Ribat). For emergency Janazah situations requiring expedited courier service, extra rush fees apply.
          </p>

          <!-- PRODUCT CARDS -->
          <table style="width: 100%; border-collapse: separate; border-spacing: 12px 0; margin: 24px -12px;" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="width: 50%; vertical-align: top; background-color: ${{cardBg}}; border: 1px solid ${{borderColor}}; border-radius: 6px; padding: 20px 16px; text-align: center;">
                <div style="display: inline-block; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: ${{badgeColor}}; background-color: ${{badgeBg}}; padding: 3px 8px; border-radius: 4px; margin-bottom: 10px;">
                  Men's Set
                </div>
                <div style="font-family: Georgia, serif; font-size: 16px; color: ${{cardTitleColor}}; font-weight: 600; margin-bottom: 6px;">
                  3-Piece Sunnah Set
                </div>
                <div style="font-size: 26px; color: ${{headlineColor}}; font-weight: 700; font-family: Georgia, serif; margin-bottom: 4px;">
                  $25 <span style="display:block; font-size: 11px; color: #059669; font-weight: 600; margin-top: 2px;">✓ Delivery Included</span>
                </div>
                <div style="font-size: 10.5px; color: #6B7280; margin-bottom: 12px; font-weight: 500;">Min. Order: 100 pcs (Mix &amp; Match)</div>
                <ul style="font-size: 12px; color: ${{cardPiecesColor}}; line-height: 1.5; text-align: left; border-top: 1px solid ${{borderColor}}; padding-top: 10px; list-style: none;">
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> Lifafa (Outer Shroud)</li>
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> Izar (Waist Wrap)</li>
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> Qamees (Chest Tunic)</li>
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> 3-4 Pre-Cut Tie Ribbons</li>
                </ul>
              </td>
              <td style="width: 50%; vertical-align: top; background-color: ${{cardBg}}; border: 1px solid ${{borderColor}}; border-radius: 6px; padding: 20px 16px; text-align: center;">
                <div style="display: inline-block; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: ${{badgeColor}}; background-color: ${{badgeBg}}; padding: 3px 8px; border-radius: 4px; margin-bottom: 10px;">
                  Women's Set
                </div>
                <div style="font-family: Georgia, serif; font-size: 16px; color: ${{cardTitleColor}}; font-weight: 600; margin-bottom: 6px;">
                  5-Piece Sunnah Set
                </div>
                <div style="font-size: 26px; color: ${{headlineColor}}; font-weight: 700; font-family: Georgia, serif; margin-bottom: 4px;">
                  $25 <span style="display:block; font-size: 11px; color: #059669; font-weight: 600; margin-top: 2px;">✓ Delivery Included</span>
                </div>
                <div style="font-size: 10.5px; color: #6B7280; margin-bottom: 12px; font-weight: 500;">Min. Order: 100 pcs (Mix &amp; Match)</div>
                <ul style="font-size: 12px; color: ${{cardPiecesColor}}; line-height: 1.5; text-align: left; border-top: 1px solid ${{borderColor}}; padding-top: 10px; list-style: none;">
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> Lifafa (Outer Shroud)</li>
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> Izar (Waist Wrap)</li>
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> Qamees (Tunic Garment)</li>
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> Khimar (Head Veil)</li>
                  <li style="margin-bottom: 4px;"><span style="color:#059669; font-weight:bold;">✓</span> Seenah-band (Chest Band)</li>
                </ul>
              </td>
            </tr>
          </table>

          <!-- KEY PILLARS -->
          <table style="width: 100%; margin: 22px 0; border-collapse: collapse;" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td style="width: 24px; color: #D4AF37; font-size: 14px; font-weight: bold; padding: 8px 0; vertical-align: top;">✦</td>
              <td style="padding: 8px 0; font-size: 13.5px; color: ${{textColor}}; vertical-align: top;">
                <strong>$25 Including Delivery (Min. 100 pcs):</strong> Standard delivery is fully included in the $25 rate. Mix and match Men's &amp; Women's sets and sizes freely.
              </td>
            </tr>
            <tr>
              <td style="width: 24px; color: #D4AF37; font-size: 14px; font-weight: bold; padding: 8px 0; vertical-align: top;">✦</td>
              <td style="padding: 8px 0; font-size: 13.5px; color: ${{textColor}}; vertical-align: top;">
                <strong>Emergency Rush Delivery:</strong> Extra fee charged for expedited priority air courier when Janazah supplies are needed immediately.
              </td>
            </tr>
            <tr>
              <td style="width: 24px; color: #D4AF37; font-size: 14px; font-weight: bold; padding: 8px 0; vertical-align: top;">✦</td>
              <td style="padding: 8px 0; font-size: 13.5px; color: ${{textColor}}; vertical-align: top;">
                <strong>100% Pure White Cotton:</strong> Premium high-thread count weave, fully opaque and respectful.
              </td>
            </tr>
            <tr>
              <td style="width: 24px; color: #D4AF37; font-size: 14px; font-weight: bold; padding: 8px 0; vertical-align: top;">✦</td>
              <td style="padding: 8px 0; font-size: 13.5px; color: ${{textColor}}; vertical-align: top;">
                <strong>Pre-Cut &amp; Ready:</strong> Zero cutting or measuring required during grief; neat pre-hemmed edges.
              </td>
            </tr>
          </table>

          <!-- CTA BUTTON -->
          <div style="text-align: center; margin: 30px 0 24px;">
            <a href="${{WEBSITE_URL}}" style="display: inline-block; background-color: ${{ctaBg}}; color: ${{ctaColor}} !important; text-decoration: none; font-size: 13.5px; font-weight: ${{ctaWeight}}; letter-spacing: 0.5px; padding: 15px 32px; border-radius: 5px; box-shadow: 0 3px 10px rgba(133, 80, 10, 0.25);" target="_blank">
              Explore Sizing &amp; Details on Our Website →
            </a>
          </div>

          <p style="margin-top: 24px; font-size: 13.5px; line-height: 1.7; color: ${{textColor}};">
            May Allah (SWT) reward your masjid and volunteers for your dedicated service to the community.
          </p>

          <p style="margin-top: 20px; font-size: 14px; color: ${{headlineColor}};">
            Warmest regards,<br/>
            <strong>Wasim</strong><br/>
            <span style="font-size: 12px; color: ${{badgeColor}};">Wasim Trader Kaffans</span><br/>
            <a href="mailto:${{GMAIL_ADDRESS}}" style="color: ${{salutationColor}}; font-size: 12px; text-decoration: none;">${{GMAIL_ADDRESS}}</a>
          </p>
        </div>

        <!-- FOOTER -->
        <div style="height: 3px; background: linear-gradient(90deg, #111827 0%, #D4AF37 50%, #111827 100%);"></div>
        <div style="background-color: ${{footerBg}}; padding: 28px 24px; text-align: center; color: #9CA3AF;">
          <div style="font-family: Georgia, serif; font-size: 15px; color: #F3C64F; margin-bottom: 8px;">
            Wasim Trader Kaffans
          </div>
          <div style="font-size: 12px; margin-bottom: 12px;">
            <a href="${{WEBSITE_URL}}" style="color: #D4AF37; text-decoration: none; margin: 0 8px;" target="_blank">Visit Website</a> ·
            <a href="${{waUrl}}" style="color: #D4AF37; text-decoration: none; margin: 0 8px;" target="_blank">WhatsApp Inquiry</a> ·
            <a href="mailto:${{GMAIL_ADDRESS}}" style="color: #D4AF37; text-decoration: none; margin: 0 8px;">Contact via Email</a>
          </div>
          <div style="font-size: 11.5px; line-height: 1.6; color: #6B7280;">
            Serving Muslim communities and funeral committees across the USA, Australia, and New Zealand.<br/>
            You are receiving this outreach because ${{footerMention}} is listed as a focal Islamic institution in ${{country}}.
          </div>
        </div>

      </div>
    </div>`;
  }}

  // Plain Text Version
  function generatePlainText(m) {{
    const rawName = (m.name || '').trim();
    const cleanName = rawName || 'your respected masjid';
    const country = m.country || 'International';
    const waText = encodeURIComponent(`As-salamu alaykum, I am inquiring about Kaffan sets for ${{cleanName}}`);
    const waUrl = WHATSAPP_NUMBER 
      ? `https://wa.me/${{WHATSAPP_NUMBER}}?text=${{waText}}`
      : `https://wa.me/?text=${{waText}}`;

    return `بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ

WASIM TRADER KAFFANS
Sunnah-Compliant Islamic Burial Garments
Website: ${{WEBSITE_URL}}

As-salamu alaykum wa rahmatullahi wa barakatuh,

To the Respected Administration and Funeral Committee of ${{cleanName}},

We respectfully write to the leadership and funeral services committee of ${{cleanName}}. During moments of grief and bereavement, families and volunteer committees should never face the added hardship of unrolling bulk textile bolts or searching for cutting shears.

Wasim Trader Kaffans provides 100% Sunnah-compliant, ready-to-use Islamic burial garment sets at $25 per complete set including standard delivery (minimum order: 100 pieces; mix & match Men's and Women's sets):

• MEN'S 3-PIECE SET ($25 / set · Delivery Included · Min. 100 pcs):
  - Lifafa (Outer Shroud)
  - Izar (Waist Wrap)
  - Qamees (Tunic)
  - Pre-cut cotton tie ribbons (Ribat) included

• WOMEN'S 5-PIECE SET ($25 / set · Delivery Included · Min. 100 pcs):
  - Lifafa (Outer Shroud)
  - Izar (Waist Wrap)
  - Qamees (Tunic)
  - Khimar (Head Veil)
  - Seenah-band (Chest Band)
  - Pre-cut cotton tie ribbons included

PRICING & DELIVERY TERMS:
- $25 per set includes standard delivery (Minimum order: 100 pieces)
- Mix & Match Men's and Women's sets and sizes freely
- Expedited emergency courier available for an extra rush fee
- Rapid Dispatch to USA, Australia & New Zealand

VIEW SIZING & PRODUCT DETAILS:
${{WEBSITE_URL}}

To place an order, discuss community reserve stock, or inquire about expedited rush delivery, simply reply directly to this email or contact us on WhatsApp: ${{waUrl}}

May Allah (SWT) reward your volunteers and community for your service.

Wasim
Wasim Trader Kaffans
Email: ${{GMAIL_ADDRESS}}
Website: ${{WEBSITE_URL}}`;
  }}

  // Build Country Filter Pills
  function buildCountryFilters() {{
    const counts = {{ ALL: ALL_MASJIDS.length }};
    ALL_MASJIDS.forEach(m => {{
      const c = m.country || 'Other';
      counts[c] = (counts[c] || 0) + 1;
    }});

    const pillsDiv = document.getElementById('countryPills');
    pillsDiv.innerHTML = Object.keys(counts).map(c => `
      <button class="country-pill ${{c === activeCountry ? 'active' : ''}}" onclick="filterByCountry('${{c}}')">
        ${{c}} (${{counts[c]}})
      </button>
    `).join('');
  }}

  // Populate Dropdown
  function populateSelect() {{
    const sel = document.getElementById('masjidSelector');
    sel.innerHTML = filteredMasjids.map((m, idx) => `
      <option value="${{idx}}" ${{idx === currentIndex ? 'selected' : ''}}>
        #${{idx + 1}}: ${{m.name || 'Unnamed Masjid'}} (${{m.country || 'N/A'}}) — ${{m.email}}
      </option>
    `).join('');
  }}

  // Render the currently selected masjid in Single View
  function renderCurrentSingle() {{
    if (!filteredMasjids.length) return;
    const m = filteredMasjids[currentIndex];

    // Update metadata
    const rawName = (m.name || '').trim();
    const cleanName = rawName || 'your respected masjid';
    const subject = cleanName === 'your respected masjid' 
      ? 'Sunnah Kaffan Sets for Your Masjid — $25 (Delivery Included · Min 100 Pcs)'
      : `Sunnah Kaffan Sets for ${{cleanName}} — $25 (Delivery Included · Min 100 Pcs)`;

    document.getElementById('meta-name').textContent = rawName || '(Fallback: "your respected masjid")';
    
    const emailEl = document.getElementById('meta-email');
    emailEl.textContent = m.email || 'None';
    emailEl.href = `mailto:${{m.email}}`;

    document.getElementById('meta-country').textContent = m.country || 'International';
    document.getElementById('meta-address').textContent = m.address || 'Public directory listing';
    document.getElementById('meta-subject').textContent = subject;

    // Update buttons & dropdown
    document.getElementById('masjidSelector').value = currentIndex;
    document.getElementById('badge-count').textContent = `Masjid ${{currentIndex + 1}} of ${{filteredMasjids.length}}`;
    document.getElementById('prevBtn').disabled = (currentIndex === 0);
    document.getElementById('nextBtn').disabled = (currentIndex === filteredMasjids.length - 1);

    // Render HTML Email
    document.getElementById('email-frame-wrap').innerHTML = generateEmailHTML(m);

    // Render Plain Text
    document.getElementById('plain-container').textContent = generatePlainText(m);
  }}

  // Render Continuous Feed
  function renderFeed() {{
    const feed = document.getElementById('feed-container');
    feed.innerHTML = filteredMasjids.map((m, idx) => `
      <div class="feed-card" id="feed-card-${{idx}}">
        <div class="feed-header">
          <div class="feed-title">#${{idx + 1}} of ${{filteredMasjids.length}} · ${{m.name || 'Your Respected Masjid'}} (${{m.country}})</div>
          <div class="feed-email">${{m.email}}</div>
        </div>
        <div class="feed-content">
          ${{generateEmailHTML(m)}}
        </div>
      </div>
    `).join('');
  }}

  // Mode Switcher
  function setMode(mode) {{
    currentMode = mode;
    document.getElementById('btn-mode-single').classList.toggle('active', mode === 'single');
    document.getElementById('btn-mode-feed').classList.toggle('active', mode === 'feed');
    document.getElementById('btn-mode-plain').classList.toggle('active', mode === 'plain');

    document.getElementById('single-view-container').style.display = (mode === 'single') ? 'block' : 'none';
    document.getElementById('feed-container').style.display = (mode === 'feed') ? 'block' : 'none';
    document.getElementById('plain-container').style.display = (mode === 'plain') ? 'block' : 'none';

    if (mode === 'feed') {{
      renderFeed();
    }}
  }}

  // Filter By Country
  function filterByCountry(c) {{
    activeCountry = c;
    buildCountryFilters();
    applyFilters();
  }}

  // Search input handler
  function handleSearch() {{
    applyFilters();
  }}

  // Combined filter logic
  function applyFilters() {{
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    filteredMasjids = ALL_MASJIDS.filter(m => {{
      const matchCountry = (activeCountry === 'ALL' || (m.country || '').toLowerCase() === activeCountry.toLowerCase());
      if (!matchCountry) return false;
      if (!query) return true;
      const haystack = `${{m.name}} ${{m.email}} ${{m.country}} ${{m.address}}`.toLowerCase();
      return haystack.includes(query);
    }});

    currentIndex = 0;
    populateSelect();
    renderCurrentSingle();
    if (currentMode === 'feed') {{
      renderFeed();
    }}
  }}

  function handleSelectChange(val) {{
    currentIndex = parseInt(val, 10);
    renderCurrentSingle();
    if (currentMode === 'feed') {{
      const el = document.getElementById(`feed-card-${{currentIndex}}`);
      if (el) el.scrollIntoView({{ behavior: 'smooth' }});
    }}
  }}

  function navigateStep(delta) {{
    const nextIdx = currentIndex + delta;
    if (nextIdx >= 0 && nextIdx < filteredMasjids.length) {{
      currentIndex = nextIdx;
      renderCurrentSingle();
    }}
  }}

  function randomMasjid() {{
    if (!filteredMasjids.length) return;
    currentIndex = Math.floor(Math.random() * filteredMasjids.length);
    renderCurrentSingle();
  }}

  // Keyboard navigation
  window.addEventListener('keydown', (e) => {{
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'SELECT') return;
    if (e.key === 'ArrowLeft') navigateStep(-1);
    if (e.key === 'ArrowRight') navigateStep(1);
  }});

  // Initialize
  buildCountryFilters();
  populateSelect();
  renderCurrentSingle();
</script>

</body>
</html>"""

    out_path.write_text(preview_html, encoding="utf-8")
    log.info("🌐 Live HTML email preview generated for all %d masjids: %s", total_count, out_path.resolve())
    return str(out_path.resolve())


def connect_smtp():
    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
    smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
    return smtp


# ──────────────────────────────────────────────
# SENDING ENGINE
# ──────────────────────────────────────────────
def run_campaign(
    recipients: list[dict],
    limit: int = None,
    delay_range: tuple[int, int] = (20, 40),
    dry_run: bool = False,
):
    total = len(recipients)
    if total == 0:
        log.warning("No recipients to process.")
        return

    # Check already sent
    already_sent = load_already_sent(LOG_FILE)
    pending = [r for r in recipients if r["email"] not in already_sent]
    log.info("📩 Previously sent: %d | Pending to send: %d", len(already_sent), len(pending))

    if not pending:
        log.info("🎉 All %d masjids have already received emails! Campaign is 100%% complete.", total)
        return

    if limit and limit > 0:
        pending = pending[:limit]
        log.info("🎯 Session limit applied: processing first %d masjids", len(pending))

    if dry_run:
        log.info("🧪 DRY-RUN MODE: Generating full preview for all %d masjids. No emails will be sent.", len(pending))
        preview_file = generate_preview(pending)
        print("\n" + "=" * 60)
        print("  DRY RUN SUMMARY")
        print("=" * 60)
        print(f"  Total Recipients in Queue:  {len(pending)}")
        print(f"  Target Website Link:        {WEBSITE_URL}")
        print(f"  Preview File (All Masjids): {preview_file}")
        print("  Next 5 Recipients:")
        for r in pending[:5]:
            print(f"    • {r['name'][:35]:<35} | {r['email']:<30} | {r['country']}")
        print("=" * 60 + "\n")
        return

    # Live Send Validation
    if not GMAIL_APP_PASSWORD or GMAIL_APP_PASSWORD.startswith("xxxx"):
        log.error("❌ GMAIL_APP_PASSWORD not configured!")
        log.error("   Please set GMAIL_APP_PASSWORD in your .env file or environment.")
        log.error("   Generate one at https://myaccount.google.com/apppasswords")
        return

    # Open log writer
    log_path = Path(LOG_FILE)
    file_exists = log_path.exists() and log_path.stat().st_size > 0
    log_file = open(log_path, mode="a", newline="", encoding="utf-8")
    log_writer = csv.DictWriter(log_file, fieldnames=["Timestamp", "Country", "Name", "Email", "Status", "Note"])
    if not file_exists:
        log_writer.writeheader()

    # Connect to SMTP
    log.info("🔌 Connecting to Gmail SMTP (smtp.gmail.com:465 SSL)...")
    try:
        smtp = connect_smtp()
        log.info("✅ Authenticated successfully as %s", GMAIL_ADDRESS)
    except Exception as e:
        log.error("❌ SMTP Authentication Failed: %s", e)
        log_file.close()
        return

    sent_count = 0
    fail_count = 0

    print("\n" + "=" * 60)
    print(f"  Starting Live Send: {len(pending)} masjids queued")
    print(f"  Delay between emails: {delay_range[0]}s – {delay_range[1]}s")
    print("=" * 60 + "\n")

    try:
        for idx, rec in enumerate(pending, 1):
            name = rec["name"]
            email = rec["email"]
            country = rec["country"]

            if email.lower() in EXCLUDED_EMAILS or any(kw in name.lower() for kw in EXCLUDED_KEYWORDS):
                log.info("⛔ Skipping excluded recipient in send loop: %s (%s)", name, email)
                continue

            log.info("── [%d/%d] Sending to: %s (%s)", idx, len(pending), name[:35], email)
            try:
                subject, html_body, plain_body = build_email_content(name, country)
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"Wasim Trader Kaffans <{GMAIL_ADDRESS}>"
                msg["To"] = email
                msg["Reply-To"] = GMAIL_ADDRESS

                msg.attach(MIMEText(plain_body, "plain", "utf-8"))
                msg.attach(MIMEText(html_body, "html", "utf-8"))

                # Try sending; auto-reconnect if Gmail dropped the idle socket
                try:
                    smtp.sendmail(GMAIL_ADDRESS, email, msg.as_string())
                except (smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException, OSError) as conn_err:
                    log.warning("   ⚠️ SMTP socket disconnected (%s). Reconnecting to Gmail...", conn_err)
                    try:
                        smtp = connect_smtp()
                        smtp.sendmail(GMAIL_ADDRESS, email, msg.as_string())
                    except Exception as retry_err:
                        raise retry_err

                log.info("   ✅ SENT successfully to %s", email)

                log_writer.writerow({
                    "Timestamp": datetime.now().isoformat(),
                    "Country": country,
                    "Name": name,
                    "Email": email,
                    "Status": "SENT",
                    "Note": "",
                })
                log_file.flush()
                sent_count += 1

            except Exception as e:
                log.warning("   ❌ FAILED (%s): %s", email, e)
                log_writer.writerow({
                    "Timestamp": datetime.now().isoformat(),
                    "Country": country,
                    "Name": name,
                    "Email": email,
                    "Status": "FAILED",
                    "Note": str(e),
                })
                log_file.flush()
                fail_count += 1

            # Polite jitter delay between emails
            if idx < len(pending):
                wait_sec = random.randint(delay_range[0], delay_range[1])
                log.info("   ⏳ Waiting %d seconds before next email...", wait_sec)
                time.sleep(wait_sec)

    except KeyboardInterrupt:
        log.warning("⚠️ Execution interrupted by user! Progress has been logged.")

    finally:
        try:
            if smtp:
                smtp.quit()
        except Exception:
            pass
        log_file.close()
        print("\n" + "=" * 60)
        log.info("🎉 Session Completed! Sent: %d | Failed: %d | Total Processed: %d",
                 sent_count, fail_count, len(pending))
        log.info("📄 Progress logged in: %s", log_path.resolve())
        print("=" * 60 + "\n")


# ──────────────────────────────────────────────
# SINGLE TEST SEND
# ──────────────────────────────────────────────
def send_single_test(test_email: str, first_masjid: dict = None):
    log.info("🧪 Sending trial email to: %s", test_email)
    if not GMAIL_APP_PASSWORD or GMAIL_APP_PASSWORD.startswith("xxxx"):
        log.error("❌ GMAIL_APP_PASSWORD not configured!")
        log.error("   Please set GMAIL_APP_PASSWORD in your .env file.")
        return

    try:
        masjid_name = first_masjid.get("name", "Auburn Gallipoli Mosque") if first_masjid else "Auburn Gallipoli Mosque"
        country = first_masjid.get("country", "Australia") if first_masjid else "Australia"

        log.info("📧 Using draft for: %s (%s)", masjid_name, country)
        subject, html_body, plain_body = build_email_content(masjid_name, country)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Wasim Trader Kaffans <{GMAIL_ADDRESS}>"
        msg["To"] = test_email
        msg["Reply-To"] = GMAIL_ADDRESS

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        log.info("🔌 Connecting to Gmail SMTP (smtp.gmail.com:465 SSL)...")
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_ADDRESS, test_email, msg.as_string())
        smtp.quit()
        log.info("✅ Trial email sent successfully to %s! Please check your inbox.", test_email)
    except Exception as e:
        log.error("❌ Trial send failed: %s", e)


# ──────────────────────────────────────────────
# CLI ENTRY POINT
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Wasim Trader Kaffans — Masjid Cold Email Engine")
    parser.add_argument("--preview", action="store_true", help="Generate email_preview.html including each masjid from the CSV")
    parser.add_argument("--dry-run", action="store_true", help="Generate preview and show recipient count without sending")
    parser.add_argument("--test", type=str, help="Send a single test email to your personal address")
    parser.add_argument("--country", type=str, help="Filter recipients by country (e.g. 'USA', 'Australia', 'New Zealand')")
    parser.add_argument("--limit", type=int, help="Maximum number of emails to send in this session")
    parser.add_argument("--delay", type=str, default="20,40", help="Delay range in seconds between emails (default: '20,40')")
    parser.add_argument("--csv", type=str, default=CSV_FILE, help=f"Path to CSV file (default: {CSV_FILE})")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip manual confirmation prompt (for scheduled/automated runs)")

    args = parser.parse_args()

    # Parse delay
    try:
        parts = [int(p.strip()) for p in args.delay.split(",")]
        delay_range = (parts[0], parts[1]) if len(parts) > 1 else (parts[0], parts[0])
    except Exception:
        delay_range = (20, 40)

    # 1. Load Recipients
    recipients = load_recipients(args.csv, country_filter=args.country)

    # 2. Test Mode
    if args.test:
        first_m = recipients[0] if recipients else None
        send_single_test(args.test, first_masjid=first_m)
        return

    if not recipients:
        return

    # 3. Preview Only
    if args.preview:
        preview_file = generate_preview(recipients)
        print("\n" + "=" * 60)
        print(f"  PREVIEW GENERATED FOR ALL {len(recipients)} MASJIDS")
        print("=" * 60)
        print(f"  File: {preview_file}")
        print("=" * 60 + "\n")
        return

    # 4. Dry-Run or Live
    if args.dry_run:
        run_campaign(recipients, limit=args.limit, dry_run=True)
        return

    # 4. Confirmation for Live Send
    print("\n" + "=" * 60)
    print("  WASIM TRADER KAFFANS — COLD EMAIL OUTREACH")
    print("=" * 60)
    print(f"  Sender Account:      {GMAIL_ADDRESS}")
    print(f"  Target Country:      {args.country or 'All (USA, Australia, New Zealand)'}")
    print(f"  Total Valid Masjids: {len(recipients)}")
    if args.limit:
        print(f"  Batch Limit Cap:     {args.limit} masjids")
    print(f"  Delay Between Mails: {delay_range[0]}s – {delay_range[1]}s")
    print(f"  Website URL:         {WEBSITE_URL}")
    print("=" * 60)

    if not args.yes:
        confirm = input("\n⚠️ Are you sure you want to start sending live emails? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted. No emails sent.\n")
            return

    run_campaign(recipients, limit=args.limit, delay_range=delay_range, dry_run=False)


if __name__ == "__main__":
    main()
