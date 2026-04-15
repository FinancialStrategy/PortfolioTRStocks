# core/data_loader.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
import yfinance as yf


@dataclass
class LoaderConfig:
    min_history_rows: int = 120
    min_asset_coverage: float = 0.70
    max_forward_fill_days: int = 3


class DataLoader:
    def __init__(
        self,
        tickers: List[str],
        benchmark_ticker: str,
        start_date,
        end_date,
        use_log_returns: bool = False,
        loader_config: LoaderConfig | None = None,
    ):
        self.tickers = list(dict.fromkeys(tickers))
        self.benchmark_ticker = benchmark_ticker
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.use_log_returns = use_log_returns
        self.loader_config = loader_config or LoaderConfig()

    def load_market_data(self) -> Dict:
        all_tickers = list(dict.fromkeys(self.tickers + [self.benchmark_ticker]))

        raw = yf.download(
            tickers=all_tickers,
            start=self.start_date,
            end=self.end_date,
            auto_adjust=True,
            progress=False,
            group_by="ticker",
            threads=True,
        )

        if raw is None or len(raw) == 0:
            raise ValueError("Yahoo Finance returned no data.")

        ohlcv_map = self._extract_ohlcv_map(raw, all_tickers)
        price_df = self._extract_close_prices(ohlcv_map)

        requested_prices = price_df[[c for c in self.tickers if c in price_df.columns]].copy()
        benchmark_prices = price_df[[c for c in [self.benchmark_ticker] if c in price_df.columns]].copy()

        cleaned_prices = self._clean_price_matrix(requested_prices)
        if cleaned_prices.empty or cleaned_prices.shape[0] < self.loader_config.min_history_rows:
            raise ValueError("Insufficient aligned price history after cleaning.")

        valid_tickers = list(cleaned_prices.columns)

        benchmark_prices = benchmark_prices.reindex(cleaned_prices.index).ffill(limit=self.loader_config.max_forward_fill_days)
        benchmark_prices = benchmark_prices.dropna(how="all")

        returns = self._price_to_returns(cleaned_prices)
        benchmark_returns = self._price_to_returns(benchmark_prices) if not benchmark_prices.empty else pd.DataFrame()

        current_prices = cleaned_prices.iloc[-1]

        filtered_ohlcv = {}
        for t in valid_tickers:
            if t in ohlcv_map:
                x = ohlcv_map[t].copy()
                x = x[~x.index.duplicated(keep="last")]
                x = x.sort_index()
                x = x.loc[x.index.intersection(cleaned_prices.index)]
                filtered_ohlcv[t] = x

        return {
            "prices": cleaned_prices,
            "returns": returns,
            "benchmark_prices": benchmark_prices,
            "benchmark_returns": benchmark_returns,
            "current_prices": current_prices,
            "valid_tickers": valid_tickers,
            "ohlcv_map": filtered_ohlcv,
        }

    def _extract_ohlcv_map(self, raw: pd.DataFrame, tickers: list[str]) -> Dict[str, pd.DataFrame]:
        out = {}

        if isinstance(raw.columns, pd.MultiIndex):
            for t in tickers:
                if t in raw.columns.get_level_values(0):
                    sub = raw[t].copy()
                    cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in sub.columns]
                    if len(cols) >= 4:
                        sub = sub[cols].copy()
                        sub = sub.dropna(how="all")
                        out[t] = sub
        else:
            cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in raw.columns]
            if cols and len(tickers) == 1:
                out[tickers[0]] = raw[cols].copy()

        return out

    def _extract_close_prices(self, ohlcv_map: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        frames = []
        for t, df in ohlcv_map.items():
            if "Close" in df.columns:
                s = pd.to_numeric(df["Close"], errors="coerce").rename(t)
                frames.append(s)
        if not frames:
            return pd.DataFrame()
        out = pd.concat(frames, axis=1)
        out = out.sort_index()
        out = out[~out.index.duplicated(keep="last")]
        return out

    def _clean_price_matrix(self, prices: pd.DataFrame) -> pd.DataFrame:
        df = prices.copy()

        for c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna(how="all")
        df = df[~df.index.duplicated(keep="last")]
        df = df.sort_index()

        if df.empty:
            return pd.DataFrame()

        coverage = df.notna().mean()
        keep_cols = coverage[coverage >= self.loader_config.min_asset_coverage].index.tolist()
        df = df[keep_cols]

        if df.empty:
            return pd.DataFrame()

        df = df.ffill(limit=self.loader_config.max_forward_fill_days)
        df = df.dropna(how="all")

        aligned = df.dropna(how="any")

        if aligned.shape[0] < self.loader_config.min_history_rows:
            aligned = self._relaxed_alignment(df)

        aligned = aligned[~aligned.index.duplicated(keep="last")]
        aligned = aligned.sort_index()

        final_cols = []
        for c in aligned.columns:
            s = aligned[c].dropna()
            if len(s) >= self.loader_config.min_history_rows and s.nunique() > 1:
                final_cols.append(c)

        aligned = aligned[final_cols]
        aligned = aligned.dropna(how="any")

        return aligned

    def _relaxed_alignment(self, df: pd.DataFrame) -> pd.DataFrame:
        coverage = df.notna().mean().sort_values(ascending=False)
        ranked = coverage.index.tolist()
        best = pd.DataFrame()

        for k in range(len(ranked), 0, -1):
            subset = ranked[:k]
            candidate = df[subset].dropna(how="any")
            if candidate.shape[0] >= self.loader_config.min_history_rows:
                return candidate
            if candidate.shape[0] > best.shape[0]:
                best = candidate

        return best

    def _price_to_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        if prices is None or prices.empty:
            return pd.DataFrame()

        if self.use_log_returns:
            ret = np.log(prices / prices.shift(1))
            ret = np.exp(ret) - 1.0
        else:
            ret = prices.pct_change()

        ret = ret.replace([np.inf, -np.inf], np.nan)
        ret = ret.dropna(how="all")

        keep_cols = []
        for c in ret.columns:
            s = ret[c].dropna()
            if len(s) > 1 and s.nunique() > 1:
                keep_cols.append(c)

        ret = ret[keep_cols] if keep_cols else pd.DataFrame(index=ret.index)
        ret = ret.dropna(how="any")
        return ret
