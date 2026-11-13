"""Add icons, Open Graph image, sitemap.xml, robots.txt and .nojekyll.

Usage: python3 tools/extras.py <site_dir>
The icons and og-image.jpg are fixed files in tools/static/ (to change the
preview image, replace tools/static/og-image.jpg with a 1200x630 JPEG).
"""
import datetime
import shutil
import sys
from pathlib import Path

site = Path(sys.argv[1])
static = Path(__file__).resolve().parent / "static"
(site / "assets").mkdir(parents=True, exist_ok=True)
for f in static.iterdir():
    shutil.copy2(f, site / "assets" / f.name)

today = datetime.date.today().isoformat()
(site / "sitemap.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://guide.chaletsissi.com/</loc>
    <lastmod>{today}</lastmod>
    <image:image><image:loc>https://guide.chaletsissi.com/assets/og-image.jpg</image:loc></image:image>
  </url>
</urlset>
""", encoding="utf-8")

(site / "robots.txt").write_text("""User-agent: *
Allow: /

Sitemap: https://guide.chaletsissi.com/sitemap.xml
""", encoding="utf-8")

(site / ".nojekyll").write_text("", encoding="utf-8")
print("Zusatzdateien fertig")
