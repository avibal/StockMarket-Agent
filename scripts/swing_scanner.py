"""
Swing Opportunity Scanner - Market Pullback Engine
Detects high-probability 2-week swing setups aligned with the Swing Strategy:
- Horizon: Up to 2 weeks (1-10 trading days)
- Target: 1.5% - 2.5% gross profit (median 2.0%)
- Capital: $10,000 USD
- Commission & Tax: IBKR Israel ($5) + Israeli Tax (25%)
- Technical Filters: Price > EMA 200, Pullback 1.5%-8%, Near EMA 20/50/BB, RSI 32-55.
"""

import os
import sys
import json
import argparse
import time
import numpy as np
import pandas as pd
import yfinance as yf

# Ensure local script directory is in sys.path for macro_calendar import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from macro_calendar import get_today_macro_risk

# Ensure Windows PowerShell handles UTF-8 Hebrew characters cleanly
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Major Index / Broad Benchmark ETFs requiring wider structural breathing room
INDEX_ETFS = {"QQQ", "QQQM", "SPY", "IWM", "DIA", "SMH", "XLE", "XLF", "XLK", "SOXX"}

# Curated universe of 60+ highly liquid US leaders & ETFs
UNIVERSE = [
    # Magnificent 7 / Mega-Cap Tech
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA",
    # Semiconductors & Hardware
    "AMD", "AVGO", "QCOM", "TSM", "ARM", "MU", "ASML", "AMAT", "LRCX", "KLAC", "INTC",
    # AI Power, Nuclear & Clean Energy
    "CEG", "VST", "GEV", "NEE", "TLN", "CCJ",
    # High-Growth AI, Cloud & Cyber
    "PLTR", "CRM", "NOW", "ADBE", "SNOW", "PANW", "CRWD", "ORCL", "IBM",
    # Industrials & Aerospace
    "GE", "CAT", "BA", "RTX", "LMT",
    # Consumer Leaders & Retail
    "NFLX", "DIS", "COST", "WMT", "HD", "NKE", "SBUX",
    # Healthcare & Pharma
    "LLY", "NVO", "UNH", "ABBV", "MRK",
    # Financials & Payments
    "JPM", "V", "MA", "BAC", "GS", "MS",
    # Broad Indices & Sectors
    "QQQ", "QQQM", "IWM", "DIA", "SMH", "XLK", "XLE", "XLF"
]

# Mapping of universe stocks to their benchmark sector ETFs for Top-Down RRG Analysis
TICKER_SECTOR_MAP = {
    # Tech & Software
    "AAPL": "XLK", "MSFT": "XLK", "CRM": "XLK", "ADBE": "XLK", "ORCL": "XLK", 
    "NOW": "XLK", "IBM": "XLK", "PLTR": "XLK", "SNOW": "XLK", "PANW": "XLK", "CRWD": "XLK", "XLK": "XLK",
    # Semiconductors
    "NVDA": "SMH", "AMD": "SMH", "AVGO": "SMH", "QCOM": "SMH", "TSM": "SMH", 
    "ARM": "SMH", "MU": "SMH", "ASML": "SMH", "AMAT": "SMH", "LRCX": "SMH", "KLAC": "SMH", "INTC": "SMH", "SMH": "SMH",
    # Consumer Discretionary & Retail
    "AMZN": "XLY", "TSLA": "XLY", "HD": "XLY", "NKE": "XLY", "SBUX": "XLY", "XLY": "XLY",
    # Communication Services
    "GOOGL": "XLC", "META": "XLC", "NFLX": "XLC", "DIS": "XLC", "XLC": "XLC",
    # Consumer Staples
    "COST": "XLP", "WMT": "XLP", "XLP": "XLP",
    # Healthcare & Pharma
    "LLY": "XLV", "NVO": "XLV", "UNH": "XLV", "ABBV": "XLV", "MRK": "XLV", "XLV": "XLV",
    # Financials & Payments
    "JPM": "XLF", "V": "XLF", "MA": "XLF", "BAC": "XLF", "GS": "XLF", "MS": "XLF", "XLF": "XLF",
    # Industrials & Defense
    "GE": "XLI", "CAT": "XLI", "BA": "XLI", "RTX": "XLI", "LMT": "XLI", "XLI": "XLI",
    # Energy, Utilities & AI Power
    "CEG": "XLU", "VST": "XLU", "GEV": "XLI", "NEE": "XLU", "TLN": "XLU", "CCJ": "XLU", "XLE": "XLE", "XLU": "XLU",
    # Broad Indices
    "QQQ": "QQQ", "QQQM": "QQQ", "SPY": "SPY", "IWM": "IWM", "DIA": "DIA", "SOXX": "SMH"
}

SECTOR_ETFS = ["SPY", "XLK", "SMH", "XLY", "XLC", "XLV", "XLF", "XLI", "XLE", "XLU", "XLP"]

def calculate_rrg_quadrants(data_df) -> dict:
    """
    Calculates Relative Rotation Graph (RRG) metrics for major sector ETFs vs SPY:
    - RS-Ratio: 20-day return of Sector relative to SPY (centered at 100)
    - RS-Momentum: 5-day return of Sector relative to SPY (centered at 100)
    Quadrants:
    - Leading (מוביל): RS-Ratio >= 100 and RS-Momentum >= 100
    - Weakening (נחלש): RS-Ratio >= 100 and RS-Momentum < 100
    - Lagging (מפגר): RS-Ratio < 100 and RS-Momentum < 100
    - Improving (משתפר): RS-Ratio < 100 and RS-Momentum >= 100
    """
    rrg_results = {}
    try:
        def get_close(t):
            if isinstance(data_df.columns, pd.MultiIndex):
                if t in data_df.columns.get_level_values(0):
                    return data_df.xs(t, axis=1, level=0)['Close'].dropna()
                elif t in data_df.columns.get_level_values(1):
                    return data_df.xs(t, axis=1, level=1)['Close'].dropna()
            elif t in data_df.columns:
                return data_df[t].dropna()
            return None

        spy_close = get_close("SPY")
        if spy_close is None or len(spy_close) < 25:
            return {}

        spy_ret_20d = ((spy_close.iloc[-1] - spy_close.iloc[-21]) / spy_close.iloc[-21]) * 100
        spy_ret_5d = ((spy_close.iloc[-1] - spy_close.iloc[-6]) / spy_close.iloc[-6]) * 100

        for sec in SECTOR_ETFS:
            if sec == "SPY":
                continue
            sec_close = get_close(sec)
            if sec_close is None or len(sec_close) < 25:
                continue
            
            sec_ret_20d = ((sec_close.iloc[-1] - sec_close.iloc[-21]) / sec_close.iloc[-21]) * 100
            sec_ret_5d = ((sec_close.iloc[-1] - sec_close.iloc[-6]) / sec_close.iloc[-6]) * 100

            rs_ratio = round(100.0 + (sec_ret_20d - spy_ret_20d), 2)
            rs_momentum = round(100.0 + (sec_ret_5d - spy_ret_5d), 2)

            if rs_ratio >= 100.0 and rs_momentum >= 100.0:
                quadrant = "Leading"
                quadrant_hebrew = "מוביל (Leading 🟢)"
                badge_class = "leading"
            elif rs_ratio >= 100.0 and rs_momentum < 100.0:
                quadrant = "Weakening"
                quadrant_hebrew = "נחלש (Weakening 🟡)"
                badge_class = "weakening"
            elif rs_ratio < 100.0 and rs_momentum < 100.0:
                quadrant = "Lagging"
                quadrant_hebrew = "מפגר (Lagging 🔴)"
                badge_class = "lagging"
            else:
                quadrant = "Improving"
                quadrant_hebrew = "משתפר (Improving 🚀)"
                badge_class = "improving"

            rrg_results[sec] = {
                "sector": sec,
                "rs_ratio": rs_ratio,
                "rs_momentum": rs_momentum,
                "quadrant": quadrant,
                "quadrant_hebrew": quadrant_hebrew,
                "badge_class": badge_class
            }
    except Exception as e:
        pass
    return rrg_results

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calculate_atr(df_ticker: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df_ticker['High']
    low = df_ticker['Low']
    close = df_ticker['Close']
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calculate_adx(df_ticker: pd.DataFrame, period: int = 14) -> float:
    """Calculates Wilder's ADX 14 for Market Regime detection (Trend vs Chop)"""
    try:
        high = df_ticker['High']
        low = df_ticker['Low']
        close = df_ticker['Close']
        
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        alpha = 1.0 / period
        atr_smooth = tr.ewm(alpha=alpha, adjust=False).mean()
        plus_di = 100 * (pd.Series(plus_dm, index=df_ticker.index).ewm(alpha=alpha, adjust=False).mean() / (atr_smooth + 1e-9))
        minus_di = 100 * (pd.Series(minus_dm, index=df_ticker.index).ewm(alpha=alpha, adjust=False).mean() / (atr_smooth + 1e-9))
        
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9)
        adx = dx.ewm(alpha=alpha, adjust=False).mean()
        return float(adx.iloc[-1])
    except Exception:
        return 22.0

def calculate_stock_relative_strength(stock_close: pd.Series, spy_close: pd.Series, sec_close: pd.Series = None) -> dict:
    """
    Calculates Stock-Level Relative Strength & Alpha metrics:
    - 20-day Alpha vs SPY (Stock return - SPY return over 20 days)
    - 20-day Alpha vs Sector ETF (Stock return - Sector return over 20 days)
    - Smart Money Absorption Divergence: SPY 5d return <= 0.2% but Stock 5d alpha vs SPY >= +1.2%
    """
    try:
        stock_c = stock_close.dropna()
        spy_c = spy_close.dropna() if spy_close is not None else None
        
        if spy_c is None or len(stock_c) < 25 or len(spy_c) < 25:
            return {
                "alpha_spy_20d": 0.0,
                "alpha_sec_20d": 0.0,
                "status": "Neutral",
                "status_hebrew": "תואמת מדד (Neutral 🟡)",
                "badge_class": "neutral",
                "is_divergence": False
            }

        # Align series by common dates
        common_idx = stock_c.index.intersection(spy_c.index)
        s_c = stock_c.loc[common_idx]
        sp_c = spy_c.loc[common_idx]

        ret_stock_20d = ((s_c.iloc[-1] - s_c.iloc[-21]) / s_c.iloc[-21]) * 100
        ret_spy_20d = ((sp_c.iloc[-1] - sp_c.iloc[-21]) / sp_c.iloc[-21]) * 100
        alpha_spy_20d = round(float(ret_stock_20d - ret_spy_20d), 2)

        # 5-day check for smart money absorption divergence
        ret_stock_5d = ((s_c.iloc[-1] - s_c.iloc[-6]) / s_c.iloc[-6]) * 100
        ret_spy_5d = ((sp_c.iloc[-1] - sp_c.iloc[-6]) / sp_c.iloc[-6]) * 100
        alpha_spy_5d = ret_stock_5d - ret_spy_5d
        is_divergence = bool((ret_spy_5d <= 0.2) and (alpha_spy_5d >= 1.2))

        # Stock vs Sector ratio
        alpha_sec_20d = alpha_spy_20d
        if sec_close is not None and len(sec_close) >= 25:
            sec_c = sec_close.dropna()
            sec_idx = s_c.index.intersection(sec_c.index)
            if len(sec_idx) >= 21:
                ret_sec_20d = ((sec_c.loc[sec_idx].iloc[-1] - sec_c.loc[sec_idx].iloc[-21]) / sec_c.loc[sec_idx].iloc[-21]) * 100
                ret_stock_sec_20d = ((s_c.loc[sec_idx].iloc[-1] - s_c.loc[sec_idx].iloc[-21]) / s_c.loc[sec_idx].iloc[-21]) * 100
                alpha_sec_20d = round(float(ret_stock_sec_20d - ret_sec_20d), 2)

        # Classification
        if alpha_spy_20d > 0 and alpha_sec_20d > 0:
            status = "Dual Leader"
            status_hebrew = "מובילת שוק וסקטור (Dual Alpha 🌟)"
            badge_class = "leader"
        elif alpha_spy_20d > 0:
            status = "Market Outperformer"
            status_hebrew = "מנצחת שוק (Outperformer 🟢)"
            badge_class = "outperformer"
        elif alpha_spy_20d < -2.5 and alpha_sec_20d < -2.5:
            status = "Relative Laggard"
            status_hebrew = "מפגרת יחסית (Laggard 🔴)"
            badge_class = "laggard"
        else:
            status = "Market Neutral"
            status_hebrew = "תואמת מדד (Neutral 🟡)"
            badge_class = "neutral"

        return {
            "alpha_spy_20d": alpha_spy_20d,
            "alpha_sec_20d": alpha_sec_20d,
            "status": status,
            "status_hebrew": status_hebrew,
            "badge_class": badge_class,
            "is_divergence": is_divergence
        }
    except Exception:
        return {
            "alpha_spy_20d": 0.0,
            "alpha_sec_20d": 0.0,
            "status": "Neutral",
            "status_hebrew": "תואמת מדד (Neutral 🟡)",
            "badge_class": "neutral",
            "is_divergence": False
        }

def run_scanner(tickers=None, capital: float = 10000.0, target_gross_pct: float = 2.0, min_score: int = 50, top_n: int = 5):
    macro_risk = get_today_macro_risk()
    tickers_to_scan = tickers or UNIVERSE
    tickers_to_scan = list(set(tickers_to_scan))
    download_list = list(set(tickers_to_scan + SECTOR_ETFS))
    
    # Download 1y data to ensure accurate EMA 200 calculation
    start_time = time.time()
    try:
        data = yf.download(download_list, period="1y", interval="1d", progress=False, group_by="ticker", auto_adjust=True)
    except Exception as e:
        return {"error": f"Failed to download market data: {str(e)}", "candidates": []}
    
    elapsed = time.time() - start_time
    rrg_map = calculate_rrg_quadrants(data)

    def _get_ticker_series(df_data, sym):
        try:
            if isinstance(df_data.columns, pd.MultiIndex):
                if sym in df_data.columns.get_level_values(0):
                    return df_data.xs(sym, axis=1, level=0)['Close'].squeeze().dropna()
                elif sym in df_data.columns.get_level_values(1):
                    return df_data.xs(sym, axis=1, level=1)['Close'].squeeze().dropna()
            elif sym in df_data.columns:
                return df_data[sym]['Close'].squeeze().dropna() if 'Close' in df_data[sym] else df_data[sym].squeeze().dropna()
        except Exception:
            pass
        return None

    spy_close_series = _get_ticker_series(data, "SPY")
    candidates = []

    for ticker in tickers_to_scan:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                if ticker in data.columns.get_level_values(0):
                    df = data.xs(ticker, axis=1, level=0).dropna()
                elif ticker in data.columns.get_level_values(1):
                    df = data.xs(ticker, axis=1, level=1).dropna()
                else:
                    continue
            else:
                df = data.dropna()

            if len(df) < 200:
                continue

            close = df['Close']
            high = df['High']
            low = df['Low']

            curr_close = float(close.iloc[-1])
            prev_close = float(close.iloc[-2])
            day_change_pct = ((curr_close - prev_close) / prev_close) * 100

            # Technical Indicators
            ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
            ema50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
            ema200 = float(close.ewm(span=200, adjust=False).mean().iloc[-1])

            # Bollinger Bands (20, 2)
            rolling_mean20 = close.rolling(20).mean().iloc[-1]
            rolling_std20 = close.rolling(20).std().iloc[-1]
            lower_bb = float(rolling_mean20 - (2 * rolling_std20))
            upper_bb = float(rolling_mean20 + (2 * rolling_std20))

            # RSI 14
            rsi_series = calculate_rsi(close, 14)
            rsi = float(rsi_series.iloc[-1])

            # 20-Day High and Pullback calculation
            high_20d = float(high.iloc[-20:].max())
            pullback_pct = ((high_20d - curr_close) / high_20d) * 100

            # ATR 14
            atr_series = calculate_atr(df, 14)
            atr = float(atr_series.iloc[-1])

            # ADX 14 & Market Regime Detection (Trend vs Chop)
            adx_val = calculate_adx(df, 14)
            is_chop = adx_val < 20.0
            if adx_val >= 25.0:
                market_regime = "Trend (מגמה ברורה)"
            elif adx_val < 20.0:
                market_regime = "Chop / Range (דשדוש)"
            else:
                market_regime = "Transition (מעבר/ניטרלי)"

            # 20-Day Swing Range, Equilibrium, and OTE / Pricing Zone (ICT/SMC)
            swing_high = float(high.iloc[-20:].max())
            swing_low = float(low.iloc[-20:].min())
            swing_span = max(0.01, swing_high - swing_low)
            equilibrium = swing_low + 0.5 * swing_span
            retrace_pct = ((swing_high - curr_close) / swing_span) * 100

            # Pricing Zone classification:
            # - Discount / OTE Zone: 50% to 78.6% retracement (Sweet spot for institutional pullback entry)
            # - Discount Zone: 45% to 50% or > 78.6% (if supported)
            # - Premium Zone: < 45% retracement (clinging to highs, high risk of buying top / poor R:R)
            if 50.0 <= retrace_pct <= 78.6:
                pricing_zone = "Discount / OTE (כניסה אידיאלית)"
                is_ote = True
                is_discount = True
            elif retrace_pct >= 45.0:
                pricing_zone = "Discount (אזור מבצע)"
                is_ote = False
                is_discount = True
            else:
                pricing_zone = "Premium (אזור יקר / סכנת FOMO)"
                is_ote = False
                is_discount = False

            # CHOP REGIME BREAKOUT BAN:
            # If market regime is Chop / Range (ADX < 20), buying in Premium Zone at the top of range is strictly banned!
            if is_chop and not is_discount:
                continue

            # Gap-Up FOMO Filter:
            today_open = float(df['Open'].iloc[-1])
            gap_up_pct = ((today_open - prev_close) / prev_close) * 100
            has_gap_up = gap_up_pct >= 1.0

            # 1. Filter: Long-Term Trend Filter
            # Price > EMA 200 OR EMA 50 > EMA 200 (healthy bullish structure)
            if curr_close < ema200 and ema50 < ema200:
                continue

            # 2. Filter: Pullback Range (1.0% to 10.0%)
            if pullback_pct < 1.0 or pullback_pct > 10.0:
                continue

            # 3. Filter: RSI sweet spot (30 to 58)
            if rsi < 30 or rsi > 58:
                continue

            # 4. Proximity to Key Support
            dist_to_ema20 = abs(curr_close - ema20) / curr_close * 100
            dist_to_ema50 = abs(curr_close - ema50) / curr_close * 100
            dist_to_lower_bb = abs(curr_close - lower_bb) / curr_close * 100

            # Near at least one support level (within 2.5%)
            near_support = (dist_to_ema20 <= 2.5) or (dist_to_ema50 <= 2.5) or (dist_to_lower_bb <= 2.0)
            if not near_support:
                continue

            # --- Confluence Scoring (0 - 100) ---
            score = 0
            score_reasons = []

            # Trend Strength (max 35 pts)
            if curr_close > ema200:
                score += 20
                score_reasons.append("מעל EMA 200 (מגמה עולה)")
            if ema20 > ema50:
                score += 15
                score_reasons.append("EMA 20 > EMA 50 (מומנטום חיובי)")

            # Pullback Quality (max 25 pts)
            if 2.5 <= pullback_pct <= 6.5:
                score += 25
                score_reasons.append(f"תיקון אידיאלי ({pullback_pct:.1f}% משיא 20 יום)")
            elif 1.0 <= pullback_pct < 2.5 or 6.5 < pullback_pct <= 9.0:
                score += 15
                score_reasons.append(f"תיקון מתון ({pullback_pct:.1f}%)")

            # Key Support Contact (max 25 pts)
            if dist_to_ema20 <= 1.2:
                score += 20
                score_reasons.append(f"בדיקת תמיכה מדויקת ב-EMA 20 (${ema20:.2f})")
            elif dist_to_ema50 <= 1.5:
                score += 22
                score_reasons.append(f"בדיקת תמיכה חזקה ב-EMA 50 (${ema50:.2f})")
            elif dist_to_lower_bb <= 1.5:
                score += 18
                score_reasons.append(f"הגעה לרצועת בולינגר תחתונה (${lower_bb:.2f})")
            else:
                score += 10
                score_reasons.append("קרוב לאזור תמיכה דינמי")

            # RSI Confluence (max 15 pts)
            if 35.0 <= rsi <= 48.0:
                score += 15
                score_reasons.append(f"RSI מושלם לסווינג ({rsi:.1f})")
            elif 30.0 <= rsi < 35.0:
                score += 12
                score_reasons.append(f"RSI מכירת יתר ({rsi:.1f})")
            else:
                score += 8
                score_reasons.append(f"RSI בריא ({rsi:.1f})")

            # OTE / Discount Confluence Scoring (max 15 pts)
            if is_ote:
                score += 15
                score_reasons.append(f"אזור OTE מושלם ({retrace_pct:.1f}% נסיגה מהגל - Discount)")
            elif is_discount:
                score += 8
                score_reasons.append(f"נמצא ב-Discount Zone ({retrace_pct:.1f}% מהגל)")
            else:
                score -= 10
                score_reasons.append("זהירות: נסחר ב-Premium Zone (קרוב לשיא)")

            # Market Regime Bonus/Adjustment
            if not is_chop and curr_close > ema50:
                score += 5
                score_reasons.append(f"משטר שוק שורי (ADX {adx_val:.1f})")
            elif is_chop and is_discount:
                score += 5
                score_reasons.append(f"איסוף ברצפת טווח דשדוש (ADX {adx_val:.1f})")

            # Sector Rotation / RRG Confluence (max 12 pts, penalty -15 pts)
            is_index_etf = ticker.upper() in INDEX_ETFS
            sector_symbol = ticker.upper() if is_index_etf else TICKER_SECTOR_MAP.get(ticker.upper(), "SPY")
            sec_rrg = rrg_map.get(sector_symbol, {
                "sector": sector_symbol,
                "rs_ratio": 100.0,
                "rs_momentum": 100.0,
                "quadrant": "Leading" if is_index_etf else "Improving",
                "quadrant_hebrew": "מדד ייחוס / שוק" if is_index_etf else "ניטרלי",
                "badge_class": "leading" if is_index_etf else "improving"
            })
            sec_quadrant = sec_rrg.get("quadrant", "Improving")
            sec_rs = sec_rrg.get("rs_ratio", 100.0)
            sec_mom = sec_rrg.get("rs_momentum", 100.0)

            # Stock-Level Relative Strength & Alpha metrics (vs SPY and vs Sector)
            sec_close_series = _get_ticker_series(data, sector_symbol) if not is_index_etf else None
            alpha_metrics = calculate_stock_relative_strength(close.squeeze(), spy_close_series, sec_close_series)

            if is_index_etf:
                score += 5
                score_reasons.append(f"מדד שוק רחב ({ticker}) - פיזור סקטוריאלי מובנה")
            else:
                if sec_quadrant == "Improving":
                    score += 12
                    score_reasons.append(f"סקטור {sector_symbol} ברוטציית Improving 🚀 (צבירה מוסדית מוקדמת | RS: {sec_rs}, Mom: {sec_mom})")
                elif sec_quadrant == "Leading":
                    score += 10
                    score_reasons.append(f"סקטור {sector_symbol} מוביל Leading 🟢 (רוח גבית מוסדית חזקה | RS: {sec_rs}, Mom: {sec_mom})")
                elif sec_quadrant == "Weakening":
                    score += 0
                    score_reasons.append(f"סקטור {sector_symbol} נחלש Weakening 🟡 (אובדן מומנטום יחסי | RS: {sec_rs}, Mom: {sec_mom})")
                elif sec_quadrant == "Lagging":
                    score -= 15
                    score_reasons.append(f"אזהרה: סקטור {sector_symbol} מפגר Lagging 🔴 (יציאת הון מוסדי | RS: {sec_rs}, Mom: {sec_mom})")
                    if is_chop and not is_discount:
                        continue # Hard Skip: Lagging sector in Chop market without deep discount

                # Stock-Level Relative Strength / Alpha scoring (max 10 pts, penalty -10 pts)
                alpha_spy = alpha_metrics.get("alpha_spy_20d", 0.0)
                alpha_sec = alpha_metrics.get("alpha_sec_20d", 0.0)
                alpha_stat = alpha_metrics.get("status", "Neutral")

                if alpha_stat == "Dual Leader":
                    score += 8
                    score_reasons.append(f"אלפא כפולה 🌟: מנצחת שוק (+{alpha_spy:+.1f}%) ומובילת סקטור (+{alpha_sec:+.1f}%)")
                elif alpha_stat == "Market Outperformer":
                    score += 5
                    score_reasons.append(f"מנצחת את השוק 🟢 (+{alpha_spy:+.1f}% מעל SPY ב-20 יום)")
                elif alpha_stat == "Relative Laggard":
                    score -= 10
                    score_reasons.append(f"אזהרה: מפגרת יחסית 🔴 ({alpha_spy:+.1f}% מול SPY, {alpha_sec:+.1f}% מול סקטור)")

                if alpha_metrics.get("is_divergence"):
                    score += 5
                    score_reasons.append("איסוף מוסדי סמוי ⚡: ספיגת היצע ועוצמה יחסית בירידות מדד")

            # Filter by minimum score
            if score < min_score:
                continue

            # --- Financial & Trade Plan Calculations ($10,000 Capital) ---

            # 1. Structural Support Anchor & Whipsaw Shield
            # Look back 3 candles to avoid micro-wicks and check tested moving averages/bands
            recent_low = float(low.iloc[-3:].min())
            
            tested_supports = [recent_low]
            if curr_close >= ema50 and (curr_close - ema50) / curr_close <= 0.035:
                tested_supports.append(ema50)
            if curr_close >= lower_bb and (curr_close - lower_bb) / curr_close <= 0.035:
                tested_supports.append(lower_bb)
            
            deepest_support = min(tested_supports)

            # Whipsaw Shield: Anchor below deepest tested support + enforce ATR noise floor
            support_buffer = deepest_support * (0.004 if is_index_etf else 0.006)
            structural_stop = deepest_support - support_buffer

            # Minimum distance based on ATR (at least 0.75x ATR for ETFs, 0.85x ATR for Equities)
            min_atr_distance = atr * (0.75 if is_index_etf else 0.85)
            atr_stop = curr_close - min_atr_distance

            # Safe stop is the lower of structural stop or ATR floor (guarantees room to breathe)
            tech_stop = round(min(structural_stop, atr_stop), 2)

            # Dual Entry definitions
            entry_limit = round(curr_close, 2)
            entry_confirmation = round(curr_close * 1.0025, 2)

            # Enhanced Execution Protocol (Macro Freeze + Lagging Sector Limit Prohibition)
            is_critical_macro = (macro_risk.get("warning_level") == "CRITICAL" or 
                                 any(any(kw in e.get("title", "") for kw in ["FOMC", "Powell", "CPI"]) for e in macro_risk.get("events", [])))

            if is_critical_macro:
                entry_recommendation = "הקפאת מאקרו (Macro Freeze ⛔)"
                entry_note = "חוק הקפאת מאקרו: אירוע פד/ריבית/מדד מחירים היום! איסור מוחלט על פקודות Limit עיוורות; אין לפתוח טרייד לפני 18:00 (רק לאחר שהאירוע נספג במלואו)."
                active_entry = entry_confirmation
            elif sec_quadrant == "Lagging":
                entry_recommendation = "אישור פריצת שיא (איסור לימיט 🔴)"
                entry_note = f"סקטור {sector_symbol} בפיגור (Lagging 🔴): איסור מוחלט על פקודת Limit פסיבית מראש! כניסה אך ורק בפריצת שיא נר שעה ראשונה (HOD Breakout) לאחר שהקונים מוכיחים ספיגת חולשת הסקטור."
                active_entry = round(curr_close * 1.004, 2)
            elif macro_risk.get("has_high_impact", False):
                entry_recommendation = "אישור היפוך (Confirmation)"
                entry_note = "יום מאקרו תנודתי: חובה להמתין לנר 15 דק' ירוק מעל התמיכה! אין להזין לימיט פסיבי לפני שעת האירוע."
                active_entry = entry_confirmation
            elif has_gap_up:
                entry_recommendation = "מילוי גאפ / אישור היפוך (Gap Fill Retest)"
                entry_note = f"זוהה Gap-Up של +{gap_up_pct:.1f}% בפתיחה: חל איסור כניסה בלימיט במחיר הגאפ; להמתין לבדיקת תמיכה/סגירת פער למניעת FOMO."
                active_entry = entry_confirmation
            else:
                entry_recommendation = "לימיט פסיבי או אישור"
                entry_note = "יום שקט: ניתן להזין פקודת Limit בתמיכה, או להמתין לנר 15 דק' ירוק לאישור נוסף."
                active_entry = entry_limit

            risk_per_share = round(active_entry - tech_stop, 2)
            risk_pct = round((risk_per_share / active_entry) * 100, 2)

            # Filter out setups where risk is negative or excessively wide (>3.5% for ETFs, >4.6% for Equities)
            max_allowed_risk_pct = 3.5 if is_index_etf else 4.6
            if risk_per_share <= 0 or risk_pct > max_allowed_risk_pct:
                continue

            # 2. Resistance Ceiling & Tiered Targets (TP1 and TP2)
            # If price is below EMA 20, EMA 20 acts as intermediate resistance (TP1)
            if active_entry < ema20:
                tp1_price = round(ema20, 2)
                tp1_pct = round(((tp1_price - active_entry) / active_entry) * 100, 2)
                min_upside = 1.2 if is_index_etf else 1.4
                if tp1_pct < min_upside:
                    # Ceiling too close (<1.2% / <1.4% upside to resistance) - No Man's Land right under overhead resistance
                    continue
            else:
                tp1_pct = max(target_gross_pct, 2.0) # At least 2.0%
                tp1_price = round(active_entry * (1 + tp1_pct / 100.0), 2)

            reward1_per_share = round(tp1_price - active_entry, 2)

            # TP2: Full Swing Objective (towards 20-day high or structural resistance)
            tp2_price = round(max(high_20d * 0.995, active_entry * (1.03 if is_index_etf else 1.04)), 2)
            tp2_pct = round(((tp2_price - active_entry) / active_entry) * 100, 2)
            reward2_per_share = round(tp2_price - active_entry, 2)

            # 3. Tiered Real R:R Filter & Nearest Obstacle Protection
            rr_tp1 = round(reward1_per_share / max(0.01, risk_per_share), 2)
            rr_tp2 = round(reward2_per_share / max(0.01, risk_per_share), 2)
            blended_rr = round((0.5 * reward1_per_share + 0.5 * reward2_per_share) / max(0.01, risk_per_share), 2)

            # NEAREST OBSTACLE PROTECTION:
            # If price is below EMA 20, we cannot accept an inverted R:R to the nearest ceiling.
            if active_entry < ema20 and rr_tp1 < 0.65:
                continue

            min_rr_threshold = 1.4 if is_index_etf else 1.7
            if rr_tp2 < min_rr_threshold:
                continue

            min_blended_threshold = 1.15 if is_index_etf else 1.25
            if blended_rr < min_blended_threshold:
                continue

            # 4. Position Sizing: Risk-Budgeted ($75 Max Risk) vs Full Capital ($10,000)
            max_risk_dollars = 75.0
            shares_by_risk = max(1, int(max_risk_dollars / max(0.01, risk_per_share)))
            shares_by_capital = int(capital / active_entry)
            if shares_by_capital == 0:
                continue

            recommended_shares = min(shares_by_risk, shares_by_capital)
            recommended_invested = round(recommended_shares * active_entry, 2)
            actual_dollar_risk = round(risk_per_share * recommended_shares, 2)

            full_shares = shares_by_capital
            full_invested = round(full_shares * active_entry, 2)
            full_dollar_risk = round(risk_per_share * full_shares, 2)

            gross_profit = round(reward2_per_share * recommended_shares, 2)
            ibkr_fee = 5.00 # $2.50 buy + $2.50 sell
            taxable_profit = max(0.0, gross_profit - ibkr_fee)
            tax_amount = round(taxable_profit * 0.25, 2) # Israeli capital gains tax
            net_profit = round(taxable_profit - tax_amount, 2)
            net_roi_pct = round((net_profit / recommended_invested) * 100, 2)

            # Support level description: Identify the actual technical support tested
            supports_checked = []
            if abs(curr_close - lower_bb) / curr_close <= 0.02:
                supports_checked.append((f"רצועת בולינגר תחתונה (${lower_bb:.2f})", abs(curr_close - lower_bb)))
            if ema50 <= curr_close * 1.01:
                supports_checked.append((f"EMA 50 (${ema50:.2f})", abs(curr_close - ema50)))
            if ema20 <= curr_close * 1.01:
                supports_checked.append((f"EMA 20 (${ema20:.2f})", abs(curr_close - ema20)))
            
            if supports_checked:
                supports_checked.sort(key=lambda x: x[1])
                support_desc = supports_checked[0][0]
            else:
                support_desc = f"רצועת בולינגר תחתונה (${lower_bb:.2f})"

            candidate = {
                "ticker": ticker,
                "score": score,
                "sector": sector_symbol,
                "sector_rrg": sec_rrg,
                "alpha_metrics": alpha_metrics,
                "price": round(curr_close, 2),
                "day_change_pct": round(day_change_pct, 2),
                "pullback_pct": round(pullback_pct, 1),
                "rsi": round(rsi, 1),
                "adx": round(adx_val, 1),
                "market_regime": market_regime,
                "pricing_zone": pricing_zone,
                "retrace_pct": round(retrace_pct, 1),
                "support_level": support_desc,
                "reasons": score_reasons,
                "trade_plan": {
                    "asset_type": "Index ETF (מדד רחב)" if is_index_etf else "Single Stock (מניה בודדת)",
                    "sector": sector_symbol,
                    "sector_rrg": sec_rrg,
                    "alpha_metrics": alpha_metrics,
                    "market_regime": market_regime,
                    "pricing_zone": pricing_zone,
                    "retrace_pct": round(retrace_pct, 1),
                    "has_gap_up": has_gap_up,
                    "entry_limit": entry_limit,
                    "entry_confirmation": entry_confirmation,
                    "entry_recommendation": entry_recommendation,
                    "entry_note": entry_note,
                    "recommended_shares": recommended_shares,
                    "recommended_invested": recommended_invested,
                    "actual_dollar_risk": actual_dollar_risk,
                    "full_shares": full_shares,
                    "full_invested": full_invested,
                    "full_dollar_risk": full_dollar_risk,
                    "entry_price": active_entry,
                    "target_price": tp2_price,
                    "target_pct": tp2_pct,
                    "tp1_price": tp1_price,
                    "tp1_pct": tp1_pct,
                    "tp2_price": tp2_price,
                    "tp2_pct": tp2_pct,
                    "stop_loss": tech_stop,
                    "risk_pct": risk_pct,
                    "rr_ratio": rr_tp2,
                    "rr_tp1": rr_tp1,
                    "rr_tp2": rr_tp2,
                    "blended_rr": blended_rr,
                    "whipsaw_shield": "פעילה (מעוגן מתחת לתמיכות עם מרווח רעש ATR)",
                    "gross_profit": gross_profit,
                    "ibkr_commission": ibkr_fee,
                    "tax_25pct": tax_amount,
                    "net_profit": net_profit,
                    "net_roi_pct": net_roi_pct
                }
            }
            candidates.append(candidate)

        except Exception as err:
            continue

    # Sort descending by score
    candidates.sort(key=lambda x: x["score"], reverse=True)
    top_candidates = candidates[:top_n]

    return {
        "scanned_universe_size": len(tickers_to_scan),
        "matches_count": len(candidates),
        "execution_time_sec": round(elapsed, 2),
        "macro_risk": macro_risk,
        "candidates": top_candidates
    }

def print_cli_summary(result):
    print("=" * 75)
    print(f"  SWING SCANNER: Found {result['matches_count']} setups (Scanned {result['scanned_universe_size']} in {result['execution_time_sec']}s)")
    macro = result.get("macro_risk", {})
    if macro.get("has_high_impact"):
        print("!" * 75)
        print(f"  🚨 {macro.get('banner_hebrew', 'התראת מאקרו פעילה')}")
        print("!" * 75)
    print("=" * 75)
    
    if not result["candidates"]:
        print("No candidates currently meet all swing confluence criteria.")
        return

    for idx, c in enumerate(result["candidates"], 1):
        tp = c["trade_plan"]
        sec_info = c.get('sector_rrg', {})
        alpha_info = c.get('alpha_metrics', {})
        print(f"\n[{idx}] {c['ticker']} ({tp['asset_type']}) | Score: {c['score']}/100 | Price: ${c['price']} ({c['day_change_pct']:+.2f}%)")
        print(f"    Tri-Layer: Regime: {c['market_regime']} | Sector RRG: {c.get('sector', 'N/A')} [{sec_info.get('quadrant_hebrew', 'N/A')}] | Alpha: [{alpha_info.get('status_hebrew', 'N/A')}] (vs SPY: {alpha_info.get('alpha_spy_20d', 0.0):+.1f}%, vs Sec: {alpha_info.get('alpha_sec_20d', 0.0):+.1f}%) | Zone: {c['pricing_zone']} (Retrace: {c['retrace_pct']}%)")
        print(f"    Pullback: -{c['pullback_pct']}% | RSI: {c['rsi']} (ADX: {c['adx']}) | Support: {c['support_level']}")
        print(f"    Reasons: {', '.join(c['reasons'])}")
        print(f"    Trade Plan (Risk-Budgeted $75 Max Risk | Whipsaw Shield Active):")
        print(f"      - Entry Mode: {tp['entry_recommendation']} (Limit: ${tp['entry_limit']} | Confirm: ${tp['entry_confirmation']})")
        print(f"      - Guidance: {tp['entry_note']}")
        print(f"      - Recommended Size: {tp['recommended_shares']} shs (${tp['recommended_invested']:,.2f}) -> Max Risk: ${tp['actual_dollar_risk']:.2f}")
        print(f"      - Targets: TP1 ${tp['tp1_price']} (+{tp['tp1_pct']}%, R:R 1:{tp['rr_tp1']}) | TP2 ${tp['tp2_price']} (+{tp['tp2_pct']}%, R:R 1:{tp['rr_tp2']})")
        print(f"      - Stop Loss: ${tp['stop_loss']} (-{tp['risk_pct']}%) [Safe Structural Stop | Blended R:R 1:{tp['blended_rr']}]")
        print(f"      - Net in Pocket: +${tp['net_profit']:.2f} (+{tp['net_roi_pct']:.2f}% net on invested after IBKR & 25% Tax)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Swing Opportunity Scanner")
    parser.add_argument("--capital", type=float, default=10000.0, help="Capital allocation (USD)")
    parser.add_argument("--target", type=float, default=2.0, help="Target gross profit percent")
    parser.add_argument("--top", type=int, default=4, help="Number of top candidates to return")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    parser.add_argument("--tickers", nargs="+", help="Optional specific tickers to scan")
    
    args = parser.parse_args()
    
    res = run_scanner(
        tickers=args.tickers,
        capital=args.capital,
        target_gross_pct=args.target,
        top_n=args.top
    )
    
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print_cli_summary(res)
