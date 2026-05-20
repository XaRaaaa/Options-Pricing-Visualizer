"""Lightweight FastAPI backend shell for Options Pricing Visualizer.

This file provides minimal, well-typed endpoints used during the
early development hours (Day 1 / Hour 2-4). It intentionally returns
stubbed values so frontend wiring can proceed while the pricing
engine and external integrations are implemented in later commits.
"""

from typing import Dict, List, Optional

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class OptionParams(BaseModel):
    spot: float = Field(..., gt=0)
    strike: float = Field(..., gt=0)
    rate: float = Field(..., ge=-1, le=1)
    vol: float = Field(..., gt=0)
    time: float = Field(..., gt=0)
    dividend: float = Field(0.0, ge=-1, le=1)
    option_type: str = Field("call")


class CurveParams(BaseModel):
    spot_min: float = Field(..., gt=0)
    spot_max: float = Field(..., gt=0)
    points: int = Field(60, ge=10, le=500)


class HistoryParams(BaseModel):
    symbol: str = Field("AAPL", min_length=1, max_length=16)
    outputsize: str = Field("compact")


class OptionsParams(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)
    expiration: Optional[str] = None


app = FastAPI(title="Options Pricing Visualizer API", version="0.1.0")

# Configure CORS origins from env (defaults to Vite dev origin)
raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
allow_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> Dict[str, str]:
    """Health check for the API."""
    return {"status": "ok"}


@app.post("/api/price")
def price(params: OptionParams) -> Dict[str, float]:
    """Stub price endpoint returning mock values for early UI wiring."""
    option_type = params.option_type.lower()
    if option_type not in {"call", "put"}:
        raise HTTPException(status_code=400, detail="option_type must be call or put")

    # Return deterministic stub values so frontend can render immediately
    return {
        "option_type": option_type,  # type: ignore[return-value]
        "price": 0.0,
        "delta": 0.0,
        "gamma": 0.0,
        "vega": 0.0,
        "theta": 0.0,
        "rho": 0.0,
    }


@app.post("/api/curve")
def curve(params: CurveParams) -> Dict[str, List[Dict[str, float]]]:
    """Return a simple line for curve plotting in the early UI.

    This stub returns `points` with evenly spaced `spot` values and
    zeroed y-values. Full curve computation will be added later.
    """
    spot_min = min(params.spot_min, params.spot_max)
    spot_max = max(params.spot_min, params.spot_max)
    if spot_max == spot_min:
        spot_max = spot_min * 1.01

    step = (spot_max - spot_min) / max(1, params.points - 1)
    points = []
    for i in range(params.points):
        s = spot_min + i * step
        points.append({"spot": float(s), "value": 0.0})

    return {"greek": "delta", "points": points}


@app.post("/api/history")
def history(params: HistoryParams) -> Dict[str, object]:
    """History endpoint placeholder. Full integration added in later commits."""
    raise HTTPException(status_code=501, detail="history endpoint not implemented yet")


@app.post("/api/options")
def options(params: OptionsParams) -> Dict[str, object]:
    """Options endpoint placeholder for later integration."""
    raise HTTPException(status_code=501, detail="options endpoint not implemented yet")
import json
import math
"""Backend API shell for Options Pricing Visualizer.

This is an intentionally small FastAPI application providing the
initial endpoints used during early development. It contains
lightweight stubs so the frontend can be wired before the full
pricing engine is implemented.
"""

import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class OptionParams(BaseModel):
    spot: float = Field(..., gt=0)
    strike: float = Field(..., gt=0)
    rate: float = Field(..., ge=-1, le=1)
    vol: float = Field(..., gt=0)
    time: float = Field(..., gt=0)
    dividend: float = Field(0.0, ge=-1, le=1)
    option_type: str = Field("call")


class CurveParams(BaseModel):
    spot_min: float = Field(..., gt=0)
    spot_max: float = Field(..., gt=0)
    points: int = Field(60, ge=10, le=500)


class OptionsParams(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)
    expiration: Optional[str] = None


app = FastAPI(title="Options Pricing Visualizer API", version="0.1.0")

# Configure CORS origins from env (defaults to Vite dev origin)
raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
allow_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    """Health check for the API."""
    return {"status": "ok"}


@app.post("/api/price")
def price(params: OptionParams) -> dict:
    """Stub price endpoint.

    Returns a minimal response so the frontend can render values
    while the real pricing engine is implemented in subsequent
    commits.
    """
    option_type = params.option_type.lower()
    if option_type not in {"call", "put"}:
        raise HTTPException(status_code=400, detail="option_type must be call or put")

    # Minimal mock values for early integration tests
    return {
        "option_type": option_type,
        "price": 0.0,
        "delta": 0.0,
        "gamma": 0.0,
        "vega": 0.0,
        "theta": 0.0,
        "rho": 0.0,
    }


@app.post("/api/curve")
def curve(params: CurveParams) -> dict:
    """Return a simple line for curve plotting in the early UI.

    This stub returns `points` with evenly spaced `spot` values and
    zeroed values for the y-axis. The full curve computation will be
    added later.
    """
    spot_min = min(params.spot_min, params.spot_max)
    spot_max = max(params.spot_min, params.spot_max)
    if spot_max == spot_min:
        spot_max = spot_min * 1.01

    step = (spot_max - spot_min) / max(1, params.points - 1)
    points = []
    for i in range(params.points):
        s = spot_min + i * step
        points.append({"spot": float(s), "value": 0.0})

    return {"greek": "delta", "points": points}


@app.post("/api/options")
def options(params: OptionsParams) -> dict:
    """Options endpoint placeholder for later integration."""
    raise HTTPException(status_code=501, detail="options endpoint not implemented yet")



@app.post("/api/history")
def history(params: HistoryParams) -> dict[str, object]:
    """Fetch daily historical prices for a symbol (Alpha Vantage)."""

    outputsize = params.outputsize.lower()
    if outputsize not in {"compact", "full"}:
        raise HTTPException(status_code=400, detail="outputsize must be compact or full")

    symbol = params.symbol.strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol is required")

    return _fetch_alpha_vantage_history(symbol, outputsize)


@app.post("/api/options")
def options(params: OptionsParams) -> dict[str, object]:
    """Fetch option chains for a symbol (Tradier).

    Returns a list of options with key fields for display.
    """
    symbol = params.symbol.strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol is required")

    return _fetch_tradier_options(symbol, expiration=params.expiration)
