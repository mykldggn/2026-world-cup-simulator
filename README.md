# 2026 World Cup Simulator

Full-stack World Cup simulator built around the expanded 48-team, 104-match 2026 format.

It combines a FastAPI backend, a custom hybrid rating engine, and a browser dashboard that lets you run Monte Carlo tournaments, inspect qualification odds, and view a sample knockout bracket.

## What it does

- Simulates the full tournament structure: 12 groups of four, top two plus eight best third-place teams, then a Round of 32 through the final.
- Scores matches with a custom power model anchored to the latest confirmed FIFA ranking snapshot, then shaped by attack, midfield, defense, keeper strength, recent form, and optional host advantage.
- Runs repeated tournament simulations to estimate title odds, group survival odds, quarterfinal/semifinal probabilities, and likely final matchups.
- Produces a sample bracket from the same model so the dashboard feels like a real tournament room instead of a raw probability table.
- Adds federation crest marks, national flags, ranking context, and deployment-ready project structure for portfolio and demo use.

## Stack

- Backend: FastAPI
- Frontend: HTML, CSS, vanilla JavaScript
- Modeling: custom Python simulation engine using Monte Carlo tournament runs

## Project structure

```text
2026 World Cup Simulator/
├── app/
│   ├── data.py
│   ├── main.py
│   ├── models.py
│   ├── simulator.py
│   └── static/
│       ├── assets/
│       │   └── federations/
│       ├── app.js
│       ├── index.html
│       └── styles.css
├── api/
│   └── index.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── Procfile
├── railway.toml
├── tests/
│   └── test_simulator.py
├── vercel.json
├── requirements.txt
└── README.md
```

## Data inputs

- Tournament field and final 12 groups reflect the confirmed 2026 World Cup lineup.
- Ranking anchor uses the FIFA Men's World Ranking snapshot dated `2026-04-01`.
- The simulator blends that ranking anchor with hand-tuned line strengths so the model can still express tactical shape instead of acting like a pure ladder lookup.

## How the model works

The simulator does not depend on `scikit-learn`. Instead, it uses a custom hybrid power score and a Monte Carlo engine:

1. Each team gets a baseline profile:
   - FIFA ranking anchor
   - squad rating prior
   - attack
   - midfield
   - defense
   - keeper
   - recent form
   - host flag
2. Match-level expected goals are derived from strength edges, tactical balance, and scenario volatility.
3. Goals are sampled from a Poisson process.
4. Group tables are ranked with points, head-to-head mini-table logic, goal difference, goals scored, and pre-tournament power as the final fallback.
5. Third-place teams are ranked across groups and dynamically assigned into the Round of 32 without same-group rematches against seeded group winners.

## Visual layer

- Team rows and bracket entries include bundled federation crest assets plus national flag assets.
- The dashboard surfaces FIFA rank, ranking anchor, power score, qualification odds, and sample bracket output in one view.
- The UI is designed to feel like a tournament operations desk rather than a notebook wrapper.

## Scenarios

- `Balanced`: baseline setting
- `Chalk`: lowers upset noise and rewards stronger teams
- `Chaos`: increases volatility and dark-horse behavior

## Run locally

```bash
cd "/Users/michaelduggan/Desktop/VSCode/2026 World Cup Simulator"
python3 -m uvicorn app.main:app --reload --port 8026
```

Then open:

```text
http://127.0.0.1:8026
```

## Test

```bash
cd "/Users/michaelduggan/Desktop/VSCode/2026 World Cup Simulator"
python3 -m unittest discover -s tests
```

## API

- `GET /api/health`
- `GET /api/metadata`
- `POST /api/simulate`

Example payload:

```json
{
  "iterations": 600,
  "scenario": "balanced",
  "hostAdvantage": true,
  "featuredTeam": "USA"
}
```

## Deployment prep

### GitHub

- Local repo structure is ready for `git init`, push, and pull-request workflow.
- GitHub Actions CI is included at `.github/workflows/ci.yml`.

### Vercel

- `api/index.py` exposes the ASGI app.
- `vercel.json` routes all requests through the FastAPI entrypoint.

### Railway

- `Procfile` and `railway.toml` are included.
- Health check is set to `/api/health`.

## Good next extensions

- Replace the line-strength priors with a learned pipeline from Elo, xG differential, squad age curves, or event-level match data.
- Add per-team injury toggles and lineup downgrades.
- Add venue-by-venue travel fatigue and climate effects.
- Save simulation runs and compare scenarios side by side.
- Add penalty shootout specialist weighting and set-piece danger features.
