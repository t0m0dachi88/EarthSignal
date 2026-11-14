# EarthSignal — Frontend

A React 18 + TypeScript + Vite scientific dashboard built to consume the **EarthSignal Complete Backend** FastAPI contract. Includes a responsive dark scientific UI, overview, precomputed discovery explorer, geographic contrast map, trend investigation charts, regional comparison, evidence inspector, authentication and saved investigations.

## Requirements

- Node.js 20.19+ or 22+
- npm
- EarthSignal FastAPI backend listening on `http://127.0.0.1:8000`

## Windows PowerShell

From `EarthSignal_Frontend`:

```powershell
npm install
npm run dev
```

Open **http://127.0.0.1:5173**.

Vite automatically proxies requests starting `/api` to `http://127.0.0.1:8000`, so no extra frontend environment configuration is required for local use.

To build production static assets:

```powershell
npm run build
```

Output: `dist/`.

## Important API routes

| Frontend view | Backend API |
|---|---|
| Overview | `GET /api/ml/health`, `GET /api/ml/discoveries` |
| Discover | `GET /api/ml/discoveries?variable=&integrated_only=&limit=&offset=` |
| Investigate | `GET /api/trends?cell_id=&variable=` or `?latitude=&longitude=&variable=` |
| Compare | `POST /api/contrasts` |
| Evidence | `GET /api/evidence/{variable}/{cell_a}/{cell_b}` |
| Recommendations | `GET /api/recommendations/{variable}` |
| Sign in | `POST /api/auth/login` |
| Register | `POST /api/auth/register` |
| Workspace | `GET /api/investigations`, `POST /api/investigations` |

## Known limitations

- **The world map is a stylized SVG geographic illustration**, not a GIS basemap; latitude/longitude markers are plotted with equirectangular coordinates. It does not imply precise coastlines or area boundaries. For submission-quality spatial investigation, upgrade to MapLibre with a verified basemap and selectable GLDAS grid cells.
- The frontend does not contain sample scientific measurements or fabricated discoveries. If the backend is unavailable, API-dependent panels show connection errors; the overview's initial aggregate figures are labeled research inventory counts, not live data.
- The frontend does not start the backend or MongoDB Atlas worker. Start those separately.
- Full local npm build was not executed in the authoring environment because npm registry dependencies were inaccessible. Run `npm install && npm run build` locally and report any errors.
- Login token is held in localStorage for MVP convenience. Before public deployment, implement a reviewed session strategy and browser security hardening.

## Folder structure

```
EarthSignal_Frontend/
├── src/
│   ├── App.tsx       # Views, interactions, data visualization
│   ├── api.ts        # Typed API client and schemas
│   ├── main.tsx      # React entry
│   └── styles.css    # Responsive theme
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── .env.example
```

No Docker is needed.


## Leaflet geographic explorer (navy edition)

The overview and discovery maps now use **React Leaflet 4 / Leaflet 1.9** with CARTO dark tiles and OpenStreetMap attribution. Drag to pan, use +/− to zoom, click regional markers or connecting lines to select a discovery, and hover to inspect coordinates and cell IDs. Selection fits the map to the discovery pair. The base tiles require internet access.

The map displays **actual discovery coordinates** from `/api/ml/discoveries`, not a hand-drawn approximation. Markers are limited to the current API result set (30 overview, up to 150 in the discovery view), not all 25,604 cells. Scientific raster/heatmap overlays and arbitrary map-click-to-cell selection require additional geographic API data and are not claimed as implemented.

The interface has been restyled to a restrained modern navy-blue palette. No backend changes or Docker are required.

After replacing an existing frontend, run `npm install` (new Leaflet dependencies) and `npm run dev -- --force`.
