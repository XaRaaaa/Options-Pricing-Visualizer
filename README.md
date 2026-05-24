# Options Pricing Visualizer

Interactive options pricing with Black-Scholes and Monte Carlo models with charts.

## Layout
- frontend/ - Vite + React UI with D3.js charts
- backend/ - FastAPI service with JAX

## Run locally
Backend (from root):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (from root):

```bash
cd frontend
npm install
npm run dev
```

Backend: http://localhost:8000
Frontend: http://localhost:5173

## Env vars
Create `backend/.env`:

```bash
POLYGON_API_KEY=your_polygon_api_key
CORS_ORIGINS=http://localhost:5173
```

## API
- POST /api/price
  - body: spot, strike, rate, vol, time, dividend, option_type
  - optional: method, num_paths, seed, antithetic
- POST /api/curve
  - body: spot, strike, rate, vol, time, dividend, option_type, greek, spot_min, spot_max, points
- POST /api/history
  - body: symbol, outputsize
- POST /api/options
  - body: symbol, expiration

## Notes
- Rates are annualized decimals (0.05 = 5%).
- Vega is reported per 1.0 volatility, not per 1%.