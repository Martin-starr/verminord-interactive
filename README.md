# Verminord Interactive Visualizations

Interactive React-based visualizations for [Verminord AS](https://verminord.com) — vermicompost producer in Klepp Stasjon, Jaeren (Rogaland, Norway).

## Files

| File | Description | URL |
|------|-------------|-----|
| `index.html` | Master combined experience — full narrative from intro to seasonal calendar | `/` |
| `raavarer.html` | The 5 ingredients of VermiCast | `/raavarer` |
| `forkompostering.html` | 6-step pre-composting arc | `/forkompostering` |
| `wedge.html` | Wedge bed cross-section | `/wedge` |
| `cft.html` | Continuous flow-through cross-section | `/cft` |
| `produksjon.html` | 7-stage production pipeline | `/produksjon` |
| `eisenia.html` | Eisenia fetida anatomy with 7 interactive hotspots | `/eisenia` |
| `lab.html` | Lab dashboard — NPK, heavy metals, hygiene, Klasse I certification | `/lab` |
| `bruk.html` | 3 use cases + dosage calculator | `/bruk` |
| `sesong.html` | Circular 12-month seasonal calendar | `/sesong` |

## Tech

- Self-contained HTML files — no build step, no install
- React 18 + Babel Standalone via unpkg.com CDN
- Fraunces + Schibsted Grotesk from Google Fonts
- All content in Norwegian (Bokmal)

## Data Pipeline

A daily sync pulls sensor data from Google Sheets and writes `data.json` for the Storskjerm TV dashboard.

| File | Description |
|------|-------------|
| `data.json` | Live sensor data (9 systems, all time ranges) |
| `mock-data.js` | Offline fallback (`window.VN`) |
| `scripts/sync_sheet.py` | Python sync: Google Sheet → data.json |
| `scripts/apps_script_alternative.gs` | Google Apps Script alternative (no service account needed) |
| `scripts/config.json` | System definitions, column mapping, target ranges |
| `scripts/test_sync.py` | Offline validation (62 checks) |

**Setup (GitHub Action — daily at 06:00):**
1. Create a Google Cloud service account with Sheets API access
2. Share the sheet with the service account email
3. Add GitHub Secrets: `GOOGLE_SHEET_ID`, `GOOGLE_CREDENTIALS_JSON`

**Setup (Apps Script — simpler alternative):**
1. In Google Sheet → Extensions → Apps Script, paste `apps_script_alternative.gs`
2. Set Script Properties: `GITHUB_TOKEN` (repo access), `REPO` (`martin-starr/verminord-interactive`)
3. Add a daily time trigger for `syncToGitHub()`

## Hosting

Hosted on GitHub Pages from `master` branch.

Embedded on verminord.com via Wix iframe elements.

## Deploy

Push to `master` — GitHub Pages auto-deploys. No build command needed.

## License

All rights reserved. Verminord AS.
