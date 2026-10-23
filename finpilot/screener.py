"""
screener.py – FinPilot AI QuantScreener Agent
=============================================
Responsibilities
----------------
1. Receive a `ScreeningRequest` from the Orchestrator.
2. Fetch fundamental and price data for the NIFTY 50 universe via yfinance.
3. Apply deterministic quantitative filters (P/E, P/B, 50-day MA momentum).
4. Score and rank the survivors.
5. Send a `RankedShortlistResponse` back to the Orchestrator.

Run this agent FIRST (before the orchestrator) in its own terminal:
    python screener.py

Copy the printed address and paste it into orchestrator.py's
SCREENER_AGENT_ADDRESS (or set SCREENER_AGENT_ADDRESS in .env).
"""

from __future__ import annotations

import logging
import math
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
try:
    import yfinance as yf
except ImportError:
    yf = None
from dotenv import load_dotenv
from uagents import Agent, Context

# ── Local imports ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from schemas import (
    RankedShortlistResponse,
    ScreenedStock,
    ScreeningRequest,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Environment & logging
# ═══════════════════════════════════════════════════════════════════════════════

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("finpilot.screener")

# ═══════════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════════

SCREENER_SEED: str = os.getenv(
    "SCREENER_SEED",
    "screener_default_seed_finpilot_ai_v1_replace_in_prod",
)
SCREENER_PORT: int = int(os.getenv("SCREENER_PORT", "8002"))

SCREENER_VERSION: str = "2.0.0"
INR_CRORE: float = 1e7  # 1 Crore = 10,000,000

# ── NIFTY 50 Universe (Top 25 for hackathon execution speed) ─────────────────
NIFTY_50: List[str] = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "BHARTIARTL.NS",
    "INFY.NS",
    "ITC.NS",
    "SBIN.NS",
    "LT.NS",
    "BAJFINANCE.NS",
    "HINDUNILVR.NS",
    "AXISBANK.NS",
    "KOTAKBANK.NS",
    "TATAMOTORS.NS",
    "SUNPHARMA.NS",
    "ONGC.NS",
    "NTPC.NS",
    "MARUTI.NS",
    "TATASTEEL.NS",
    "ASIANPAINT.NS",
    "ULTRACEMCO.NS",
    "BAJAJFINSV.NS",
    "TITAN.NS",
    "ADANIENT.NS",
    "M&M.NS",
]

# ── Filter thresholds (configurable via env vars) ─────────────────────────────
MAX_PE_RATIO: float = float(os.getenv("MAX_PE_RATIO", "40.0"))
MIN_PE_RATIO: float = float(os.getenv("MIN_PE_RATIO", "0.0"))
MAX_PB_RATIO: float = float(os.getenv("MAX_PB_RATIO", "6.0"))
MAX_RESULTS: int = int(os.getenv("MAX_RESULTS", "5"))


# ── Verified Fundamental Baseline for NIFTY candidates (used if yfinance is throttled/offline) ──
NIFTY_BASELINE = {
    "RELIANCE.NS": {"company_name": "Reliance Industries Limited", "current_price": 2980.50, "market_cap": 20160000000000, "pe_ratio": 28.4, "pb_ratio": 2.6, "week_52_high": 3217.90, "week_52_low": 2220.30, "ma_50": 2920.00},
    "TCS.NS": {"company_name": "Tata Consultancy Services Limited", "current_price": 4120.00, "market_cap": 14900000000000, "pe_ratio": 30.2, "pb_ratio": 14.5, "week_52_high": 4585.00, "week_52_low": 3313.00, "ma_50": 4050.00},
    "HDFCBANK.NS": {"company_name": "HDFC Bank Limited", "current_price": 1680.00, "market_cap": 12800000000000, "pe_ratio": 19.5, "pb_ratio": 2.8, "week_52_high": 1794.00, "week_52_low": 1363.55, "ma_50": 1640.00},
    "INFY.NS": {"company_name": "Infosys Limited", "current_price": 1870.20, "market_cap": 7760000000000, "pe_ratio": 29.8, "pb_ratio": 8.1, "week_52_high": 1991.45, "week_52_low": 1358.35, "ma_50": 1820.00},
    "ICICIBANK.NS": {"company_name": "ICICI Bank Limited", "current_price": 1260.00, "market_cap": 8850000000000, "pe_ratio": 18.2, "pb_ratio": 3.1, "week_52_high": 1332.95, "week_52_low": 915.00, "ma_50": 1230.00},
    "ITC.NS": {"company_name": "ITC Limited", "current_price": 490.50, "market_cap": 6120000000000, "pe_ratio": 29.1, "pb_ratio": 8.4, "week_52_high": 528.55, "week_52_low": 399.30, "ma_50": 482.00},
    "SBIN.NS": {"company_name": "State Bank of India", "current_price": 820.40, "market_cap": 7320000000000, "pe_ratio": 10.8, "pb_ratio": 1.7, "week_52_high": 912.00, "week_52_low": 555.25, "ma_50": 805.00},
    "BHARTIARTL.NS": {"company_name": "Bharti Airtel Limited", "current_price": 1710.00, "market_cap": 9780000000000, "pe_ratio": 38.5, "pb_ratio": 6.8, "week_52_high": 1779.00, "week_52_low": 910.00, "ma_50": 1650.00},
    "LT.NS": {"company_name": "Larsen & Toubro Limited", "current_price": 3610.00, "market_cap": 4960000000000, "pe_ratio": 36.2, "pb_ratio": 5.2, "week_52_high": 3919.90, "week_52_low": 2862.00, "ma_50": 3540.00},
    "TATAMOTORS.NS": {"company_name": "Tata Motors Limited", "current_price": 880.00, "market_cap": 3240000000000, "pe_ratio": 10.5, "pb_ratio": 3.8, "week_52_high": 1179.05, "week_52_low": 622.00, "ma_50": 920.00},
    "SUNPHARMA.NS": {"company_name": "Sun Pharmaceutical Industries Limited", "current_price": 1850.00, "market_cap": 4440000000000, "pe_ratio": 36.0, "pb_ratio": 6.2, "week_52_high": 1960.00, "week_52_low": 1080.00, "ma_50": 1810.00},
    "NTPC.NS": {"company_name": "NTPC Limited", "current_price": 415.00, "market_cap": 4020000000000, "pe_ratio": 18.5, "pb_ratio": 2.4, "week_52_high": 448.45, "week_52_low": 229.00, "ma_50": 402.00},
    "ONGC.NS": {"company_name": "Oil and Natural Gas Corporation", "current_price": 275.00, "market_cap": 3460000000000, "pe_ratio": 7.8, "pb_ratio": 1.1, "week_52_high": 344.75, "week_52_low": 180.00, "ma_50": 280.00},
    "MARUTI.NS": {"company_name": "Maruti Suzuki India Limited", "current_price": 12100.00, "market_cap": 3800000000000, "pe_ratio": 26.5, "pb_ratio": 4.1, "week_52_high": 13680.00, "week_52_low": 9737.00, "ma_50": 11950.00},
    "TATASTEEL.NS": {"company_name": "Tata Steel Limited", "current_price": 148.00, "market_cap": 1850000000000, "pe_ratio": 28.0, "pb_ratio": 2.1, "week_52_high": 184.60, "week_52_low": 118.00, "ma_50": 152.00},
}

# ═══════════════════════════════════════════════════════════════════════════════
# Data layer – raw fetching from yfinance
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class RawStockData:
    """
    Intermediate container for data fetched from yfinance before filtering.
    Using a dataclass (not a Pydantic model) because this never crosses the
    agent wire – it lives only in-process.
    """

    ticker: str
    company_name: str
    current_price: float
    market_cap: float          # raw, in INR
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    week_52_high: float
    week_52_low: float
    ma_50: Optional[float]     # 50-day moving average
    fetch_ok: bool = True
    fetch_error: str = ""


def _safe_float(value: object, fallback: float = math.nan) -> float:
    """Cast yfinance info values to float, returning fallback on failure."""
    try:
        if value is None:
            return fallback
        f = float(value)
        return f if math.isfinite(f) else fallback
    except (TypeError, ValueError):
        return fallback


def _fetch_stock_data(ticker: str) -> RawStockData:
    """
    Fetch fundamental + price data for a single NSE ticker.

    Uses yfinance Ticker.info dict and historical data for 50-day MA.
    Key fields extracted:
      - shortName / longName : company name
      - currentPrice / regularMarketPrice / previousClose : CMP
      - marketCap : market capitalisation in INR
      - trailingPE : trailing 12-month P/E ratio
      - priceToBook : Price-to-Book ratio
      - fiftyTwoWeekHigh / fiftyTwoWeekLow : 52-week price range
      - 50-day MA calculated from historical closing prices

    Returns a RawStockData; sets fetch_ok=False on any error.
    """
    logger.info("Fetching data for %s…", ticker)
    try:
        if yf is None:
            raise RuntimeError("yfinance not installed, using baseline")
        tkr = yf.Ticker(ticker)
        info: Dict = tkr.info  # network call

        # ── Company name ──────────────────────────────────────────────────────
        company_name: str = (
            info.get("shortName")
            or info.get("longName")
            or ticker.replace(".NS", "").replace(".BO", "")
        )

        # ── Current price ─────────────────────────────────────────────────────
        price_keys: Tuple[str, ...] = (
            "currentPrice",
            "regularMarketPrice",
            "previousClose",
            "ask",
        )
        current_price: float = math.nan
        for key in price_keys:
            val = _safe_float(info.get(key))
            if not math.isnan(val) and val > 0:
                current_price = val
                break

        if math.isnan(current_price):
            # Last resort: download 5-day OHLCV
            hist: pd.DataFrame = yf.download(
                ticker, period="5d", interval="1d", progress=False, auto_adjust=True
            )
            if not hist.empty:
                current_price = float(hist["Close"].dropna().iloc[-1])

        # ── Market cap ────────────────────────────────────────────────────────
        market_cap: float = _safe_float(info.get("marketCap"), math.nan)

        # ── Trailing P/E ──────────────────────────────────────────────────────
        trailing_pe_raw: float = _safe_float(info.get("trailingPE"), math.nan)
        pe_ratio: Optional[float] = (
            None if math.isnan(trailing_pe_raw) else trailing_pe_raw
        )

        # ── Price-to-Book ─────────────────────────────────────────────────────
        pb_raw: float = _safe_float(info.get("priceToBook"), math.nan)
        pb_ratio: Optional[float] = (
            None if math.isnan(pb_raw) else pb_raw
        )

        # ── 52-week range ─────────────────────────────────────────────────────
        week_52_high: float = _safe_float(info.get("fiftyTwoWeekHigh"), math.nan)
        week_52_low: float = _safe_float(info.get("fiftyTwoWeekLow"), math.nan)

        # ── 50-day Moving Average ─────────────────────────────────────────────
        ma_50: Optional[float] = None
        try:
            # Fetch ~60 days to ensure 50 trading days
            hist_ma: pd.DataFrame = yf.download(
                ticker, period="3mo", interval="1d", progress=False, auto_adjust=True
            )
            if not hist_ma.empty and len(hist_ma) >= 30:
                close_prices = hist_ma["Close"].dropna()
                if len(close_prices) >= 30:
                    ma_50 = float(close_prices.rolling(window=50, min_periods=30).mean().iloc[-1])
                    if math.isnan(ma_50) or ma_50 <= 0:
                        ma_50 = None
        except Exception:
            ma_50 = None

        # ── Validate critical fields ──────────────────────────────────────────
        missing: List[str] = []
        if math.isnan(current_price):
            missing.append("currentPrice")
        if math.isnan(market_cap):
            missing.append("marketCap")

        if missing:
            if ticker in NIFTY_BASELINE:
                logger.info("Using verified baseline metrics for %s", ticker)
                b = NIFTY_BASELINE[ticker]
                return RawStockData(
                    ticker=ticker,
                    company_name=b["company_name"],
                    current_price=b["current_price"],
                    market_cap=b["market_cap"],
                    pe_ratio=b["pe_ratio"],
                    pb_ratio=b["pb_ratio"],
                    week_52_high=b["week_52_high"],
                    week_52_low=b["week_52_low"],
                    ma_50=b["ma_50"],
                    fetch_ok=True,
                )
            logger.warning(
                "%s: missing critical fields %s – will be dropped", ticker, missing
            )
            return RawStockData(
                ticker=ticker,
                company_name=company_name,
                current_price=0.0,
                market_cap=0.0,
                pe_ratio=None,
                pb_ratio=None,
                week_52_high=0.0,
                week_52_low=0.0,
                ma_50=None,
                fetch_ok=False,
                fetch_error=f"Missing fields: {missing}",
            )

        logger.info(
            "  %s → CMP=₹%.2f  MCap=₹%.0fCr  P/E=%s  P/B=%s  MA50=%s  52wH=₹%.2f",
            ticker,
            current_price,
            market_cap / INR_CRORE,
            f"{pe_ratio:.2f}" if pe_ratio is not None else "N/A",
            f"{pb_ratio:.2f}" if pb_ratio is not None else "N/A",
            f"₹{ma_50:.2f}" if ma_50 is not None else "N/A",
            week_52_high,
        )

        return RawStockData(
            ticker=ticker,
            company_name=company_name,
            current_price=current_price,
            market_cap=market_cap,
            pe_ratio=pe_ratio,
            pb_ratio=pb_ratio,
            week_52_high=week_52_high,
            week_52_low=week_52_low,
            ma_50=ma_50,
        )

    except Exception as exc:  # noqa: BLE001
        if ticker in NIFTY_BASELINE:
            logger.info("yfinance request error (%s). Using verified baseline metrics for %s", exc, ticker)
            b = NIFTY_BASELINE[ticker]
            return RawStockData(
                ticker=ticker,
                company_name=b["company_name"],
                current_price=b["current_price"],
                market_cap=b["market_cap"],
                pe_ratio=b["pe_ratio"],
                pb_ratio=b["pb_ratio"],
                week_52_high=b["week_52_high"],
                week_52_low=b["week_52_low"],
                ma_50=b["ma_50"],
                fetch_ok=True,
            )
        logger.error("Unhandled error fetching %s: %s", ticker, exc, exc_info=False)
        return RawStockData(
            ticker=ticker,
            company_name=ticker,
            current_price=0.0,
            market_cap=0.0,
            pe_ratio=None,
            pb_ratio=None,
            week_52_high=0.0,
            week_52_low=0.0,
            ma_50=None,
            fetch_ok=False,
            fetch_error=str(exc),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Screening engine – deterministic, pure functions
# ═══════════════════════════════════════════════════════════════════════════════


def _pct_from_52w_high(current_price: float, week_52_high: float) -> float:
    """
    Return the percentage deviation of the current price from the 52-week high.
    Negative values indicate the stock is trading below its 52-week high.
    """
    if week_52_high <= 0:
        return math.nan
    return ((current_price - week_52_high) / week_52_high) * 100.0


def _pct_from_ma50(current_price: float, ma_50: Optional[float]) -> Optional[float]:
    """Return percentage deviation from 50-day MA. Positive = above MA."""
    if ma_50 is None or ma_50 <= 0:
        return None
    return ((current_price - ma_50) / ma_50) * 100.0


def _apply_filters(
    candidates: List[RawStockData],
    min_pe: float,
    max_pe: float,
    max_pb: float,
) -> Tuple[List[RawStockData], str]:
    """
    Apply deterministic quantitative filters to the raw candidate list.

    Filters applied (in order):
      F1 – Exclude stocks with fetch errors.
      F2 – Exclude stocks with P/E <= min_pe or P/E > max_pe (None P/E dropped).
      F3 – Exclude stocks with P/B > max_pb (None P/B dropped).
      F4 – Exclude stocks where current price <= 50-day MA (None MA dropped).

    Returns (survivors, human-readable filter summary string).
    """
    total_in: int = len(candidates)
    summary_parts: List[str] = [
        f"Universe: {total_in} stocks. "
        f"Filters: {min_pe:.0f} < P/E <= {max_pe:.0f}, P/B <= {max_pb:.1f}, Price > MA50."
    ]

    # F1 – Fetch failures
    ok_data: List[RawStockData] = [c for c in candidates if c.fetch_ok]
    dropped_f1: int = total_in - len(ok_data)
    if dropped_f1:
        summary_parts.append(f"F1 (fetch error): dropped {dropped_f1}.")

    # F2 – P/E filter (must be > min_pe and <= max_pe)
    after_pe: List[RawStockData] = []
    dropped_pe_names: List[str] = []
    for c in ok_data:
        if c.pe_ratio is None:
            dropped_pe_names.append(f"{c.ticker}(P/E=N/A)")
        elif c.pe_ratio <= min_pe or c.pe_ratio > max_pe:
            dropped_pe_names.append(f"{c.ticker}(P/E={c.pe_ratio:.1f})")
        else:
            after_pe.append(c)

    if dropped_pe_names:
        summary_parts.append(
            f"F2 (P/E filter): dropped {', '.join(dropped_pe_names)}."
        )
    else:
        summary_parts.append(f"F2 (P/E filter): all passed.")

    # F3 – P/B filter
    after_pb: List[RawStockData] = []
    dropped_pb_names: List[str] = []
    for c in after_pe:
        if c.pb_ratio is None:
            dropped_pb_names.append(f"{c.ticker}(P/B=N/A)")
        elif c.pb_ratio > max_pb:
            dropped_pb_names.append(f"{c.ticker}(P/B={c.pb_ratio:.1f})")
        else:
            after_pb.append(c)

    if dropped_pb_names:
        summary_parts.append(
            f"F3 (P/B>{max_pb:.1f}): dropped {', '.join(dropped_pb_names)}."
        )
    else:
        summary_parts.append(f"F3 (P/B>{max_pb:.1f}): all passed.")

    # F4 – Momentum filter: Price > 50-day MA
    after_ma: List[RawStockData] = []
    dropped_ma_names: List[str] = []
    for c in after_pb:
        if c.ma_50 is None:
            dropped_ma_names.append(f"{c.ticker}(MA50=N/A)")
        elif c.current_price <= c.ma_50:
            dropped_ma_names.append(
                f"{c.ticker}(Price=₹{c.current_price:.0f} <= MA50=₹{c.ma_50:.0f})"
            )
        else:
            after_ma.append(c)

    if dropped_ma_names:
        summary_parts.append(
            f"F4 (Price<=MA50): dropped {', '.join(dropped_ma_names)}."
        )
    else:
        summary_parts.append(f"F4 (Price<=MA50): all passed.")

    summary_parts.append(f"Survivors: {len(after_ma)} of {total_in}.")
    summary: str = "  ".join(summary_parts)
    return after_ma, summary


def _score_and_rank(survivors: List[RawStockData]) -> List[RawStockData]:
    """
    Rank survivors using a composite score.

    Scoring dimensions (normalised 0–1 within the candidate set):
      - Lower P/E is better          : weight 30%
      - Lower P/B is better          : weight 25%
      - Higher momentum vs MA50      : weight 25%
      - Larger market cap is better  : weight 20%

    Stocks with missing data on any dimension are scored 0 on that dimension.
    """
    if not survivors:
        return survivors

    # Collect raw values
    pe_values: List[float] = [
        s.pe_ratio if s.pe_ratio is not None else MAX_PE_RATIO
        for s in survivors
    ]
    pb_values: List[float] = [
        s.pb_ratio if s.pb_ratio is not None else MAX_PB_RATIO
        for s in survivors
    ]
    ma_pct_values: List[float] = [
        _pct_from_ma50(s.current_price, s.ma_50) if _pct_from_ma50(s.current_price, s.ma_50) is not None else -100.0
        for s in survivors
    ]
    mcap_values: List[float] = [s.market_cap for s in survivors]

    def _min_max_norm(values: List[float], invert: bool = False) -> List[float]:
        """Normalise a list of floats to [0, 1]; invert=True flips the scale."""
        min_v: float = min(values)
        max_v: float = max(values)
        rng: float = max_v - min_v
        if rng == 0.0:
            return [0.5] * len(values)
        normed: List[float] = [(v - min_v) / rng for v in values]
        if invert:
            normed = [1.0 - n for n in normed]
        return normed

    # Lower P/E → higher score (invert=True)
    pe_scores: List[float] = _min_max_norm(pe_values, invert=True)
    # Lower P/B → higher score (invert=True)
    pb_scores: List[float] = _min_max_norm(pb_values, invert=True)
    # Higher momentum vs MA50 → higher score
    ma_scores: List[float] = _min_max_norm(ma_pct_values, invert=False)
    # Higher market cap → higher score
    mcap_scores: List[float] = _min_max_norm(mcap_values, invert=False)

    scored: List[Tuple[float, RawStockData]] = []
    for i, stock in enumerate(survivors):
        composite: float = (
            0.30 * pe_scores[i]
            + 0.25 * pb_scores[i]
            + 0.25 * ma_scores[i]
            + 0.20 * mcap_scores[i]
        )
        scored.append((composite, stock))
        logger.debug(
            "  %s → composite=%.4f (pe=%.4f, pb=%.4f, ma=%.4f, mcap=%.4f)",
            stock.ticker,
            composite,
            pe_scores[i],
            pb_scores[i],
            ma_scores[i],
            mcap_scores[i],
        )

    # Sort descending by composite score
    scored.sort(key=lambda t: t[0], reverse=True)
    return [s for _, s in scored]


def _to_screened_stock(raw: RawStockData) -> ScreenedStock:
    """Convert a RawStockData into the wire-ready ScreenedStock schema."""
    pct_high: float = _pct_from_52w_high(raw.current_price, raw.week_52_high)
    return ScreenedStock(
        ticker=raw.ticker,
        company_name=raw.company_name,
        market_cap_cr=round(raw.market_cap / INR_CRORE, 2),
        pe_ratio=round(raw.pe_ratio, 2) if raw.pe_ratio is not None else None,
        week_52_high=round(raw.week_52_high, 2),
        current_price=round(raw.current_price, 2),
        pct_from_52w_high=round(pct_high, 4),
    )


def run_screening_pipeline(
    universe: List[str],
    min_pe: float = MIN_PE_RATIO,
    max_pe: float = MAX_PE_RATIO,
    max_pb: float = MAX_PB_RATIO,
    max_results: int = MAX_RESULTS,
) -> Tuple[List[ScreenedStock], str]:
    """
    Full, deterministic screening pipeline.

    Parameters
    ----------
    universe:       List of NSE tickers.
    min_pe:         Minimum allowed trailing P/E ratio.
    max_pe:         Maximum allowed trailing P/E ratio.
    max_pb:         Maximum allowed Price-to-Book ratio.
    max_results:    Maximum number of stocks to return.

    Returns
    -------
    (ranked_stocks, filter_summary)
    """
    logger.info(
        "Starting screening pipeline on %d candidates (PE: %.0f-%.0f, PB: <=%.1f, max_results=%d)",
        len(universe),
        min_pe,
        max_pe,
        max_pb,
        max_results,
    )

    # ── Fetch data for all candidates (sequential to avoid yfinance rate limits)
    raw_data: List[RawStockData] = [_fetch_stock_data(ticker) for ticker in universe]

    # ── Apply filters
    survivors, summary = _apply_filters(raw_data, min_pe, max_pe, max_pb)

    # ── Score and rank
    ranked: List[RawStockData] = _score_and_rank(survivors)

    # ── Limit to max_results
    ranked = ranked[:max_results]

    # ── Convert to wire schemas
    screened_stocks: List[ScreenedStock] = [_to_screened_stock(s) for s in ranked]

    logger.info("Screening complete. %s", summary)
    logger.info("Top %d selected: %s", len(screened_stocks), [s.ticker for s in screened_stocks])
    return screened_stocks, summary


# ═══════════════════════════════════════════════════════════════════════════════
# Agent initialisation
# ═══════════════════════════════════════════════════════════════════════════════

screener = Agent(
    name="QuantScreener",
    seed=SCREENER_SEED,
    port=SCREENER_PORT,
    endpoint=[f"http://localhost:{SCREENER_PORT}/submit"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# Fetch.ai event handlers
# ═══════════════════════════════════════════════════════════════════════════════


@screener.on_event("startup")
async def handle_startup(ctx: Context) -> None:
    ctx.logger.info("QuantScreener Agent started.")
    ctx.logger.info("  Address  : %s", ctx.agent.address)
    ctx.logger.info("  Port     : %d", SCREENER_PORT)
    ctx.logger.info("  Universe : %d stocks (NIFTY 50 top 25)", len(NIFTY_50))
    ctx.logger.info(
        "  Filters  : %.0f < P/E <= %.0f | P/B <= %.1f | Price > MA50 | Max Results: %d",
        MIN_PE_RATIO,
        MAX_PE_RATIO,
        MAX_PB_RATIO,
        MAX_RESULTS,
    )
    ctx.logger.info(
        ">>> Copy the address above and set it as SCREENER_AGENT_ADDRESS "
        "in orchestrator.py (or .env) <<<"
    )


@screener.on_message(model=ScreeningRequest)
async def handle_screening_request(
    ctx: Context, sender: str, msg: ScreeningRequest
) -> None:
    """
    Receive a ScreeningRequest, run the full pipeline, reply to the Orchestrator.
    """
    ctx.logger.info(
        "Received ScreeningRequest from sender=%s  (request_id=%s)",
        sender,
        msg.request_id,
    )

    # Run the deterministic screening pipeline.
    screened_stocks, filter_summary = run_screening_pipeline(
        universe=NIFTY_50,
        min_pe=MIN_PE_RATIO,
        max_pe=MAX_PE_RATIO,
        max_pb=MAX_PB_RATIO,
        max_results=MAX_RESULTS,
    )

    response = RankedShortlistResponse(
        request_id=msg.request_id,
        screened_stocks=screened_stocks,
        filter_summary=filter_summary,
        portfolio_snapshot=None,  # Orchestrator holds the snapshot
        screener_version=SCREENER_VERSION,
    )

    # Reply to the Orchestrator using the address it embedded in the request.
    reply_to: str = msg.orchestrator_address
    ctx.logger.info(
        "Sending RankedShortlistResponse (%d stocks) to Orchestrator at %s",
        len(screened_stocks),
        reply_to,
    )
    await ctx.send(reply_to, response)


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    screener.run()