"""
Swing Simulation Chart Generator (TradingView Dark Theme)
Generates high-resolution candlestick charts with projected "Long Position" setup boxes:
- 45 trading days history with Candlesticks
- EMA 20 (Cyan) and EMA 50 (Gold)
- Projected 10-day swing horizon:
  - Active: Green profit box (Target), Red loss box (Stop), White dashed Entry line with price badges
  - Avoid: Amber hatched No Man's Land box, EMA 20 barrier line
"""

import os
import sys
import shutil
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Default brain artifact directory if active
ARTIFACTS_DIR = r"C:\Users\aviba\.gemini\antigravity\brain\5dfab7ef-76a3-4612-8cc7-1106a637d084"

def generate_swing_simulation_chart(
    ticker: str,
    entry_price: float,
    stop_price: float,
    target_price: float,
    output_path: str,
    horizon_days: int = 10,
    is_avoid: bool = False,
    avoid_reason: str = "",
    disaster_stop_price: float = None,
    target1_price: float = None
) -> str:
    """
    Generates a dark-themed chart simulation image and saves it to output_path.
    Supports hybrid stop architecture (Tactical TV Alert + IBKR Hard Disaster Stop)
    and dual profit targets (TP1 Scale-Out + TP2 Full Target).
    Returns the absolute path to the generated image.
    """
    try:
        # Fetch 60 days of daily data
        df = yf.download(ticker, period="4mo", interval="1d", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            if ticker in df.columns.get_level_values(0):
                df = df.xs(ticker, axis=1, level=0)
            elif ticker in df.columns.get_level_values(1):
                df = df.xs(ticker, axis=1, level=1)
            else:
                df.columns = df.columns.get_level_values(0)

        # Enrich latest candle if it contains NaN before dropping
        if len(df) > 0 and pd.isna(df['Close'].iloc[-1]):
            try:
                t = yf.Ticker(ticker)
                fi = t.fast_info
                last_p = getattr(fi, 'last_price', None)
                open_p = getattr(fi, 'open', last_p)
                high_p = getattr(fi, 'day_high', max(open_p, last_p) if open_p and last_p else None)
                low_p = getattr(fi, 'day_low', min(open_p, last_p) if open_p and last_p else None)
                if last_p is not None and not np.isnan(last_p):
                    df.iloc[-1, df.columns.get_loc('Close')] = last_p
                    df.iloc[-1, df.columns.get_loc('Open')] = open_p if open_p is not None else last_p
                    df.iloc[-1, df.columns.get_loc('High')] = high_p if high_p is not None else last_p
                    df.iloc[-1, df.columns.get_loc('Low')] = low_p if low_p is not None else last_p
            except Exception:
                pass

        df = df.dropna().iloc[-45:] # Last 45 trading days
        
        if len(df) < 20:
            raise ValueError(f"Insufficient historical data for {ticker}")

        # Calculate indicators
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # Figure setup (Dark High-Tech TradingView Theme)
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(11, 5.2), dpi=150)
        fig.patch.set_facecolor('#0d1117')
        ax.set_facecolor('#0d1117')
        
        n_bars = len(df)
        x_vals = np.arange(n_bars)
        
        # Plot Candlesticks
        candle_width = 0.6
        wick_width = 1.2
        
        for i in range(n_bars):
            open_p = df['Open'].iloc[i]
            close_p = df['Close'].iloc[i]
            high_p = df['High'].iloc[i]
            low_p = df['Low'].iloc[i]
            
            color = '#10b981' if close_p >= open_p else '#ef4444' # Green / Red
            
            # Wick
            ax.plot([i, i], [low_p, high_p], color=color, linewidth=wick_width, zorder=2)
            # Body
            body_bottom = min(open_p, close_p)
            body_height = max(abs(close_p - open_p), 0.02)
            rect = patches.Rectangle((i - candle_width/2, body_bottom), candle_width, body_height,
                                     facecolor=color, edgecolor=color, zorder=3)
            ax.add_patch(rect)
            
        # Plot EMAs
        ax.plot(x_vals, df['EMA20'], color='#38bdf8', linewidth=1.5, label='EMA 20', zorder=4)
        ax.plot(x_vals, df['EMA50'], color='#fbbf24', linewidth=1.5, label='EMA 50', zorder=4)
        
        # Simulation Projection Zone
        future_start = n_bars - 1
        future_end = future_start + horizon_days
        
        risk = entry_price - stop_price
        reward = target_price - entry_price
        risk_pct = (risk / entry_price) * 100
        reward_pct = (reward / entry_price) * 100
        rr_ratio = reward / max(0.01, risk)
        
        if not is_avoid:
            # 1. Green Profit Target Box
            profit_rect = patches.Rectangle(
                (future_start, entry_price), horizon_days, reward,
                facecolor='#10b981', alpha=0.18, edgecolor='#10b981', linestyle='--', linewidth=1.2, zorder=1
            )
            ax.add_patch(profit_rect)
            
            # 2. Red Risk Stop Box (Tactical Alert Zone)
            loss_rect = patches.Rectangle(
                (future_start, stop_price), horizon_days, -risk if risk < 0 else risk,
                facecolor='#ef4444', alpha=0.18, edgecolor='#ef4444', linestyle='--', linewidth=1.2, zorder=1
            )
            ax.add_patch(loss_rect)
            
            # Guide Lines & Badges
            # Entry Line
            ax.axhline(entry_price, color='#ffffff', linestyle=':', linewidth=1.2, alpha=0.85)
            ax.text(future_end + 0.3, entry_price, f' Entry ${entry_price:.2f}', color='#ffffff',
                    va='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#1f2937', edgecolor='#ffffff', alpha=0.9))
            
            # Target 1 (TP1 50% Scale-Out) if provided
            if target1_price and entry_price < target1_price < target_price:
                tp1_reward = target1_price - entry_price
                tp1_pct = (tp1_reward / entry_price) * 100
                ax.axhline(target1_price, color='#34d399', linestyle='--', linewidth=1.3, alpha=0.9)
                ax.text(future_end + 0.3, target1_price, f' TP1 ${target1_price:.2f} (+{tp1_pct:.1f}% [50% Scale-Out])',
                        color='#34d399', va='center', fontsize=8.5, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#064e3b', edgecolor='#34d399', alpha=0.9))

            # Target 2 (TP2 Full Target)
            target_tag = f' TP2 Full ${target_price:.2f} (+{reward_pct:.1f}% | R:R 1:{rr_ratio:.2f})' if target1_price else f' Target ${target_price:.2f} (+{reward_pct:.1f}% | R:R 1:{rr_ratio:.2f})'
            ax.axhline(target_price, color='#10b981', linestyle='--', linewidth=1.5)
            ax.text(future_end + 0.3, target_price, target_tag, color='#10b981',
                    va='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#064e3b', edgecolor='#10b981', alpha=0.9))
            
            # Stop Line (Layer 1: Tactical TV Alert)
            stop_tag = ' TV Alert' if disaster_stop_price else ' Stop'
            ax.axhline(stop_price, color='#ef4444', linestyle='--', linewidth=1.5)
            ax.text(future_end + 0.3, stop_price, f'{stop_tag} ${stop_price:.2f} (-{risk_pct:.1f}%)', color='#ef4444',
                    va='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#7f1d1d', edgecolor='#ef4444', alpha=0.9))
            
            # Layer 2: Hard Disaster Stop Line (if specified)
            if disaster_stop_price and disaster_stop_price < stop_price:
                disaster_risk = entry_price - disaster_stop_price
                disaster_risk_pct = (disaster_risk / entry_price) * 100
                ax.axhline(disaster_stop_price, color='#f43f5e', linestyle=':', linewidth=1.3, alpha=0.85)
                ax.text(future_end + 0.3, disaster_stop_price, f' IBKR Hard Stop ${disaster_stop_price:.2f} (-{disaster_risk_pct:.1f}%)', color='#fca5a5',
                        va='center', fontsize=8.5, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#4c0519', edgecolor='#f43f5e', alpha=0.85))
                
            # Ensure vertical scaling includes all critical levels
            lowest_bound = disaster_stop_price if (disaster_stop_price and disaster_stop_price < stop_price) else stop_price
            min_y = min(df['Low'].min(), lowest_bound) * 0.985
            max_y = max(df['High'].max(), target_price) * 1.015
            ax.set_ylim(min_y, max_y)
        else:
            # AVOID / NO MAN'S LAND SIMULATION
            curr_price = df['Close'].iloc[-1]
            ema20_curr = df['EMA20'].iloc[-1]
            
            trap_rect = patches.Rectangle(
                (future_start, min(curr_price, ema20_curr)), horizon_days, abs(ema20_curr - curr_price),
                facecolor='#f59e0b', alpha=0.2, edgecolor='#f59e0b', hatch='//', linestyle='--', linewidth=1.2, zorder=1
            )
            ax.add_patch(trap_rect)
            
            ax.axhline(ema20_curr, color='#38bdf8', linestyle='--', linewidth=1.5)
            ax.text(future_end + 0.3, ema20_curr, f' EMA 20 Barrier (${ema20_curr:.2f})', color='#38bdf8',
                    va='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#0c4a6e', edgecolor='#38bdf8', alpha=0.9))
                    
            ax.text(future_start + horizon_days/2, (curr_price + ema20_curr)/2, 'No Man\'s Land (Avoid)',
                    color='#f59e0b', ha='center', va='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#451a03', edgecolor='#f59e0b', alpha=0.9))

        # Formatting
        ax.set_xlim(-1, future_end + 5.5)
        
        sample_indices = np.linspace(0, n_bars - 1, 6, dtype=int)
        date_labels = [df.index[i].strftime('%d/%m') for i in sample_indices]
        ax.set_xticks(sample_indices)
        ax.set_xticklabels(date_labels, color='#94a3b8', fontsize=8)
        
        ax.tick_params(colors='#94a3b8', labelsize=8)
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position("right")
        ax.grid(True, linestyle=':', alpha=0.15, color='#ffffff')
        
        # Professional English title on image to ensure flawless cross-platform font rendering
        title_suffix = "Swing Setup Simulation (Long Position)" if not is_avoid else "No Man's Land Trap — Avoid Simulation"
        ax.set_title(f"{ticker} — {title_suffix}", color='#f8fafc', fontsize=12, fontweight='bold', pad=12, loc='right')
        
        ax.legend(loc='upper left', framealpha=0.3, fontsize=8)
        plt.tight_layout()
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close()
        
        # Also copy to artifacts dir if available
        try:
            if os.path.exists(ARTIFACTS_DIR):
                art_target = os.path.join(ARTIFACTS_DIR, os.path.basename(output_path))
                shutil.copy2(output_path, art_target)
        except Exception:
            pass

        return output_path

    except Exception as e:
        print(f"[-] Warning: Failed to generate chart simulation: {e}")
        return ""
