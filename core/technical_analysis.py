 ## core/technical_analysis.py
# core/technical_analysis.py

from __future__ import annotations

import numpy as np
import pandas as pd


def _validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")
    out = df.copy().sort_index()
    out = out[~out.index.duplicated(keep="last")]
    return out


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return pd.DataFrame({
        "macd_line": macd_line,
        "signal_line": signal_line,
        "macd_hist": hist
    })


def bollinger_bands(close: pd.Series, period: int = 20, std_mult: float = 2.0) -> pd.DataFrame:
    mid = close.rolling(period).mean()
    vol = close.rolling(period).std(ddof=1)
    upper = mid + std_mult * vol
    lower = mid - std_mult * vol
    return pd.DataFrame({
        "bb_mid": mid,
        "bb_upper": upper,
        "bb_lower": lower
    })


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    tr = true_range(high, low, close)
    return tr.ewm(alpha=1/period, adjust=False).mean()


def momentum(close: pd.Series, period: int = 20) -> pd.Series:
    return close / close.shift(period) - 1.0


def roc(close: pd.Series, period: int = 12) -> pd.Series:
    return (close - close.shift(period)) / close.shift(period) * 100.0


def enrich_technical_indicators(
    ohlcv: pd.DataFrame,
    rsi_period: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    bollinger_period: int = 20,
    bollinger_std: float = 2.0,
    atr_period: int = 14,
    sma_short: int = 20,
    sma_medium: int = 50,
    sma_long: int = 200,
) -> pd.DataFrame:
    df = _validate_ohlcv(ohlcv)

    df["sma_short"] = sma(df["Close"], sma_short)
    df["sma_medium"] = sma(df["Close"], sma_medium)
    df["sma_long"] = sma(df["Close"], sma_long)

    df["ema_fast"] = ema(df["Close"], macd_fast)
    df["ema_slow"] = ema(df["Close"], macd_slow)

    df["rsi"] = rsi(df["Close"], rsi_period)

    macd_df = macd(df["Close"], macd_fast, macd_slow, macd_signal)
    df = pd.concat([df, macd_df], axis=1)

    bb_df = bollinger_bands(df["Close"], bollinger_period, bollinger_std)
    df = pd.concat([df, bb_df], axis=1)

    df["atr"] = atr(df["High"], df["Low"], df["Close"], atr_period)
    df["momentum_20"] = momentum(df["Close"], 20)
    df["roc_12"] = roc(df["Close"], 12)

    return df


def technical_signal_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    score = pd.Series(0.0, index=out.index)

    score += np.where(out["Close"] > out["sma_short"], 1.0, -1.0)
    score += np.where(out["sma_short"] > out["sma_medium"], 1.0, -1.0)
    score += np.where(out["sma_medium"] > out["sma_long"], 1.0, -1.0)

    score += np.where(out["rsi"] < 30, 1.0, 0.0)
    score += np.where(out["rsi"] > 70, -1.0, 0.0)

    score += np.where(out["macd_line"] > out["signal_line"], 1.0, -1.0)
    score += np.where(out["macd_hist"] > 0, 0.5, -0.5)

    score += np.where(out["Close"] < out["bb_lower"], 1.0, 0.0)
    score += np.where(out["Close"] > out["bb_upper"], -1.0, 0.0)

    score += np.where(out["momentum_20"] > 0, 1.0, -1.0)

    out["signal_score"] = score

    out["signal_label"] = np.select(
        [
            out["signal_score"] >= 4,
            (out["signal_score"] >= 1) & (out["signal_score"] < 4),
            (out["signal_score"] > -1) & (out["signal_score"] < 1),
            (out["signal_score"] <= -1) & (out["signal_score"] > -4),
            out["signal_score"] <= -4,
        ],
        [
            "Strong Bullish",
            "Bullish",
            "Neutral",
            "Bearish",
            "Strong Bearish",
        ],
        default="Neutral",
    )

    return out


def latest_technical_snapshot(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        raise ValueError("Technical analysis DataFrame is empty.")
    return df.iloc[-1]
