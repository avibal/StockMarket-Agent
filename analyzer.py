import pandas as pd
import numpy as np
from typing import Dict, Any, Union

class Analyzer:
    """
    Performs custom statistical computations on historical pandas structures.
    Uses pure pandas implementations for SMA, RSI, and MACD to guarantee
    robustness across all Windows Python environments without native binary deps.
    """
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates 50 SMA, 200 SMA, Wilder's RSI (14), and MACD (12, 26, 9) 
        directly on a pandas DataFrame.
        """
        df = df.copy()
        
        # 1. Simple Moving Averages
        df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
        df['SMA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
        
        # 2. RSI (Relative Strength Index) using Wilder's Smoothing
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        
        # First avg gain/loss is a simple mean
        avg_gain = gain.rolling(window=14, min_periods=14).mean()
        avg_loss = loss.rolling(window=14, min_periods=14).mean()
        
        # Wilder's exponential smoothing method
        # We operate on writeable copy arrays to avoid read-only errors in newer pandas/numpy versions
        avg_gain_vals = avg_gain.to_numpy(copy=True)
        avg_loss_vals = avg_loss.to_numpy(copy=True)
        gain_vals = gain.to_numpy()
        loss_vals = loss.to_numpy()
        
        for i in range(14, len(df)):
            if not np.isnan(avg_gain_vals[i-1]):
                avg_gain_vals[i] = (avg_gain_vals[i-1] * 13 + gain_vals[i]) / 14
            if not np.isnan(avg_loss_vals[i-1]):
                avg_loss_vals[i] = (avg_loss_vals[i-1] * 13 + loss_vals[i]) / 14
                
        df['Avg_Gain'] = avg_gain_vals
        df['Avg_Loss'] = avg_loss_vals
        
        # Prevent division by zero
        rs = df['Avg_Gain'] / df['Avg_Loss'].replace(0, np.nan)
        df['RSI_14'] = 100 - (100 / (1 + rs))
        # Fill leading NaNs
        df['RSI_14'] = df['RSI_14'].fillna(50)
        
        # 3. MACD (Moving Average Convergence Divergence)
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        return df

    @classmethod
    def analyze(cls, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interprets calculated indicators to form an executive diagnostic summary 
        prepared for feeding the Gemini prompt.
        """
        df = stock_data["history"]
        fundamentals = stock_data["fundamentals"]
        
        # Inject calculations
        df_indicators = cls.calculate_indicators(df)
        latest = df_indicators.iloc[-1]
        
        current_price = fundamentals["current_price"]
        
        # Retrieve latest metrics safely
        rsi = float(latest["RSI_14"])
        sma_50 = float(latest["SMA_50"]) if not pd.isna(latest["SMA_50"]) else None
        sma_200 = float(latest["SMA_200"]) if not pd.isna(latest["SMA_200"]) else None
        macd = float(latest["MACD"]) if not pd.isna(latest["MACD"]) else 0.0
        macd_signal = float(latest["MACD_Signal"]) if not pd.isna(latest["MACD_Signal"]) else 0.0
        macd_hist = float(latest["MACD_Hist"]) if not pd.isna(latest["MACD_Hist"]) else 0.0
        
        # Calculate historical momentum change compared to the previous day
        prev_macd_hist = 0.0
        if len(df_indicators) > 1:
            prev_row = df_indicators.iloc[-2]
            prev_macd_hist = float(prev_row["MACD_Hist"]) if not pd.isna(prev_row["MACD_Hist"]) else 0.0
            
        macd_momentum_state = "NEUTRAL"
        if macd_hist > 0:
            if macd_hist > prev_macd_hist:
                macd_momentum_state = "ACCELERATING BULLISH MOMENTUM"
            else:
                macd_momentum_state = "FADING BULLISH MOMENTUM"
        elif macd_hist < 0:
            if macd_hist < prev_macd_hist:
                macd_momentum_state = "ACCELERATING BEARISH MOMENTUM"
            else:
                macd_momentum_state = "FADING BEARISH MOMENTUM"
                
        # Calculate standard diagnostics
        rsi_signal = "NEUTRAL"
        if rsi < 30:
            rsi_signal = "OVERSOLD (Potential Bullish Reversal)"
        elif rsi > 70:
            rsi_signal = "OVERBOUGHT (Potential Bearish Retracement)"
            
        trend_signal = "NEUTRAL"
        if sma_50 and sma_200:
            if current_price > sma_50 > sma_200:
                trend_signal = "STRONG BULLISH"
            elif current_price < sma_50 < sma_200:
                trend_signal = "STRONG BEARISH"
            elif sma_50 > sma_200:
                trend_signal = "BULLISH (Golden Cross Active)"
            elif sma_50 < sma_200:
                trend_signal = "BEARISH (Death Cross Active)"
                
        macd_signal_text = "NEUTRAL"
        if macd and macd_signal:
            if macd > macd_signal and macd_hist > 0:
                macd_signal_text = "BULLISH CROSSOVER"
            elif macd < macd_signal and macd_hist < 0:
                macd_signal_text = "BEARISH CROSSOVER"
                
        # Format for return payload
        return {
            "fundamentals": fundamentals,
            "technicals": {
                "rsi": round(rsi, 2),
                "rsi_signal": rsi_signal,
                "sma_50": round(sma_50, 2) if sma_50 else "N/A",
                "sma_200": round(sma_200, 2) if sma_200 else "N/A",
                "trend_signal": trend_signal,
                "macd": round(macd, 4),
                "macd_signal": round(macd_signal, 4),
                "macd_hist": round(macd_hist, 4),
                "macd_signal_text": macd_signal_text,
                "macd_momentum_state": macd_momentum_state
            }
        }

    @classmethod
    def analyze_portfolio(cls, stock_data: Dict[str, Any], purchase_price: float) -> Dict[str, Any]:
        """
        Performs custom portfolio position analysis relative to a purchase price.
        Calculates:
        1. Daily Change (שינוי יומי) - Yesterday's percentage change.
        2. Total Return (תשואה כוללת) - Percentage return relative to the purchase price.
        3. Fibonacci Support/Resistance levels since purchase date with custom Hebrew roles.
        4. Support/Resistance Touches (Backward compatible base level).
        5. Consolidation (דשדוש) - If 52w price volatility range is within ±3% (total span <= 6%).
        """
        df = stock_data["history"]
        fundamentals = stock_data["fundamentals"]
        current_price = fundamentals["current_price"]
        
        # 1. Daily Change (שינוי יומי) - calculated up to the end of the completed session prior to running the current analysis
        daily_change = 0.0
        if len(df) > 1:
            import datetime
            latest_date = df.index[-1].date()
            today = datetime.date.today()
            if latest_date == today and len(df) > 2:
                target_close = float(df['Close'].iloc[-2])
                prev_close = float(df['Close'].iloc[-3])
            else:
                target_close = float(df['Close'].iloc[-1])
                prev_close = float(df['Close'].iloc[-2])
            daily_change = ((target_close - prev_close) / prev_close) * 100
            
        # 2. Total Return (תשואה כוללת)
        total_return = ((current_price - purchase_price) / purchase_price) * 100
        
        # 3. Locate the purchase date in history (earliest day where Low <= purchase_price <= High)
        purchase_mask = (df['Low'] <= purchase_price) & (df['High'] >= purchase_price)
        purchase_indices = df.index[purchase_mask]
        
        if len(purchase_indices) > 0:
            purchase_date = purchase_indices[0]
            purchase_date_str = purchase_date.strftime("%Y-%m-%d")
            # Slice df from purchase_date to today
            df_since_purchase = df.loc[purchase_date:]
        else:
            # Fallback if purchase price was never explicitly within a daily candle range
            df_since_purchase = df
            purchase_date_str = "לא נמצא בהיסטוריית הנתונים"
            
        # 4. Fibonacci Level Support/Resistance Analysis
        peak_price = float(df_since_purchase['High'].max()) if not df_since_purchase.empty else purchase_price
        span = peak_price - purchase_price
        
        fib_definitions = [
            {"ratio": 0.236, "name": "23.6%", "role_desc": "קו הבלימה הראשון"},
            {"ratio": 0.382, "name": "38.2%", "role_desc": "קו התיקון הבריא"},
            {"ratio": 0.500, "name": "50.0%", "role_desc": "קו אמצע הדרך"},
            {"ratio": 0.618, "name": "61.8%", "role_desc": "קו הזהב הקריטי"},
            {"ratio": 0.786, "name": "78.6%", "role_desc": "קו ההגנה האחרון"},
            {"ratio": 1.000, "name": "100.0%", "role_desc": "מחיר הרכישה שלך"}
        ]
        
        fib_levels = []
        for item in fib_definitions:
            ratio = item["ratio"]
            level_price = peak_price - ratio * span if span > 0 else purchase_price
            lb = level_price * 0.985
            ub = level_price * 1.015
            
            sup_count = len(df_since_purchase[(df_since_purchase['Low'] >= lb) & (df_since_purchase['Low'] <= ub)]) if not df_since_purchase.empty else 0
            res_count = len(df_since_purchase[(df_since_purchase['High'] >= lb) & (df_since_purchase['High'] <= ub)]) if not df_since_purchase.empty else 0
            
            role = "תמיכה 🟢" if current_price >= level_price else "התנגדות 🔴"
            
            fib_levels.append({
                "name": item["name"],
                "role_desc": item["role_desc"],
                "price": round(level_price, 2),
                "current_role": role,
                "support_touches": sup_count,
                "resistance_touches": res_count,
                "total_touches": sup_count + res_count
            })
            
        # Backward-compatible counts (based on purchase price level)
        purchase_lb = purchase_price * 0.985
        purchase_ub = purchase_price * 1.015
        support_touches_count = len(df_since_purchase[(df_since_purchase['Low'] >= purchase_lb) & (df_since_purchase['Low'] <= purchase_ub)]) if not df_since_purchase.empty else 0
        support_touched = "כן 🟢" if support_touches_count >= 3 else "לא 🔴"
        
        resistance_touches_count = len(df_since_purchase[(df_since_purchase['High'] >= purchase_lb) & (df_since_purchase['High'] <= purchase_ub)]) if not df_since_purchase.empty else 0
        resistance_touched = "כן 🟢" if resistance_touches_count >= 3 else "לא 🔴"
        
        # 5. Consolidation (דשדוש) in the last 52 weeks (252 trading days)
        df_52w = df.iloc[-252:] if len(df) >= 252 else df
        max_price_52w = float(df_52w['High'].max())
        min_price_52w = float(df_52w['Low'].min())
        
        yearly_volatility = 0.0
        if min_price_52w > 0:
            yearly_volatility = ((max_price_52w - min_price_52w) / min_price_52w) * 100
            
        # Consolidation is True if the total 52w range is 6% or less (±3% around midpoint)
        consolidation_active = yearly_volatility <= 6.0
        consolidation = "כן 🟢 (טווח תנועה שנתי צר)" if consolidation_active else "לא 🔴 (תנודתיות שנתית רחבה)"
        
        # Determine appropriate emojis
        daily_change_emoji = "🟢" if daily_change > 0 else ("🔴" if daily_change < 0 else "⚪")
        total_return_emoji = "🚀" if total_return >= 10.0 else ("🟢" if total_return > 0 else ("🔴" if total_return < 0 else "⚪"))
        
        return {
            "fundamentals": fundamentals,
            "portfolio_metrics": {
                "purchase_price": purchase_price,
                "purchase_date": purchase_date_str,
                "current_price": current_price,
                "daily_change": round(daily_change, 2),
                "daily_change_emoji": daily_change_emoji,
                "total_return": round(total_return, 2),
                "total_return_emoji": total_return_emoji,
                "support_touches_count": support_touches_count,
                "support_touched": support_touched,
                "resistance_touches_count": resistance_touches_count,
                "resistance_touched": resistance_touched,
                "yearly_volatility": round(yearly_volatility, 2),
                "consolidation": consolidation,
                "peak_price": round(peak_price, 2),
                "fibonacci_levels": fib_levels
            }
        }

    @classmethod
    def analyze_strategic_position(cls, stock_data: Dict[str, Any], purchase_price: float, investment_type: str, investment_period: str) -> Dict[str, Any]:
        """
        Performs strategic position analysis based on investment type and period.
        Calculates indicators, support and resistance, and Fibonacci levels customized
        specifically to the chosen strategy period window.
        """
        df = stock_data["history"]
        fundamentals = stock_data["fundamentals"]
        current_price = fundamentals["current_price"]
        
        # 1. Parse investment period to discover lookback window (trading days)
        period_str = str(investment_period).lower().strip()
        days = 252 # Default to 1 year of trading days
        if "month" in period_str:
            try:
                num = int(''.join(filter(str.isdigit, period_str)))
                days = num * 21
            except Exception:
                days = 42 # Default to 2 months
        elif "week" in period_str:
            try:
                num = int(''.join(filter(str.isdigit, period_str)))
                days = num * 5
            except Exception:
                days = 10
        elif "year" in period_str:
            try:
                num = int(''.join(filter(str.isdigit, period_str)))
                days = num * 252
            except Exception:
                days = 252
        
        # Clamp days to size of df
        days = min(days, len(df))
        
        # Slice DataFrame specifically to this strategy timeframe
        df_period = df.iloc[-days:] if len(df) >= days else df
        
        # Calculate technical indicators on the sliced data
        df_indicators = cls.calculate_indicators(df)
        latest = df_indicators.iloc[-1]
        
        # 2. Daily Change
        daily_change = 0.0
        if len(df) > 1:
            target_close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            daily_change = ((target_close - prev_close) / prev_close) * 100
            
        # 3. Total Return
        total_return = ((current_price - purchase_price) / purchase_price) * 100
        
        # 4. Support & Resistance Analysis inside the period
        peak_price = float(df_period['High'].max()) if not df_period.empty else purchase_price
        span = peak_price - purchase_price
        
        fib_definitions = [
            {"ratio": 0.236, "name": "23.6%", "role_desc": "קו הבלימה הראשון"},
            {"ratio": 0.382, "name": "38.2%", "role_desc": "קו התיקון הבריא"},
            {"ratio": 0.500, "name": "50.0%", "role_desc": "קו אמצע הדרך"},
            {"ratio": 0.618, "name": "61.8%", "role_desc": "קו הזהב הקריטי"},
            {"ratio": 0.786, "name": "78.6%", "role_desc": "קו ההגנה האחרון"},
            {"ratio": 1.000, "name": "100.0%", "role_desc": "מחיר הרכישה שלך"}
        ]
        
        fib_levels = []
        for item in fib_definitions:
            ratio = item["ratio"]
            level_price = peak_price - ratio * span if span > 0 else purchase_price
            lb = level_price * 0.985
            ub = level_price * 1.015
            
            sup_count = len(df_period[(df_period['Low'] >= lb) & (df_period['Low'] <= ub)]) if not df_period.empty else 0
            res_count = len(df_period[(df_period['High'] >= lb) & (df_period['High'] <= ub)]) if not df_period.empty else 0
            
            role = "תמיכה 🟢" if current_price >= level_price else "התנגדות 🔴"
            
            fib_levels.append({
                "name": item["name"],
                "role_desc": item["role_desc"],
                "price": round(level_price, 2),
                "current_role": role,
                "support_touches": sup_count,
                "resistance_touches": res_count,
                "total_touches": sup_count + res_count
            })
            
        # 5. Consolidation inside the period
        max_price_period = float(df_period['High'].max())
        min_price_period = float(df_period['Low'].min())
        period_volatility = 0.0
        if min_price_period > 0:
            period_volatility = ((max_price_period - min_price_period) / min_price_period) * 100
            
        consolidation_active = period_volatility <= 6.0
        consolidation = f"כן 🟢 (טווח תנועה צר של {period_volatility:.1f}%)" if consolidation_active else f"לא 🔴 (תנודתיות של {period_volatility:.1f}%)"
        
        # 6. Emas & Technical Diagnostics
        rsi = float(latest["RSI_14"])
        sma_50 = float(latest["SMA_50"]) if not pd.isna(latest["SMA_50"]) else None
        sma_200 = float(latest["SMA_200"]) if not pd.isna(latest["SMA_200"]) else None
        macd_hist = float(latest["MACD_Hist"]) if not pd.isna(latest["MACD_Hist"]) else 0.0
        
        # Determine appropriate emojis
        daily_change_emoji = "🟢" if daily_change > 0 else ("🔴" if daily_change < 0 else "⚪")
        total_return_emoji = "🚀" if total_return >= 10.0 else ("🟢" if total_return > 0 else ("🔴" if total_return < 0 else "⚪"))
        
        return {
            "fundamentals": fundamentals,
            "portfolio_metrics": {
                "purchase_price": purchase_price,
                "current_price": current_price,
                "daily_change": round(daily_change, 2),
                "daily_change_emoji": daily_change_emoji,
                "total_return": round(total_return, 2),
                "total_return_emoji": total_return_emoji,
                "period_volatility": round(period_volatility, 2),
                "consolidation": consolidation,
                "peak_price": round(peak_price, 2),
                "fibonacci_levels": fib_levels,
                "technicals": {
                    "rsi": round(rsi, 2),
                    "sma_50": round(sma_50, 2) if sma_50 else "N/A",
                    "sma_200": round(sma_200, 2) if sma_200 else "N/A",
                    "macd_hist": round(macd_hist, 4)
                }
            }
        }

