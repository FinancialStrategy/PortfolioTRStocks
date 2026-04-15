# config.py

from __future__ import annotations

TRADING_DAYS = 252
ROLLING_WINDOW = 63
VAR_CONFIDENCE = 0.95
DEFAULT_RISK_FREE_RATE = 0.35   # TR-friendly placeholder, user-adjustable in UI
DEFAULT_TAU = 0.05
DEFAULT_NUM_SIMULATIONS = 10000
DEFAULT_FORECAST_DAYS = 252

DEFAULT_BENCHMARK = "XU100.IS"

# =========================================================
# Major 25 Turkish Stocks
# =========================================================
MAJOR_TURKEY_25 = {
    "AKBNK.IS": {"name": "Akbank", "category": "Bank", "segment": "Major"},
    "ARCLK.IS": {"name": "Arcelik", "category": "Consumer Durables", "segment": "Major"},
    "ASELS.IS": {"name": "Aselsan", "category": "Defense", "segment": "Major"},
    "BIMAS.IS": {"name": "BIM", "category": "Retail", "segment": "Major"},
    "DOHOL.IS": {"name": "Dogan Holding", "category": "Holding", "segment": "Major"},
    "EKGYO.IS": {"name": "Emlak Konut GYO", "category": "Real Estate", "segment": "Major"},
    "ENKAI.IS": {"name": "Enka Insaat", "category": "Construction", "segment": "Major"},
    "EREGL.IS": {"name": "Eregli Demir Celik", "category": "Steel", "segment": "Major"},
    "FROTO.IS": {"name": "Ford Otosan", "category": "Automotive", "segment": "Major"},
    "GARAN.IS": {"name": "Garanti BBVA", "category": "Bank", "segment": "Major"},
    "GUBRF.IS": {"name": "Gubre Fabrikalari", "category": "Chemicals", "segment": "Major"},
    "HALKB.IS": {"name": "Halkbank", "category": "Bank", "segment": "Major"},
    "ISCTR.IS": {"name": "Is Bankasi C", "category": "Bank", "segment": "Major"},
    "KCHOL.IS": {"name": "Koc Holding", "category": "Holding", "segment": "Major"},
    "KOZAL.IS": {"name": "Koza Altin", "category": "Mining", "segment": "Major"},
    "MGROS.IS": {"name": "Migros", "category": "Retail", "segment": "Major"},
    "PETKM.IS": {"name": "Petkim", "category": "Petrochemicals", "segment": "Major"},
    "PGSUS.IS": {"name": "Pegasus", "category": "Airlines", "segment": "Major"},
    "SAHOL.IS": {"name": "Sabanci Holding", "category": "Holding", "segment": "Major"},
    "SISE.IS": {"name": "Sise Cam", "category": "Glass", "segment": "Major"},
    "TCELL.IS": {"name": "Turkcell", "category": "Telecom", "segment": "Major"},
    "THYAO.IS": {"name": "Turkish Airlines", "category": "Airlines", "segment": "Major"},
    "TOASO.IS": {"name": "Tofas", "category": "Automotive", "segment": "Major"},
    "TUPRS.IS": {"name": "Tupras", "category": "Refinery", "segment": "Major"},
    "YKBNK.IS": {"name": "Yapi Kredi", "category": "Bank", "segment": "Major"},
}

# =========================================================
# Mid Cap 20 Turkish Stocks
# =========================================================
MIDCAP_TURKEY_20 = {
    "AEFES.IS": {"name": "Anadolu Efes", "category": "Beverages", "segment": "MidCap"},
    "AKSEN.IS": {"name": "Aksa Enerji", "category": "Energy", "segment": "MidCap"},
    "ALARK.IS": {"name": "Alarko Holding", "category": "Holding", "segment": "MidCap"},
    "CCOLA.IS": {"name": "Coca Cola Icecek", "category": "Beverages", "segment": "MidCap"},
    "CIMSA.IS": {"name": "Cimsa", "category": "Cement", "segment": "MidCap"},
    "DOAS.IS": {"name": "Dogus Otomotiv", "category": "Automotive", "segment": "MidCap"},
    "ENJSA.IS": {"name": "Enerjisa", "category": "Utilities", "segment": "MidCap"},
    "GENIL.IS": {"name": "Gen Ilac", "category": "Pharma", "segment": "MidCap"},
    "INDES.IS": {"name": "Indeks Bilgisayar", "category": "Technology", "segment": "MidCap"},
    "KONTR.IS": {"name": "Kontrolmatik", "category": "Technology", "segment": "MidCap"},
    "MAVI.IS": {"name": "Mavi Giyim", "category": "Retail", "segment": "MidCap"},
    "OTKAR.IS": {"name": "Otokar", "category": "Defense", "segment": "MidCap"},
    "OYAKC.IS": {"name": "Oyak Cimento", "category": "Cement", "segment": "MidCap"},
    "QUAGR.IS": {"name": "Qua Granite", "category": "Industrials", "segment": "MidCap"},
    "SELEC.IS": {"name": "Selcuk Ecza", "category": "Healthcare", "segment": "MidCap"},
    "SMRTG.IS": {"name": "Smart Gunes", "category": "Energy", "segment": "MidCap"},
    "SOKM.IS": {"name": "Sok Marketler", "category": "Retail", "segment": "MidCap"},
    "TAVHL.IS": {"name": "TAV Havalimanlari", "category": "Airports", "segment": "MidCap"},
    "TKFEN.IS": {"name": "Tekfen Holding", "category": "Industrials", "segment": "MidCap"},
    "VESTL.IS": {"name": "Vestel", "category": "Electronics", "segment": "MidCap"},
}

UNIVERSES = {
    "Major 25 Turkish Stocks": MAJOR_TURKEY_25,
    "Mid Cap 20 Turkish Stocks": MIDCAP_TURKEY_20,
}

TECHNICAL_DEFAULTS = {
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bollinger_period": 20,
    "bollinger_std": 2.0,
    "atr_period": 14,
    "sma_short": 20,
    "sma_medium": 50,
    "sma_long": 200,
}

STRATEGY_DEFAULTS = {
    "trend_following_weight": 0.40,
    "mean_reversion_weight": 0.30,
    "momentum_weight": 0.30,
}
