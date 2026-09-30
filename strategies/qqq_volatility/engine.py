"""
QQQ Volatility Engine
Calculates indicators, detects mean-reversion setups on QQQ,
sizes $10,000 TQQQ positions with +1.0% target, and simulates the last 30 trading days.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yfinance as yf

# Configure UTF-8 for Windows PowerShell output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return 100.0 - (100.0 / (1.0 + rs))


def fetch_ticker_individual(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch a single ticker using yf.Ticker to avoid batch SQLite locking."""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval="1d", auto_adjust=False)
        if not df.empty:
            df.columns = [c.lower() for c in df.columns]
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        print(f"Warning: Failed to fetch individual ticker {ticker}: {e}", file=sys.stderr)
        return pd.DataFrame()


def fetch_strategy_data():
    """Fetch daily price history for QQQ, TQQQ and ^VIX with robust retries, threads=False, and fallback."""
    tickers = ["QQQ", "TQQQ", "^VIX"]
    data = None
    
    # 1. Attempt batch download with threads=False to avoid SQLite lock collisions
    for attempt in range(1, 4):
        try:
            data = yf.download(tickers, period="1y", interval="1d", progress=False, auto_adjust=False, threads=False)
            if data is not None and not data.empty and isinstance(data.columns, pd.MultiIndex):
                if 'Close' in data and 'QQQ' in data['Close'] and 'TQQQ' in data['Close']:
                    if len(data['Close']['QQQ'].dropna()) >= 50 and len(data['Close']['TQQQ'].dropna()) >= 50:
                        break
            time.sleep(1.5)
        except Exception as e:
            print(f"Warning: Batch download attempt {attempt} failed ({e}). Retrying...", file=sys.stderr)
            time.sleep(2.0)
            
    # Check if batch data is complete and valid
    is_valid_batch = False
    if data is not None and not data.empty and isinstance(data.columns, pd.MultiIndex):
        if 'Close' in data and 'QQQ' in data['Close'] and 'TQQQ' in data['Close']:
            if len(data['Close']['QQQ'].dropna()) >= 50 and len(data['Close']['TQQQ'].dropna()) >= 50:
                is_valid_batch = True
                
    if is_valid_batch:
        closes = data['Close']
        highs = data['High']
        lows = data['Low']
        opens = data['Open']
        volumes = data['Volume']
        
        df_qqq = pd.DataFrame({
            'open': opens['QQQ'],
            'high': highs['QQQ'],
            'low': lows['QQQ'],
            'close': closes['QQQ'],
            'volume': volumes['QQQ']
        }).dropna()
        
        df_tqqq = pd.DataFrame({
            'open': opens['TQQQ'],
            'high': highs['TQQQ'],
            'low': lows['TQQQ'],
            'close': closes['TQQQ'],
            'volume': volumes['TQQQ']
        }).dropna()
        
        vix_series = closes['^VIX'].dropna() if '^VIX' in closes else pd.Series(dtype=float)
    else:
        # Fallback to individual ticker download
        print("Notice: Falling back to individual ticker downloads...", file=sys.stderr)
        hist_qqq = fetch_ticker_individual("QQQ")
        hist_tqqq = fetch_ticker_individual("TQQQ")
        hist_vix = fetch_ticker_individual("^VIX")
        
        if hist_qqq.empty or hist_tqqq.empty:
            raise ValueError("Failed to fetch QQQ or TQQQ data from yfinance after all attempts.")
            
        df_qqq = pd.DataFrame({
            'open': hist_qqq['open'],
            'high': hist_qqq['high'],
            'low': hist_qqq['low'],
            'close': hist_qqq['close'],
            'volume': hist_qqq['volume']
        }).dropna()
        
        df_tqqq = pd.DataFrame({
            'open': hist_tqqq['open'],
            'high': hist_tqqq['high'],
            'low': hist_tqqq['low'],
            'close': hist_tqqq['close'],
            'volume': hist_tqqq['volume']
        }).dropna()
        
        vix_series = hist_vix['close'].dropna() if not hist_vix.empty and 'close' in hist_vix else pd.Series(dtype=float)
        
    # Strip any timezone to guarantee clean index alignment
    if df_qqq.index.tz is not None:
        df_qqq.index = df_qqq.index.tz_localize(None)
    if df_tqqq.index.tz is not None:
        df_tqqq.index = df_tqqq.index.tz_localize(None)
    if hasattr(vix_series.index, 'tz') and vix_series.index.tz is not None:
        vix_series.index = vix_series.index.tz_localize(None)
        
    # Align dates
    common_idx = df_qqq.index.intersection(df_tqqq.index)
    if len(common_idx) < 30:
        raise ValueError(f"Insufficient aligned price data ({len(common_idx)} bars).")
        
    df_qqq = df_qqq.loc[common_idx].copy()
    df_tqqq = df_tqqq.loc[common_idx].copy()
    vix_series = vix_series.reindex(common_idx).ffill().bfill()
    
    return df_qqq, df_tqqq, vix_series


def compute_indicators(df_qqq: pd.DataFrame, df_tqqq: pd.DataFrame, vix_series: pd.Series):
    """Compute moving averages, RSI, and technical metrics."""
    # Moving Averages on QQQ
    df_qqq['ema_20'] = df_qqq['close'].ewm(span=20, adjust=False).mean()
    df_qqq['ema_50'] = df_qqq['close'].ewm(span=50, adjust=False).mean()
    df_qqq['ema_200'] = df_qqq['close'].ewm(span=200, adjust=False).mean()
    
    # Bollinger Bands (20, 2)
    sma_20 = df_qqq['close'].rolling(window=20).mean()
    std_20 = df_qqq['close'].rolling(window=20).std()
    df_qqq['bb_upper'] = sma_20 + (2.0 * std_20)
    df_qqq['bb_lower'] = sma_20 - (2.0 * std_20)
    
    # RSI 14
    df_qqq['rsi_14'] = calculate_rsi(df_qqq['close'], period=14)
    
    # Stretch metrics
    df_qqq['dist_ema20_pct'] = ((df_qqq['close'] - df_qqq['ema_20']) / df_qqq['ema_20']) * 100.0
    df_qqq['dist_ema200_pct'] = ((df_qqq['close'] - df_qqq['ema_200']) / df_qqq['ema_200']) * 100.0
    
    # VIX
    df_qqq['vix'] = vix_series
    
    # TQQQ indicators
    df_tqqq['ema_20'] = df_tqqq['close'].ewm(span=20, adjust=False).mean()
    df_tqqq['ema_50'] = df_tqqq['close'].ewm(span=50, adjust=False).mean()
    df_tqqq['ema_200'] = df_tqqq['close'].ewm(span=200, adjust=False).mean()
    
    return df_qqq, df_tqqq


def simulate_trading_days(df_qqq: pd.DataFrame, df_tqqq: pd.DataFrame, lookback_days: int = 60):
    """
    Simulates the strategy on the last 60 trading days:
    - Allocation: $10,000 per trade (shares = floor(10000 / entry_price))
    - Days 1-5: Target +1.0% on TQQQ
    - Days 6-9: Break-Even defense (cover $5.00 IBKR commissions)
    - Day 10: Cut-off market exit
    """
    total_bars = len(df_qqq)
    if total_bars < 70:
        return []
    
    # Lookback window: last 60 trading days
    lookback = min(lookback_days, total_bars - 1)
    start_sim_idx = total_bars - lookback
    
    trades = []
    in_trade = False
    active_trade = {}
    
    for i in range(start_sim_idx, total_bars):
        current_date = df_qqq.index[i]
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Check active trade progression first
        if in_trade:
            entry_idx = active_trade['entry_bar_idx']
            bars_held = i - entry_idx
            entry_price = active_trade['tqqq_entry']
            shares = active_trade['shares']
            tqqq_high = df_tqqq['high'].iloc[i]
            tqqq_low = df_tqqq['low'].iloc[i]
            tqqq_close = df_tqqq['close'].iloc[i]
            
            # Days 1 to 5: Aiming for full +1.0%
            if 1 <= bars_held <= 5:
                target_price = round(entry_price * 1.01, 2)
                if tqqq_high >= target_price:
                    # Target hit!
                    exit_price = target_price
                    pnl_gross = round(shares * (exit_price - entry_price), 2)
                    commissions = 5.0  # IBKR: $2.50 buy + $2.50 sell
                    tax = round(max(0.0, pnl_gross - commissions) * 0.25, 2)
                    net_pnl = round(pnl_gross - commissions - tax, 2)
                    
                    active_trade.update({
                        'exit_date': date_str,
                        'exit_price': exit_price,
                        'bars_held': bars_held,
                        'status': 'יעד הושג (+1.0%)',
                        'outcome_type': 'TARGET_HIT',
                        'pnl_gross': pnl_gross,
                        'pnl_net': net_pnl,
                        'return_pct': 1.0
                    })
                    trades.append(active_trade)
                    in_trade = False
                    continue
            
            # Days 6 to 9: Break-even defense (cover $5.00 commissions)
            elif 6 <= bars_held <= 9:
                be_price = round(entry_price + (5.0 / shares), 2) if shares > 0 else round(entry_price * 1.0025, 2)
                if tqqq_high >= be_price:
                    # Break-even scratch hit
                    exit_price = be_price
                    pnl_gross = round(shares * (exit_price - entry_price), 2)
                    commissions = 5.0  # IBKR: $2.50 buy + $2.50 sell
                    tax = round(max(0.0, pnl_gross - commissions) * 0.25, 2)
                    net_pnl = round(pnl_gross - commissions - tax, 2)
                    
                    active_trade.update({
                        'exit_date': date_str,
                        'exit_price': exit_price,
                        'bars_held': bars_held,
                        'status': 'חילוץ באיזון',
                        'outcome_type': 'BREAK_EVEN',
                        'pnl_gross': pnl_gross,
                        'pnl_net': net_pnl,
                        'return_pct': round(((exit_price - entry_price) / entry_price) * 100, 2)
                    })
                    trades.append(active_trade)
                    in_trade = False
                    continue
            
            # Day 10: Cut-off market exit
            elif bars_held >= 10:
                exit_price = round(tqqq_close, 2)
                pnl_gross = round(shares * (exit_price - entry_price), 2)
                commissions = 5.0  # IBKR: $2.50 buy + $2.50 sell
                tax = round(max(0.0, pnl_gross - commissions) * 0.25, 2) if pnl_gross > commissions else 0.0
                net_pnl = round(pnl_gross - commissions - tax, 2)
                ret_pct = round(((exit_price - entry_price) / entry_price) * 100.0, 2)
                
                active_trade.update({
                    'exit_date': date_str,
                    'exit_price': exit_price,
                    'bars_held': bars_held,
                    'status': f'סגירת זמן יום 10 ({ret_pct:+.2f}%)',
                    'outcome_type': 'TIME_CUTOFF',
                    'pnl_gross': pnl_gross,
                    'pnl_net': net_pnl,
                    'return_pct': ret_pct
                })
                trades.append(active_trade)
                in_trade = False
                continue
        
        # If not in trade, check for entry signal on day i
        if not in_trade:
            qqq_close = df_qqq['close'].iloc[i]
            qqq_open = df_qqq['open'].iloc[i]
            qqq_ema20 = df_qqq['ema_20'].iloc[i]
            qqq_ema200 = df_qqq['ema_200'].iloc[i]
            qqq_bb_lower = df_qqq['bb_lower'].iloc[i]
            qqq_rsi = df_qqq['rsi_14'].iloc[i]
            vix = df_qqq['vix'].iloc[i]
            
            # Rule 1: Bull regime (QQQ > EMA 200)
            cond_regime = qqq_close > qqq_ema200
            
            # Rule 2: Stretch below EMA 20 (>= 1.0%) OR at/below lower Bollinger Band
            dist_ema20 = ((qqq_close - qqq_ema20) / qqq_ema20) * 100.0
            cond_stretch = (dist_ema20 <= -1.0) or (qqq_close <= qqq_bb_lower * 1.002)
            
            # Rule 3: RSI oversold / tension (RSI <= 50)
            cond_rsi = qqq_rsi <= 50.0
            
            # Rule 4: Pure Dip Buying (no reversal candle needed)
            
            # Rule 5: No Black Swan (VIX < 35 and QQQ > EMA 200 * 0.97)
            cond_no_black_swan = (vix < 35.0) and (qqq_close >= qqq_ema200 * 0.97)
            
            if cond_regime and cond_stretch and cond_rsi and cond_no_black_swan:
                # Trigger Entry
                tqqq_entry = round(df_tqqq['close'].iloc[i], 2)
                shares = int(10000.0 / tqqq_entry) if tqqq_entry > 0 else 0
                allocated = round(shares * tqqq_entry, 2)
                
                in_trade = True
                active_trade = {
                    'entry_date': date_str,
                    'entry_bar_idx': i,
                    'qqq_entry': round(qqq_close, 2),
                    'tqqq_entry': tqqq_entry,
                    'shares': shares,
                    'allocated_usd': allocated,
                    'dist_ema20_at_entry': round(dist_ema20, 2),
                    'rsi_at_entry': round(qqq_rsi, 1)
                }
    
    # If still in trade at the latest bar
    if in_trade:
        latest_idx = total_bars - 1
        bars_held = latest_idx - active_trade['entry_bar_idx']
        curr_price = round(df_tqqq['close'].iloc[-1], 2)
        entry_price = active_trade['tqqq_entry']
        shares = active_trade['shares']
        pnl_gross = round(shares * (curr_price - entry_price), 2)
        ret_pct = round(((curr_price - entry_price) / entry_price) * 100.0, 2)
        
        active_trade.update({
            'exit_date': 'פתוחה כעת (Open)',
            'exit_price': curr_price,
            'bars_held': bars_held,
            'status': f'פוזיציה פעילה ({ret_pct:+.2f}%)',
            'outcome_type': 'OPEN',
            'pnl_gross': pnl_gross,
            'pnl_net': round(pnl_gross - 3.0, 2),
            'return_pct': ret_pct
        })
        trades.append(active_trade)
        
    return trades


def analyze_market():
    """Run full analysis on QQQ and TQQQ and return executive state."""
    df_qqq, df_tqqq, vix_series = fetch_strategy_data()
    df_qqq, df_tqqq = compute_indicators(df_qqq, df_tqqq, vix_series)
    
    # Latest data point
    latest_date = df_qqq.index[-1].strftime('%Y-%m-%d')
    qqq_close = round(float(df_qqq['close'].iloc[-1]), 2)
    qqq_open = round(float(df_qqq['open'].iloc[-1]), 2)
    qqq_change = round(float(((df_qqq['close'].iloc[-1] - df_qqq['close'].iloc[-2]) / df_qqq['close'].iloc[-2]) * 100.0), 2)
    
    tqqq_close = round(float(df_tqqq['close'].iloc[-1]), 2)
    tqqq_change = round(float(((df_tqqq['close'].iloc[-1] - df_tqqq['close'].iloc[-2]) / df_tqqq['close'].iloc[-2]) * 100.0), 2)
    
    vix_val = round(float(df_qqq['vix'].iloc[-1]), 2)
    
    ema_20 = round(float(df_qqq['ema_20'].iloc[-1]), 2)
    ema_50 = round(float(df_qqq['ema_50'].iloc[-1]), 2)
    ema_200 = round(float(df_qqq['ema_200'].iloc[-1]), 2)
    rsi_14 = round(float(df_qqq['rsi_14'].iloc[-1]), 1)
    dist_ema20 = round(float(df_qqq['dist_ema20_pct'].iloc[-1]), 2)
    dist_ema200 = round(float(df_qqq['dist_ema200_pct'].iloc[-1]), 2)
    bb_lower = round(float(df_qqq['bb_lower'].iloc[-1]), 2)
    
    # Committee Rule Checks
    rule_regime = qqq_close > ema_200
    rule_stretch = (dist_ema20 <= -1.0) or (qqq_close <= bb_lower * 1.002)
    rule_rsi = rsi_14 <= 50.0
    rule_black_swan = (vix_val >= 35.0) or (qqq_close < ema_200 * 0.97)
    
    if rule_black_swan:
        status_label = "⚠️ BLACK SWAN VETO"
        status_color = "#e53e3e"
        verdict_he = "התראת ברבור שחור! רמת סיכון קיצונית במדד - מסחר מושבת"
        action_allowed = False
    elif not rule_regime:
        status_label = "🔴 VETO (BEAR REGIME)"
        status_color = "#e53e3e"
        verdict_he = "וטו משטר שוק: QQQ נסחר מתחת ל-EMA 200 (ללא כניסות לונג במגמה דובית)"
        action_allowed = False
    elif rule_stretch and rule_rsi:
        status_label = "🟢 BUY SIGNAL (TQQQ)"
        status_color = "#38a169"
        verdict_he = "איתות כניסה מאושר! מתיחת דיפ מובהקת מתחת ל-EMA 20 ו-RSI תומך (קנייה ישירה בסגירה)"
        action_allowed = True
    else:
        status_label = "⚪ NO SETUP (HOLD CASH)"
        status_color = "#718096"
        verdict_he = "אין מתיחה כרגע - המדד קרוב לממוצע נע או מעליו. ממתינים לדיפ"
        action_allowed = False

    # Trade Plan Calculation (Based on actual entry price & exact actual capital allocated)
    entry_price = tqqq_close
    shares = int(10000.0 / entry_price) if entry_price > 0 else 0
    allocated_usd = round(shares * entry_price, 2)
    target_1pct_price = round(entry_price * 1.01, 2)
    per_share_gain = round(target_1pct_price - entry_price, 2)
    gross_target_profit = round(shares * per_share_gain, 2)
    
    # Commissions: IBKR Israel $2.50 buy + $2.50 sell = $5.00 total roundtrip
    commissions = 5.0
    taxable_gain = max(0.0, gross_target_profit - commissions)
    tax_israel = round(taxable_gain * 0.25, 2)
    net_profit = round(gross_target_profit - commissions - tax_israel, 2)
    
    # Exact break-even exit price covering IBKR commissions
    per_share_comm = (commissions / shares) if shares > 0 else 0.04
    be_price = round(entry_price + per_share_comm, 2)
    
    trade_plan = {
        'capital_usd': 10000.0,
        'tqqq_price': entry_price,
        'shares': shares,
        'allocated_usd': allocated_usd,
        'target_1pct_price': target_1pct_price,
        'per_share_gain': per_share_gain,
        'target_gross_profit': gross_target_profit,
        'break_even_price': be_price,
        'commissions_est': commissions,
        'tax_israel_est': tax_israel,
        'net_pocket_profit': net_profit
    }
    
    # Run 45-day simulation
    sim_trades = simulate_trading_days(df_qqq, df_tqqq, lookback_days=45)
    
    # 45-day summary statistics
    closed_trades = [t for t in sim_trades if t.get('outcome_type') != 'OPEN']
    wins = [t for t in closed_trades if t.get('return_pct', 0) > 0]
    total_trades_count = len(sim_trades)
    win_rate = round((len(wins) / len(closed_trades) * 100.0), 1) if closed_trades else 0.0
    total_net_pnl = round(sum(t.get('pnl_net', 0) for t in sim_trades), 2)
    avg_hold_days = round(float(np.mean([t['bars_held'] for t in sim_trades])), 1) if sim_trades else 0.0
    
    sim_summary = {
        'total_trades': total_trades_count,
        'closed_trades': len(closed_trades),
        'winning_trades': len(wins),
        'win_rate_pct': win_rate,
        'total_net_pnl_usd': total_net_pnl,
        'avg_hold_days': avg_hold_days
    }
    
    # Prepare candlestick and markers data for TradingView chart (TQQQ traded asset - 55 bars for clean spacing)
    chart_bars = []
    chart_df_qqq = df_qqq.iloc[-55:].copy()
    chart_df_tqqq = df_tqqq.iloc[-55:].copy()
    
    for idx, tqqq_row in chart_df_tqqq.iterrows():
        qqq_row = chart_df_qqq.loc[idx] if idx in chart_df_qqq.index else None
        bar_item = {
            'time': idx.strftime('%Y-%m-%d'),
            'open': round(float(tqqq_row['open']), 2),
            'high': round(float(tqqq_row['high']), 2),
            'low': round(float(tqqq_row['low']), 2),
            'close': round(float(tqqq_row['close']), 2),
            'ema20': round(float(tqqq_row['ema_20']), 2),
            'ema50': round(float(tqqq_row['ema_50']), 2),
            'ema200': round(float(tqqq_row['ema_200']), 2),
            'qqq_close': round(float(qqq_row['close']), 2) if qqq_row is not None else 0.0,
            'qqq_ema20': round(float(qqq_row['ema_20']), 2) if qqq_row is not None else 0.0
        }
        chart_bars.append(bar_item)
        
    return {
        'as_of_date': latest_date,
        'market_data': {
            'qqq_close': qqq_close,
            'qqq_change': qqq_change,
            'tqqq_close': tqqq_close,
            'tqqq_change': tqqq_change,
            'vix': vix_val,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'ema_200': ema_200,
            'rsi_14': rsi_14,
            'dist_ema20_pct': dist_ema20,
            'dist_ema200_pct': dist_ema200
        },
        'committee_verdict': {
            'status_label': status_label,
            'status_color': status_color,
            'verdict_he': verdict_he,
            'action_allowed': action_allowed,
            'rules': {
                'regime_bull_ema200': {'passed': bool(rule_regime), 'desc': f'QQQ מעל EMA 200 ({ema_200})'},
                'stretch_ema20': {'passed': bool(rule_stretch), 'desc': f'מתיחה מתחת ל-EMA 20 ({dist_ema20:+.1f}%)'},
                'rsi_tension': {'passed': bool(rule_rsi), 'desc': f'מתנד RSI(14) מתחת ל-50 ({rsi_14})'},
                'pure_dip_execution': {'passed': True, 'desc': 'קניית דיפ ישירה בסגירה (Pure Dip Buying)'},
                'no_black_swan': {'passed': bool(not rule_black_swan), 'desc': f'סביבת סיכון רגועה (VIX {vix_val})'}
            }
        },
        'trade_plan': trade_plan,
        'simulation': {
            'summary': sim_summary,
            'trades': sim_trades
        },
        'chart_data': chart_bars
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="QQQ Volatility Strategy Engine")
    parser.add_argument('--json', action='store_true', help="Output pure JSON")
    args = parser.parse_args()
    
    try:
        results = analyze_market()
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"\n=======================================================")
            print(f"🎯 ועדת השקעות QQQ Volatility (ביצוע ממונף ב-TQQQ)")
            print(f"תאריך נתונים: {results['as_of_date']}")
            print(f"סטטוס: {results['committee_verdict']['status_label']}")
            print(f"החלטת ועדה: {results['committee_verdict']['verdict_he']}")
            print(f"-------------------------------------------------------")
            print(f"QQQ: ${results['market_data']['qqq_close']} ({results['market_data']['qqq_change']:+.2f}%) | EMA 20: ${results['market_data']['ema_20']} | RSI: {results['market_data']['rsi_14']}")
            print(f"TQQQ: ${results['market_data']['tqqq_close']} ({results['market_data']['tqqq_change']:+.2f}%) | VIX: {results['market_data']['vix']}")
            print(f"-------------------------------------------------------")
            tp = results['trade_plan']
            print(f"תוכנית הטרייד ($10,000):")
            print(f"  • כמות מניות: {tp['shares']} מניות (הקצאה: ${tp['allocated_usd']})")
            print(f"  • יעד רווח 1%+: ${tp['target_1pct_price']} (רווח נקי משוער: ${tp['net_pocket_profit']})")
            print(f"  • שער חילוץ באיזון: ${tp['break_even_price']}")
            print(f"-------------------------------------------------------")
            sim = results['simulation']['summary']
            print(f"ביצועי 45 ימי מסחר אחרונים:")
            print(f"  • סה\"כ עסקאות: {sim['total_trades']} | אחוז הצלחה: {sim['win_rate_pct']}%")
            print(f"  • רווח נקי מצטבר: ${sim['total_net_pnl_usd']} | זמן החזקה ממוצע: {sim['avg_hold_days']} ימים")
            print(f"=======================================================\n")
    except Exception as e:
        print(f"Error executing engine: {str(e)}", file=sys.stderr)
        sys.exit(1)
