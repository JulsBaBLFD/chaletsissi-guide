"""Turn the extracted artifact HTML into a SEO-ready index.html.

Usage: python3 tools/finalize.py <site_dir>

Tolerant against text changes in the artifact: the SEO head is always added,
old title/description tags are removed wherever they are. Only the order
switch (vorschau) is critical: if the artifact still has `vorschau: true`
after this script, the build fails so guest orders are never silently lost.
"""
import json
import re
import sys
from pathlib import Path

site = Path(sys.argv[1])
s = (site / "index.raw.html").read_text(encoding="utf-8")

BASE = "https://guide.chaletsissi.com/"
TITLE = "Chalets Sissi Mendelpass | Gästemappe, Frühstück, Erlebnisse"
DESC = ("Gästemappe der Chalets Sissi am Mendelpass in Cavareno (Trentino): Frühstück an die Tür "
        "bestellen, Ausflugstipps im Val di Non und alle Infos für deinen Aufenthalt.")
OG_IMG = BASE + "assets/og-image.jpg"


def warn(msg):
    print(f"::warning::{msg}")


ld = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "LodgingBusiness",
            "@id": "https://www.chaletsissi.com/#chalets",
            "name": "Chalets Sissi",
            "url": "https://www.chaletsissi.com/",
            "image": OG_IMG,
            "logo": BASE + "assets/icon-512.png",
            "description": "Drei Chalets am Mendelpass in Cavareno (Trentino), Chalet Queen und Empress mit Panoramasauna.",
            "telephone": "+49 163 4404921",
            "email": "info@chaletsissi.com",
            "checkinTime": "15:00",
            "checkoutTime": "11:00",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Località Genzianella",
                "postalCode": "38011",
                "addressLocality": "Cavareno",
                "addressRegion": "TN",
                "addressCountry": "IT",
            },
            "geo": {"@type": "GeoCoordinates", "latitude": 46.411639, "longitude": 11.209583},
            "sameAs": [
                "https://www.instagram.com/sissichalets/",
                "https://www.facebook.com/sissichalets/",
            ],
        },
        {
            "@type": "WebPage",
            "@id": BASE + "#webpage",
            "url": BASE,
            "name": TITLE,
            "description": DESC,
            "inLanguage": "de",
            "about": {"@id": "https://www.chaletsissi.com/#chalets"},
            "primaryImageOfPage": OG_IMG,
        },
    ],
}

head = f"""
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{BASE}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Chalets Sissi">
<meta property="og:locale" content="de_DE">
<meta property="og:url" content="{BASE}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="{OG_IMG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Gedeckter Tisch im Garten der Chalets Sissi mit Blick auf die Berge">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
"""

# 1. Remove any existing <title> and meta description (the artifact puts them in <body>)
s = re.sub(r"<title>.*?</title>\s*", "", s, count=1, flags=re.S | re.I)
s = re.sub(r'<meta\s+name=["\']?description["\']?[^>]*>\s*', "", s, count=1, flags=re.I)

# 2. <html lang="de"> and the SEO head right after <head>
s, n = re.subn(r"<html\b[^>]*>", '<html lang="de">', s, count=1, flags=re.I)
if not n:
    raise SystemExit("::error::Kein <html>-Tag gefunden")
s = re.sub(r"<meta\s+charset=[^>]*>", "", s, count=1, flags=re.I)
s, n = re.subn(r"<head\b[^>]*>", lambda m: m.group(0) + '<meta charset="utf-8">' + head, s, count=1, flags=re.I)
if not n:
    raise SystemExit("::error::Kein <head>-Tag gefunden")

# 3. German SEO title when the page sets its title via JavaScript
s, n = re.subn(r'document\.title = tr\(("[^"]*")\);',
               lambda m: f'document.title = SPR === "de" ? "{TITLE}" : tr({m.group(1)});', s, count=1)
if not n:
    warn("document.title-Zeile nicht gefunden, Seitentitel kommt nur aus dem <head>")

# 4. Crawlers (Googlebot renders with an English locale) get the German version
anchor = "  if (!k) { const n = (navigator.language"
if anchor in s:
    s = s.replace(anchor, '  if (!k && /bot|crawler|spider|slurp|lighthouse|inspectiontool|facebookexternalhit|whatsapp/i.test(navigator.userAgent || "")) k = "de";\n' + anchor, 1)
else:
    warn("Sprachwahl-Zeile nicht gefunden, Google sieht evtl. die englische Version")

# 5. Live mode: breakfast and firewood orders are really sent (critical)
s = re.sub(r"vorschau:\s*true", "vorschau: false", s)
if re.search(r"vorschau:\s*true", s):
    raise SystemExit("::error::vorschau ist noch true – Bestellungen würden nicht verschickt")
if "vorschau:" not in s:
    warn("Einstellung 'vorschau' nicht gefunden – bitte Bestellversand prüfen")

(site / "index.html").write_text(s, encoding="utf-8")
(site / "index.raw.html").unlink()
print("index.html", len(s.encode("utf-8")), "Bytes")
