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

## Hosting

Hosted on Netlify with auto-deploy on push to `main`.

- **Current:** `verminord-interactive.netlify.app`
- **Planned:** `interaktiv.verminord.no` (pending DNS access)

Embedded on verminord.com via Wix iframe elements.

## Deploy

Push to `main` — Netlify auto-deploys. No build command needed.

## License

All rights reserved. Verminord AS.
