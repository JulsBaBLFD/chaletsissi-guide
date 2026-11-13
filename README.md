# Gästemappe Chalets Sissi

Live: **https://guide.chaletsissi.com**

## Neue Version veröffentlichen (für Simon & Julian)

1. Gästemappe wie gewohnt im Claude-Artefakt ändern und die HTML-Datei herunterladen.
2. Hier im Repo den Ordner **`quelle`** öffnen.
3. **Add file → Upload files** → die heruntergeladene HTML-Datei hineinziehen → **Commit changes**.
4. Fertig. Nach ca. 2 Minuten ist die neue Version online. Den Fortschritt siehst du oben im Tab **Actions** (grüner Haken = live, rotes X = Fehler, dann Julian Bescheid geben).

Hinweise:
- Es wird immer die **zuletzt hochgeladene** HTML-Datei in `quelle/` verwendet. Am besten jedes Mal denselben Dateinamen verwenden (`Chalets_Sissi_Website.html`), dann wird die alte Datei einfach ersetzt.
- Der Vorschau-Modus im Artefakt kann an bleiben – beim Veröffentlichen werden die Bestellungen automatisch scharf geschaltet.
- Bitte **nicht** direkt an anderen Dateien arbeiten. Die Seite wird bei jedem Upload komplett neu aus der HTML-Datei gebaut.

## Was beim Bauen passiert (`tools/`)

- `extract.py` – eingebettete Bilder und Schriften als eigene Dateien auslagern (Seite lädt schneller)
- `finalize.py` – SEO (Titel, Beschreibung, Vorschaubild, strukturierte Daten), Deutsch für Suchmaschinen, Bestellungen live schalten
- `extras.py` – Icons, Vorschaubild, `sitemap.xml`, `robots.txt`
- `static/og-image.jpg` – Vorschaubild für WhatsApp/Google (1200×630). Zum Ändern einfach durch ein neues JPEG mit gleichem Namen ersetzen.

Veröffentlicht wird über GitHub Actions (`.github/workflows/build.yml`). Domain: Strato, Subdomain `guide` → CNAME `julsbablfd.github.io`.
