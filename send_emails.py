#!/usr/bin/env python3
"""
Wasim Trader Kaffans — Masjid Cold Email Engine
================================================
Sends a captivating, modern, and respectful HTML cold email to masjids
from masjid_data.csv featuring the newly redesigned website and sample offer.

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

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ──────────────────────────────────────────────
# CONFIGURATION & DEFAULTS
# ──────────────────────────────────────────────
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "iwasimtrader@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://wasim-trader-kaffans.vercel.app/").rstrip("/")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "").strip()

CSV_FILE = "masjid_data.csv"
LOG_FILE = "email_log.csv"
PREVIEW_FILE = "email_preview.html"

# Default subject line (respectful, community-focused, high open rate)
DEFAULT_SUBJECT = "Sunnah Kaffan Sets & Complimentary Sample Kit for {masjid_name}"

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
    clean_name = masjid_name.strip() if masjid_name else "Respected Masjid Administration"
    subject = DEFAULT_SUBJECT.format(masjid_name=clean_name)

    # WhatsApp Link
    wa_text = f"As-salamu alaykum, I am inquiring about Kaffan sets for {clean_name}"
    import urllib.parse
    encoded_wa = urllib.parse.quote(wa_text)
    if WHATSAPP_NUMBER:
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_wa}"
    else:
        wa_url = f"https://wa.me/?text={encoded_wa}"

    # HTML Body
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
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
    color: #111827;
    line-height: 1.4;
    margin-bottom: 16px;
    font-weight: 600;
  }}
  .body-text {{
    font-size: 14.5px;
    line-height: 1.7;
    color: #374151;
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
    color: #996515;
    background-color: rgba(153, 101, 21, 0.1);
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 10px;
  }}
  .card-name {{
    font-family: Georgia, serif;
    font-size: 16px;
    color: #111827;
    font-weight: 600;
    margin-bottom: 6px;
  }}
  .card-price {{
    font-size: 26px;
    color: #111827;
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
    color: #374151;
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
    background-color: #111827;
    color: #FBF9F5 !important;
    text-decoration: none;
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 15px 32px;
    border-radius: 5px;
    box-shadow: 0 3px 10px rgba(17, 24, 39, 0.2);
  }}
  /* Sample Kit Box */
  .sample-box {{
    background-color: #FDFBF7;
    border: 1px dashed #D4AF37;
    border-radius: 6px;
    padding: 20px 22px;
    margin: 26px 0 16px;
  }}
  .sample-title {{
    font-size: 14.5px;
    font-weight: 700;
    color: #996515;
    margin-bottom: 6px;
  }}
  .sample-desc {{
    font-size: 13px;
    color: #4B5563;
    line-height: 1.6;
    margin-bottom: 10px;
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
      We respectfully write to the leadership and funeral services committee of <strong>{clean_name}</strong>.
      During moments of grief and bereavement, families and volunteer committees should never face the added hardship of unrolling bulk textile bolts or searching for cutting shears.
    </p>

    <p class="body-text">
      <strong>Wasim Trader Kaffans</strong> provides 100% Sunnah-compliant, ready-to-use Islamic burial garments. Every set is pre-cut to generous, audited dimensions from 100% pure white opaque cotton, complete with pre-cut cotton tie ribbons (Ribat).
    </p>

    <!-- PRODUCT CARDS -->
    <table class="cards-table" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td class="card-td">
          <div class="card-badge">Men's Set</div>
          <div class="card-name">3-Piece Sunnah Set</div>
          <div class="card-price">$25 <span>/ complete set</span></div>
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
          <div class="card-price">$25 <span>/ complete set</span></div>
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
        <td><strong>100% Pure White Cotton:</strong> Premium high-thread count weave, fully opaque and respectful.</td>
      </tr>
      <tr class="pillar-row">
        <td class="pillar-bullet">✦</td>
        <td><strong>Pre-Cut &amp; Ready:</strong> Zero cutting or measuring required during grief; neat pre-hemmed edges.</td>
      </tr>
      <tr class="pillar-row">
        <td class="pillar-bullet">✦</td>
        <td><strong>Direct Dispatch:</strong> Rapid delivery across the USA, Australia, and New Zealand.</td>
      </tr>
      <tr class="pillar-row">
        <td class="pillar-bullet">✦</td>
        <td><strong>Transparent $25 Community Rate:</strong> Individual sets and bulk carton pricing available.</td>
      </tr>
    </table>

    <!-- CTA BUTTON -->
    <div class="cta-wrap">
      <a href="{WEBSITE_URL}" class="cta-btn" target="_blank">
        Explore Sizing &amp; Details on Our Website →
      </a>
    </div>

    <!-- FREE SAMPLE OFFER -->
    <div class="sample-box">
      <div class="sample-title">🎁 Complimentary Sample Kit for {clean_name}</div>
      <p class="sample-desc">
        We would be honoured to mail <strong>1 complimentary complete sample set</strong> to your Imam or funeral coordinator so your committee can inspect the fabric weight, softness, opacity, and craftsmanship firsthand.
      </p>
      <p style="font-size:12.5px; color:#6B7280; margin:0;">
        To request your sample kit, simply reply to this email with your shipping address, or reach us on WhatsApp:
        <a href="{wa_url}" style="color:#059669; font-weight:600; text-decoration:none;" target="_blank">Chat with Us on WhatsApp</a>
      </p>
    </div>

    <p class="body-text" style="margin-top:24px; font-size:13.5px;">
      May Allah (SWT) reward your masjid and volunteers for your dedicated service to the community.
    </p>

    <p style="margin-top:20px; font-size:14px; color:#111827;">
      Warmest regards,<br/>
      <strong>Wasim</strong><br/>
      <span style="font-size:12px; color:#996515;">Wasim Trader Kaffans</span><br/>
      <a href="mailto:{GMAIL_ADDRESS}" style="color:#6B7280; font-size:12px; text-decoration:none;">{GMAIL_ADDRESS}</a>
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
      You are receiving this outreach because {clean_name} is listed as a focal Islamic institution in {country}.<br/>
      To unsubscribe from future supply announcements, reply with "Unsubscribe" in the subject line.
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

Wasim Trader Kaffans provides 100% Sunnah-compliant, ready-to-use Islamic burial garment sets, pre-cut from 100% pure white opaque cotton:

• MEN'S 3-PIECE SET ($25 / set):
  - Lifafa (Outer Shroud)
  - Izar (Waist Wrap)
  - Qamees (Tunic)
  - Pre-cut cotton tie ribbons (Ribat) included

• WOMEN'S 5-PIECE SET ($25 / set):
  - Lifafa (Outer Shroud)
  - Izar (Waist Wrap)
  - Qamees (Tunic)
  - Khimar (Head Veil)
  - Seenah-band (Chest Band)
  - Pre-cut cotton tie ribbons included

KEY PILLARS:
- 100% Pure White Cotton (Opaque, high-thread count)
- Pre-Cut Dimensions (Zero cutting hassle in grief)
- Flat $25 Community Rate
- Rapid Dispatch to USA, Australia & New Zealand

VIEW SIZING & PRODUCT DETAILS:
{WEBSITE_URL}

COMPLIMENTARY MASJID SAMPLE KIT:
We would be honoured to mail 1 complimentary sample kit to your masjid committee so you can inspect the weave, opacity, and pre-cut quality in person. 

Simply reply directly to this email with your preferred mailing address, or message us on WhatsApp: {wa_url}

May Allah (SWT) reward your volunteers and community for your service.

Wasim
Wasim Trader Kaffans
Email: {GMAIL_ADDRESS}
Website: {WEBSITE_URL}

To unsubscribe, reply with "Unsubscribe" in the subject.
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

            seen_emails.add(email)
            name = row.get("Name", "").strip() or "Respected Masjid Administration"
            recipients.append({
                "country": country or "International",
                "name": name,
                "email": email,
                "website": row.get("Website", "").strip(),
                "address": row.get("Address", "").strip(),
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
            if row.get("Status") == "SENT":
                email = row.get("Email", "").strip().lower()
                if email:
                    sent.add(email)
    return sent


# ──────────────────────────────────────────────
# PREVIEW GENERATOR
# ──────────────────────────────────────────────
def generate_preview(sample_name: str, sample_country: str) -> str:
    subject, html_body, _ = build_email_content(sample_name, sample_country)
    out_path = Path(PREVIEW_FILE)
    out_path.write_text(html_body, encoding="utf-8")
    log.info("🌐 Live HTML email preview generated: %s", out_path.resolve())
    return str(out_path.resolve())


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

    if limit and limit > 0:
        pending = pending[:limit]
        log.info("🎯 Session limit applied: processing first %d masjids", len(pending))

    if dry_run:
        log.info("🧪 DRY-RUN MODE: No emails will be sent.")
        sample = pending[0] if pending else {"name": "Auburn Gallipoli Mosque", "country": "Australia"}
        preview_file = generate_preview(sample["name"], sample["country"])
        print("\n" + "=" * 60)
        print("  DRY RUN SUMMARY")
        print("=" * 60)
        print(f"  Total Recipients in Queue:  {len(pending)}")
        print(f"  Target Website Link:        {WEBSITE_URL}")
        print(f"  Preview File:               {preview_file}")
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
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
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

                smtp.sendmail(GMAIL_ADDRESS, email, msg.as_string())
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
        smtp.quit()
        log_file.close()
        print("\n" + "=" * 60)
        log.info("🎉 Session Completed! Sent: %d | Failed: %d | Total Processed: %d",
                 sent_count, fail_count, len(pending))
        log.info("📄 Progress logged in: %s", log_path.resolve())
        print("=" * 60 + "\n")


# ──────────────────────────────────────────────
# SINGLE TEST SEND
# ──────────────────────────────────────────────
def send_single_test(test_email: str):
    log.info("🧪 Sending 1 test email to: %s", test_email)
    if not GMAIL_APP_PASSWORD or GMAIL_APP_PASSWORD.startswith("xxxx"):
        log.error("❌ GMAIL_APP_PASSWORD not configured!")
        log.error("   Please set GMAIL_APP_PASSWORD in your .env file.")
        return

    try:
        subject, html_body, plain_body = build_email_content("Islamic Center Test Masjid", "USA")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[TEST PREVIEW] {subject}"
        msg["From"] = f"Wasim Trader Kaffans <{GMAIL_ADDRESS}>"
        msg["To"] = test_email
        msg["Reply-To"] = GMAIL_ADDRESS

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        log.info("🔌 Connecting to Gmail SMTP...")
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_ADDRESS, test_email, msg.as_string())
        smtp.quit()
        log.info("✅ Test email sent successfully to %s! Check your inbox.", test_email)
    except Exception as e:
        log.error("❌ Test send failed: %s", e)


# ──────────────────────────────────────────────
# CLI ENTRY POINT
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Wasim Trader Kaffans — Masjid Cold Email Engine")
    parser.add_argument("--dry-run", action="store_true", help="Generate preview and show recipient count without sending")
    parser.add_argument("--test", type=str, help="Send a single test email to your personal address")
    parser.add_argument("--country", type=str, help="Filter recipients by country (e.g. 'USA', 'Australia', 'New Zealand')")
    parser.add_argument("--limit", type=int, help="Maximum number of emails to send in this session")
    parser.add_argument("--delay", type=str, default="20,40", help="Delay range in seconds between emails (default: '20,40')")
    parser.add_argument("--csv", type=str, default=CSV_FILE, help=f"Path to CSV file (default: {CSV_FILE})")

    args = parser.parse_args()

    # Parse delay
    try:
        parts = [int(p.strip()) for p in args.delay.split(",")]
        delay_range = (parts[0], parts[1]) if len(parts) > 1 else (parts[0], parts[0])
    except Exception:
        delay_range = (20, 40)

    # 1. Test Mode
    if args.test:
        send_single_test(args.test)
        return

    # 2. Load Recipients
    recipients = load_recipients(args.csv, country_filter=args.country)
    if not recipients:
        return

    # 3. Dry-Run or Live
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

    confirm = input("\n⚠️ Are you sure you want to start sending live emails? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted. No emails sent.\n")
        return

    run_campaign(recipients, limit=args.limit, delay_range=delay_range, dry_run=False)


if __name__ == "__main__":
    main()
