"""
Masjid / Mosque Data Scraper — Google Maps
==========================================
Scrapes mosque listings from Google Maps for USA, Australia, and New Zealand.
For each listing it extracts:
  • Name
  • Full Address
  • Website URL
  • Email  (from Google Maps if shown, otherwise from the mosque's own website)

Output : masjid_data.csv   (same directory as this script)

Requirements
------------
pip install playwright requests beautifulsoup4
playwright install chromium

Usage
-----
python masjid_scrapper.py
"""

import csv
import re
import time
import random
import logging
from pathlib import Path
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
OUTPUT_FILE  = "masjid_data.csv"
HEADLESS     = True    # set False to watch the browser (great for debugging)
SEARCH_DELAY = (3, 6)  # random sleep between searches (seconds)
SCROLL_PAUSE = 2.0     # seconds between result-list scrolls
MAX_SCROLLS  = 30      # max scroll attempts per query
REQUEST_TO   = 12      # timeout for email scraping (seconds)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

SEARCH_REGIONS = {
    "Australia": [
        "mosques in Sydney Australia",
        "mosques in Melbourne Australia",
        "mosques in Brisbane Australia",
        "mosques in Perth Australia",
        "mosques in Adelaide Australia",
        "mosques in Canberra Australia",
        "mosques in Darwin Australia",
        "mosques in Hobart Australia",
    ],
    "New Zealand": [
        "mosques in Auckland New Zealand",
        "mosques in Wellington New Zealand",
        "mosques in Christchurch New Zealand",
        "mosques in Hamilton New Zealand",
        "mosques in Dunedin New Zealand",
    ],
    "USA": [
        "mosques in New York City USA",
        "mosques in Los Angeles USA",
        "mosques in Chicago USA",
        "mosques in Houston USA",
        "mosques in Phoenix USA",
        "mosques in Philadelphia USA",
        "mosques in San Antonio USA",
        "mosques in San Diego USA",
        "mosques in Dallas USA",
        "mosques in San Jose USA",
        "mosques in Austin USA",
        "mosques in Jacksonville USA",
        "mosques in Fort Worth USA",
        "mosques in Columbus USA",
        "mosques in Charlotte USA",
        "mosques in Indianapolis USA",
        "mosques in San Francisco USA",
        "mosques in Seattle USA",
        "mosques in Denver USA",
        "mosques in Washington DC USA",
        "mosques in Nashville USA",
        "mosques in Oklahoma City USA",
        "mosques in El Paso USA",
        "mosques in Boston USA",
        "mosques in Portland USA",
        "mosques in Las Vegas USA",
        "mosques in Detroit USA",
        "mosques in Memphis USA",
        "mosques in Louisville USA",
        "mosques in Baltimore USA",
        "mosques in Milwaukee USA",
        "mosques in Albuquerque USA",
        "mosques in Tucson USA",
        "mosques in Fresno USA",
        "mosques in Sacramento USA",
        "mosques in Atlanta USA",
        "mosques in Kansas City USA",
        "mosques in Omaha USA",
        "mosques in Raleigh USA",
        "mosques in Miami USA",
        "mosques in Minneapolis USA",
        "mosques in Cleveland USA",
        "mosques in Tulsa USA",
        "mosques in Tampa USA",
        "mosques in New Orleans USA",
        "mosques in Arlington USA",
        "mosques in Bakersfield USA",
        "mosques in Honolulu USA",
        "mosques in Anchorage USA",
        "mosques in Boise USA",
    ],
}

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# EMAIL SCRAPER
# ──────────────────────────────────────────────
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
SKIP_DOMAINS = {"sentry.io", "wixpress.com", "example.com", "domain.com",
                "email.com", "youremail.com", "gmail.com.au"}

def _clean_email(email: str) -> str | None:
    domain = email.split("@")[-1].lower()
    if domain in SKIP_DOMAINS:
        return None
    if any(ext in domain for ext in [".png", ".jpg", ".gif", ".svg", ".css", ".js"]):
        return None
    if len(email) > 80:
        return None
    return email

def find_email_on_website(url: str) -> str:
    if not url:
        return "No Website"
    if any(x in url for x in ["facebook.com", "instagram.com", "twitter.com", "youtube.com"]):
        return "Social Media Only"
    if not url.startswith("http"):
        url = "https://" + url

    headers = {"User-Agent": USER_AGENT}
    pages_to_check = [
        url,
        url.rstrip("/") + "/contact",
        url.rstrip("/") + "/contact-us",
        url.rstrip("/") + "/about",
    ]

    for page_url in pages_to_check:
        try:
            resp = requests.get(page_url, timeout=REQUEST_TO, headers=headers, allow_redirects=True)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            # Priority 1: mailto links
            for a in soup.find_all("a", href=True):
                if a["href"].startswith("mailto:"):
                    candidate = a["href"][7:].split("?")[0].strip()
                    cleaned = _clean_email(candidate)
                    if cleaned:
                        return cleaned

            # Priority 2: regex on visible text only (avoids JS noise)
            text = soup.get_text(separator=" ")
            for m in EMAIL_RE.findall(text):
                cleaned = _clean_email(m)
                if cleaned:
                    return cleaned

        except requests.exceptions.Timeout:
            return "Site Timeout"
        except Exception:
            pass

    return "Not Found"


# ──────────────────────────────────────────────
# GOOGLE MAPS SCRAPER  (robust multi-selector approach)
# ──────────────────────────────────────────────

def _get_text(page, selectors: list[str], timeout=3000) -> str:
    """Try multiple CSS selectors and return the first match's text."""
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                text = loc.inner_text(timeout=timeout).strip()
                if text:
                    return text
        except Exception:
            pass
    return ""

def _get_attr(page, selectors: list[str], attr: str, timeout=3000) -> str:
    """Try multiple CSS selectors and return the first match's attribute."""
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                val = loc.get_attribute(attr, timeout=timeout)
                if val:
                    return val.strip()
        except Exception:
            pass
    return ""


def scrape_google_maps(page, search_query: str) -> list[dict]:
    results = []
    seen = set()

    url = "https://www.google.com/maps/search/" + search_query.replace(" ", "+")
    log.info("🔍 Searching: %s", search_query)

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=40_000)
        time.sleep(4)
    except PlaywrightTimeout:
        log.warning("⚠️  Page load timed out — skipping.")
        return results

    # Dismiss consent / cookie dialogs
    for label in ["Accept all", "Accept", "Reject all", "I agree", "Agree"]:
        try:
            btn = page.get_by_role("button", name=re.compile(label, re.I))
            if btn.count() > 0:
                btn.first.click(timeout=2000)
                time.sleep(1)
                break
        except Exception:
            pass

    # Wait for the results feed
    feed_selectors = ['div[role="feed"]', 'div[aria-label*="Results"]', 'div[aria-label*="result"]']
    feed_found = False
    for sel in feed_selectors:
        try:
            page.wait_for_selector(sel, timeout=12_000)
            feed_found = True
            feed_sel = sel
            break
        except PlaywrightTimeout:
            pass

    if not feed_found:
        log.warning("⚠️  No results feed found for: %s", search_query)
        # Debug: print how many place links exist anyway
        place_links = page.locator('a[href*="/maps/place/"]').all()
        log.info("   (Found %d raw place links without feed)", len(place_links))
        if not place_links:
            return results
        feed_sel = None  # proceed without feed scrolling

    # Scroll to load all results
    if feed_sel:
        for i in range(MAX_SCROLLS):
            page.locator(feed_sel).evaluate("el => el.scrollBy(0, 1000)")
            time.sleep(SCROLL_PAUSE)
            if page.locator("text=/end of the list/i").count() > 0:
                log.info("   Reached end of list after %d scrolls.", i + 1)
                break

    # Collect all place links (cards)
    # Use a broader selector to catch all result anchors
    all_links = page.locator('a[href*="/maps/place/"]').all()
    log.info("   Found %d place links.", len(all_links))

    for idx, link in enumerate(all_links):
        try:
            # Get the name from aria-label or inner text
            name = (
                link.get_attribute("aria-label", timeout=2000) or
                link.inner_text(timeout=2000) or ""
            ).strip()

            # Skip non-place links (navigation arrows, etc.)
            if not name or len(name) < 3:
                continue
            if name in seen:
                continue

            # Click to open detail panel
            link.click(timeout=6000)
            time.sleep(3)

            # ── Name (from detail panel, more accurate) ──
            detail_name = _get_text(page, [
                'h1.fontHeadlineLarge',
                'h1[class*="fontHeadline"]',
                'h1[class*="DUwDvf"]',
                'h1',
            ])
            name = detail_name or name
            if name in seen:
                continue
            seen.add(name)

            # ── Address ──
            address = _get_text(page, [
                'button[data-item-id="address"]',
                '[data-item-id="address"]',
                'button[aria-label*="Address"]',
                '[data-tooltip="Copy address"]',
            ])

            # Fallback: look for address in the page source via regex
            if not address:
                try:
                    content = page.content()
                    addr_match = re.search(r'"formatted_address":"([^"]+)"', content)
                    if addr_match:
                        address = addr_match.group(1)
                except Exception:
                    pass

            # ── Website ──
            website = _get_attr(page, [
                'a[data-item-id="authority"]',
                'a[aria-label*="website" i]',
                'a[href*="http"]:not([href*="google"]):not([href*="maps"])',
            ], "href")

            # Unwrap Google redirect
            if website and "google.com/url" in website:
                m = re.search(r"[?&]q=([^&]+)", website)
                if m:
                    website = unquote(m.group(1))

            # ── Email on Maps (rare) ──
            email_raw = ""
            try:
                mailto = page.locator('a[href^="mailto:"]').first
                if mailto.count() > 0:
                    href = mailto.get_attribute("href", timeout=2000) or ""
                    email_raw = href.replace("mailto:", "").split("?")[0].strip()
            except Exception:
                pass

            results.append({
                "name":      name,
                "address":   address,
                "website":   website,
                "email_raw": email_raw,
            })
            log.info("   ✅ [%d] %s", len(results), name)

        except PlaywrightTimeout:
            log.debug("   Timeout on link %d — skipping.", idx)
        except Exception as e:
            log.debug("   Error on link %d: %s", idx, e)

    return results


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    output_path = Path(OUTPUT_FILE)
    fieldnames  = ["Country", "Name", "Address", "Website", "Email"]

    file_exists = output_path.exists()
    csv_file    = open(output_path, mode="a", newline="", encoding="utf-8")
    writer      = csv.DictWriter(csv_file, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()

    total_saved = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=HEADLESS,
            args=["--lang=en-US", "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 900},
            locale="en-US",
            timezone_id="America/New_York",
        )
        # Hide webdriver flag
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()

        for country, queries in SEARCH_REGIONS.items():
            log.info("═" * 55)
            log.info("🌍 Country: %s  (%d queries)", country, len(queries))
            log.info("═" * 55)

            for query in queries:
                records = scrape_google_maps(page, query)

                for rec in records:
                    if rec["email_raw"]:
                        email = rec["email_raw"]
                    else:
                        email = find_email_on_website(rec["website"])

                    writer.writerow({
                        "Country": country,
                        "Name":    rec["name"],
                        "Address": rec["address"],
                        "Website": rec["website"],
                        "Email":   email,
                    })
                    csv_file.flush()
                    total_saved += 1
                    log.info(
                        "  💾 #%-4d  %-40s | %-28s | %s",
                        total_saved,
                        rec["name"][:40],
                        (rec["address"] or "No address")[:28],
                        email or "—",
                    )

                log.info("  ✔ Query done. Total saved: %d\n", total_saved)

                sleep_for = random.uniform(*SEARCH_DELAY)
                log.info("  ⏳ Sleeping %.1f s …\n", sleep_for)
                time.sleep(sleep_for)

        browser.close()

    csv_file.close()
    log.info("🎉 Done! %d records saved to %s", total_saved, output_path.resolve())


if __name__ == "__main__":
    main()
\