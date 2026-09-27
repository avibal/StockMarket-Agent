"""
QQQ Volatility Report Generator
Produces an executive RTL HTML report featuring TradingView Lightweight Charts,
concise strategy rules, market metrics audit, and a 30-day trade simulation table.
"""

import os
import sys
import json
from datetime import datetime

# Add project root to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from strategies.qqq_volatility.engine import analyze_market


def generate_html_report(data: dict) -> str:
    """Generate self-contained RTL HTML report with embedded TradingView chart."""
    as_of = data['as_of_date']
    m = data['market_data']
    v = data['committee_verdict']
    tp = data['trade_plan']
    sim = data['simulation']
    trades = sim['trades']
    chart_bars = data['chart_data']
    
    # Build chart markers for entries and exits
    markers = []
    for trade in trades:
        # Entry marker
        markers.append({
            'time': trade['entry_date'],
            'position': 'belowBar',
            'color': '#38a169',
            'shape': 'arrowUp',
            'text': f"כניסה TQQQ (${trade['tqqq_entry']})"
        })
        # Exit marker if closed
        if trade['exit_date'] != 'פתוחה כעת (Open)':
            is_win = trade.get('return_pct', 0) > 0
            outcome = trade.get('outcome_type', '')
            if outcome == 'TARGET_HIT':
                color = '#d69e2e'
                shape = 'circle'
                text = f"יעד +1% (${trade['exit_price']})"
            elif outcome == 'BREAK_EVEN':
                color = '#3182ce'
                shape = 'arrowDown'
                text = f"איזון (${trade['exit_price']})"
            else:
                color = '#e53e3e' if not is_win else '#38a169'
                shape = 'arrowDown'
                text = f"סגירה יום 10 (${trade['exit_price']})"
                
            markers.append({
                'time': trade['exit_date'],
                'position': 'aboveBar',
                'color': color,
                'shape': shape,
                'text': text
            })
            
    # Sort markers chronologically
    markers = sorted(markers, key=lambda x: x['time'])
    
    # Generate trade table rows
    trade_rows_html = ""
    if not trades:
        trade_rows_html = "<tr><td colspan='8' style='text-align:center; padding:15px; color:#a0aec0;'>לא נוצרו עסקאות ב-45 ימי המסחר האחרונים (תנאי הסף לא התממשו).</td></tr>"
    else:
        for idx, t in enumerate(trades, 1):
            ret = t.get('return_pct', 0)
            ret_color = "#38a169" if ret > 0 else ("#e53e3e" if ret < 0 else "#a0aec0")
            ret_badge = f"<span style='color:{ret_color}; font-weight:bold;'>{ret:+.2f}%</span>"
            pnl_net = t.get('pnl_net', 0)
            pnl_color = "#38a169" if pnl_net > 0 else ("#e53e3e" if pnl_net < 0 else "#a0aec0")
            
            trade_rows_html += f"""
            <tr style="border-bottom: 1px solid #2d3748;">
                <td style="padding: 10px 12px; font-weight: 600;">#{idx}</td>
                <td style="padding: 10px 12px;">{t['entry_date']}</td>
                <td style="padding: 10px 12px; direction:ltr; text-align:right;">${t['tqqq_entry']}</td>
                <td style="padding: 10px 12px;">{t['exit_date']}</td>
                <td style="padding: 10px 12px; direction:ltr; text-align:right;">${t.get('exit_price', '-')}</td>
                <td style="padding: 10px 12px; text-align:center;">{t.get('bars_held', 0)} ימים</td>
                <td style="padding: 10px 12px; text-align:center;">{ret_badge}</td>
                <td style="padding: 10px 12px; text-align:center; color:{pnl_color}; font-weight: bold;">${pnl_net:+.2f}</td>
            </tr>
            """
            
    # Audit rules list
    audit_html = ""
    for k, r in v['rules'].items():
        icon = "✅" if r['passed'] else "❌"
        badge_class = "pass-badge" if r['passed'] else "fail-badge"
        audit_html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:#1a202c; border-radius:8px; margin-bottom:8px; border:1px solid #2d3748;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:16px;">{icon}</span>
                <span style="font-weight:600; color:#e2e8f0;">{r['desc']}</span>
            </div>
            <span style="font-size:12px; padding:3px 10px; border-radius:12px; font-weight:bold; background:{'#22543d' if r['passed'] else '#742a2a'}; color:{'#9ae6b4' if r['passed'] else '#feb2b2'};">
                {'מאושר' if r['passed'] else 'לא התקיים'}
            </span>
        </div>
        """

    # Build Trade Plan Card HTML dynamically based on committee action_allowed
    is_active = v.get('action_allowed', False)
    if is_active:
        trade_plan_card_html = f"""
        <!-- Trade Plan (ACTIVE) -->
        <div class="card" style="border-right: 4px solid var(--accent-green);">
            <div class="card-header" style="color:var(--accent-green); justify-content:space-between;">
                <span>🚀 תוכנית מסחר פעילה ב-TQQQ ($10,000)</span>
                <span style="font-size:12px; background:#166534; color:#86efac; padding:2px 8px; border-radius:4px; font-weight:bold;">🟢 איתות קנייה מאושר</span>
            </div>

            <!-- Active Banner -->
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px 12px; margin-bottom: 14px; font-size: 13px; color: #86efac;">
                <strong>⚡ איתות דיפ מאושר בסגירה:</strong> תנאי הסף התקיימו. פקודה מומלצת לשידור לקראת נעילת המסחר.
            </div>

            <div class="metric-row">
                <span class="metric-label">מסגרת תקציב מירבית</span>
                <span class="metric-val" style="color:var(--text-muted);">$10,000.00</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">🟢 מחיר כניסה מומלץ (TQQQ בסגירה)</span>
                <span class="metric-val" style="color:#38bdf8; font-size:15px; font-weight:bold;">${tp['tqqq_price']:.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">כמות מניות מחושבת</span>
                <span class="metric-val">{tp['shares']} מניות</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">💵 סך הון מוקצה בפועל לטרייד</span>
                <span class="metric-val" style="color:var(--accent-green); font-weight:bold;">${tp['allocated_usd']:,.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">🎯 מחיר יציאה מתוכנן ביעד 1.0%+</span>
                <span class="metric-val" style="color:var(--accent-amber); font-size:15px; font-weight:bold;">${tp['target_1pct_price']:.2f} (+${tp['per_share_gain']:.2f}$/מניה)</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">רווח גולמי מחושב לפי ההקצאה בפועל</span>
                <span class="metric-val" style="color:#cbd5e1; font-weight:bold;">+${tp['target_gross_profit']:.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">עמלות מסחר IBKR ($2.50 קנייה + $2.50 מכירה)</span>
                <span class="metric-val" style="color:#f87171;">-${tp['commissions_est']:.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">מס רווחי הון בישראל (25% מרווח בניכוי עמלות)</span>
                <span class="metric-val" style="color:#f87171;">-${tp['tax_israel_est']:.2f}</span>
            </div>
            <div class="metric-row" style="background:rgba(16, 185, 129, 0.1); padding:10px 8px; border-radius:6px; margin-top:4px;">
                <span class="metric-label" style="color:var(--accent-green); font-weight:bold;">💰 רווח נקי סופי לכיס (Net Profit)</span>
                <span class="metric-val" style="color:var(--accent-green); font-size:17px; font-weight:800;">+${tp['net_pocket_profit']:.2f}</span>
            </div>
            <div class="metric-row" style="margin-top:6px; border-top:1px dashed #334155;">
                <span class="metric-label">🛡️ שער חילוץ באיזון (כיסוי $5 עמלות ברוקר)</span>
                <span class="metric-val" style="color:#94a3b8;">${tp['break_even_price']:.2f}</span>
            </div>

            <!-- Execution Directives (אופן ביצוע) -->
            <div style="margin-top: 14px; background: rgba(15, 23, 42, 0.7); border: 1px solid #10b981; border-radius: 8px; padding: 12px 14px;">
                <div style="font-size: 13px; font-weight: 700; color: #34d399; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px;">
                    <span>⚡ אופן ביצוע (הוראות שידור פקודה ב-IBKR)</span>
                    <span style="font-size: 11px; background: #065f46; color: #a7f3d0; padding: 2px 8px; border-radius: 4px;">🟢 פקודה לשידור</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 6px; font-size: 13px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">סוג פקודה ראשי:</span>
                        <span style="font-weight: 700; color: #f8fafc; direction: ltr;">Buy Limit</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">שער לימיט לקנייה:</span>
                        <span style="font-weight: 700; color: #38bdf8; direction: ltr;">${tp['tqqq_price']:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">כמות מניות לשידור:</span>
                        <span style="font-weight: 700; color: #f8fafc; direction: ltr;">{tp['shares']} מניות (${tp['allocated_usd']:,.2f})</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">הוראה נלווית (Attach):</span>
                        <span style="font-weight: 700; color: var(--accent-amber); direction: ltr;">Profit Taker (Limit) @ ${tp['target_1pct_price']:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">סטופ לוס (SL מוצמד):</span>
                        <span style="font-weight: 700; color: #94a3b8;">ללא (ניהול לפי סטופ זמן מדורג)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">תוקף הפקודה (Time in Force):</span>
                        <span style="font-weight: 700; color: #f8fafc; direction: ltr;">GTC (Good-Til-Canceled)</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 4px; padding-top: 6px; border-top: 1px dashed rgba(255,255,255,0.1);">
                        <span style="color: var(--text-muted);">חלון שיגור מומלץ:</span>
                        <span style="font-weight: 700; color: var(--accent-green); direction: ltr;">22:45 – 22:50 (שעון ישראל)</span>
                    </div>
                </div>
            </div>
        </div>
        """
    else:
        trade_plan_card_html = f"""
        <!-- Trade Plan (STANDBY / NO ACTION) -->
        <div class="card" style="border-right: 4px solid #64748b;">
            <div class="card-header" style="color:#94a3b8; justify-content:space-between;">
                <span>💼 תוכנית מסחר ב-TQQQ ($10,000)</span>
                <span style="font-size:12px; background:#334155; color:#cbd5e1; padding:2px 8px; border-radius:4px; font-weight:bold;">⏸️ מצב המתנה (Standby)</span>
            </div>

            <!-- Standby Warning / Notice -->
            <div style="background: rgba(51, 65, 85, 0.4); border: 1px solid #475569; border-radius: 8px; padding: 12px 14px; margin-bottom: 14px; font-size: 13px;">
                <div style="font-weight: 700; color: #f8fafc; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                    <span>⏸️ אין לפעול כעת — התיק נשאר ב-100% מזומן (Cash)</span>
                </div>
                <div style="color: #cbd5e1; font-size: 12px; line-height: 1.5;">
                    מדד הייחוס QQQ אינו במצב דיפ ({m['dist_ema20_pct']:+.2f}% מ-EMA 20, RSI={m['rsi_14']}).<br>
                    הפרמטרים מטה מוצגים כ<strong>סימולטור תיאורטי בלבד</strong> להמחשת מודל ההקצאה.
                </div>
            </div>

            <div class="metric-row">
                <span class="metric-label">מסגרת תקציב מירבית</span>
                <span class="metric-val" style="color:var(--text-muted);">$10,000.00</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">⚪ שער TQQQ בסגירה אחרונה (ייחוס)</span>
                <span class="metric-val" style="color:#94a3b8; font-size:15px; font-weight:bold;">${tp['tqqq_price']:.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">כמות מניות מחושבת בתקציב</span>
                <span class="metric-val">{tp['shares']} מניות</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">💵 סך הון שיוקצה בעת כניסה</span>
                <span class="metric-val" style="color:#94a3b8; font-weight:bold;">${tp['allocated_usd']:,.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">🎯 מחיר יציאה מתוכנן ביעד 1.0%+</span>
                <span class="metric-val" style="color:#94a3b8; font-size:15px; font-weight:bold;">${tp['target_1pct_price']:.2f} (+${tp['per_share_gain']:.2f}$/מניה)</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">רווח גולמי משוער לפי ההקצאה</span>
                <span class="metric-val" style="color:#cbd5e1; font-weight:bold;">+${tp['target_gross_profit']:.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">עמלות מסחר IBKR ($2.50 קנייה + $2.50 מכירה)</span>
                <span class="metric-val" style="color:#f87171;">-${tp['commissions_est']:.2f}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">מס רווחי הון בישראל (25% מרווח בניכוי עמלות)</span>
                <span class="metric-val" style="color:#f87171;">-${tp['tax_israel_est']:.2f}</span>
            </div>
            <div class="metric-row" style="background:rgba(51, 65, 85, 0.2); padding:10px 8px; border-radius:6px; margin-top:4px;">
                <span class="metric-label" style="color:#cbd5e1; font-weight:bold;">💰 רווח נקי משוער לכיס (Net Profit)</span>
                <span class="metric-val" style="color:#cbd5e1; font-size:17px; font-weight:800;">+${tp['net_pocket_profit']:.2f}</span>
            </div>
            <div class="metric-row" style="margin-top:6px; border-top:1px dashed #334155;">
                <span class="metric-label">🛡️ שער חילוץ באיזון (כיסוי $5 עמלות ברוקר)</span>
                <span class="metric-val" style="color:#94a3b8;">${tp['break_even_price']:.2f}</span>
            </div>

            <!-- Execution Directives (אופן ביצוע - מושבת) -->
            <div style="margin-top: 14px; background: rgba(15, 23, 42, 0.6); border: 1px solid #334155; border-radius: 8px; padding: 12px 14px;">
                <div style="font-size: 13px; font-weight: 700; color: #94a3b8; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 6px;">
                    <span>⚡ אופן ביצוע ב-IBKR (סימולטור תיאורטי)</span>
                    <span style="font-size: 11px; background: #475569; color: #f1f5f9; padding: 2px 8px; border-radius: 4px;">🚫 פקודה מושבתת</span>
                </div>
                <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 8px 10px; margin-bottom: 10px; font-size: 12px; color: #fca5a5; font-weight: bold; text-align: center;">
                    ⛔ סטטוס פקודה: מושבתת (Disabled) — אין לשדר שום פקודה לבורסה!
                </div>
                <div style="display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: #94a3b8;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">סוג פקודה במודל:</span>
                        <span style="font-weight: 600; color: #cbd5e1; direction: ltr;">Buy Limit</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">שער לחישוב תיאורטי:</span>
                        <span style="font-weight: 600; color: #cbd5e1; direction: ltr;">${tp['tqqq_price']:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">כמות מניות מוקצית:</span>
                        <span style="font-weight: 600; color: #cbd5e1; direction: ltr;">{tp['shares']} מניות (${tp['allocated_usd']:,.2f})</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">הוראה נלווית ביעד:</span>
                        <span style="font-weight: 600; color: #cbd5e1; direction: ltr;">Profit Taker (Limit) @ ${tp['target_1pct_price']:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 4px; padding-top: 6px; border-top: 1px dashed rgba(255,255,255,0.1);">
                        <span style="color: var(--text-muted);">מועד שידור הבא:</span>
                        <span style="font-weight: 700; color: #fca5a5;">ממתינים לסגירת יום עם איתות 🟢 BUY SIGNAL</span>
                    </div>
                </div>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>דוח ועדת השקעות: QQQ Volatility ({as_of})</title>
    <!-- TradingView Lightweight Charts CDN -->
    <script src="https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        :root {{
            --bg-main: #0f172a;
            --bg-card: #1e293b;
            --border: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-blue: #38bdf8;
            --accent-red: #ef4444;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: var(--font-family);
            line-height: 1.6;
            padding: 24px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-card);
            padding: 20px 28px;
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }}
        .header-title h1 {{
            font-size: 26px;
            font-weight: 800;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .header-title p {{
            color: var(--text-muted);
            font-size: 14px;
            margin-top: 4px;
        }}
        .badge {{
            padding: 8px 18px;
            border-radius: 9999px;
            font-weight: 800;
            font-size: 14px;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }}
        .card-header {{
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--accent-blue);
        }}
        .rules-list {{
            list-style: none;
        }}
        .rules-list li {{
            position: relative;
            padding-right: 24px;
            margin-bottom: 12px;
            font-size: 14px;
            color: #cbd5e1;
        }}
        .rules-list li::before {{
            content: "•";
            position: absolute;
            right: 8px;
            color: var(--accent-blue);
            font-weight: bold;
            font-size: 18px;
        }}
        .rules-list strong {{
            color: #f1f5f9;
        }}
        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 14px;
        }}
        .metric-label {{ color: var(--text-muted); }}
        .metric-val {{ font-weight: 700; direction: ltr; }}
        .chart-box {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        .chart-legend {{
            display: flex;
            gap: 16px;
            margin-bottom: 12px;
            font-size: 13px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }}
        #tv_chart {{
            width: 100%;
            height: 440px;
            position: relative;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th {{
            background: #1a2234;
            color: var(--text-muted);
            text-align: right;
            padding: 10px 12px;
            font-weight: 600;
            border-bottom: 2px solid var(--border);
        }}
        @media (max-width: 768px) {{
            .grid-2 {{ grid-template-columns: 1fr; }}
            .header {{ flex-direction: column; align-items: flex-start; gap: 14px; }}
        }}
    </style>
</head>
<body>
<div class="container">

    <!-- Header -->
    <div class="header">
        <div class="header-title">
            <h1>🎯 ועדת השקעות: TQQQ Volatility</h1>
            <p>נכס מסחר ראשי: <strong>TQQQ (מינוף פי 3)</strong> • מדד ייחוס לקבלת החלטות: <strong>QQQ</strong> • עדכון: {as_of}</p>
        </div>
        <div>
            <span class="badge" style="background:{v['status_color']}; color:#ffffff;">
                {v['status_label']}
            </span>
        </div>
    </div>

    <!-- Grid 1: Concise Rules & Committee Audit -->
    <div class="grid-2">
        <!-- Rules Block -->
        <div class="card">
            <div class="card-header">
                📜 חוקי האסטרטגיה בתמצית
            </div>
            <ul class="rules-list">
                <li><strong>1. משטר שוק ראשי:</strong> פוזיציות לונג אך ורק כשמדד הייחוס QQQ נסחר <strong>מעל EMA 200</strong> בגרף היומי (ללא מסחר בשוק דובי).</li>
                <li><strong>2. טריגר חזרה לממוצע:</strong> מתיחה של <strong>1.0% ומעלה מתחת ל-EMA 20</strong> ב-QQQ, מתנד <strong>RSI(14) נמוך מ-50</strong>, וקניית דיפ ישירה בסגירה (Pure Dip Buying).</li>
                <li><strong>3. ביצוע ב-TQQQ ויעד רווח:</strong> <strong>1.0%+ בלבד</strong> ב-TQQQ (שווה ערך לתיקון קל של כ-0.33%–0.5% בלבד ב-QQQ).</li>
                <li><strong>4. סטופ זמן מדורג:</strong> ימים 1–5 חתירה ליעד מלא של 1%+; ימים 6–9 חילוץ באיזון (+0.25%); <strong>יום 10 סגירה בשער השוק</strong> ושחרור המזומן.</li>
                <li><strong>5. ברבור שחור:</strong> שבירה של מעל 3% מתחת ל-EMA 200 או VIX > 35 מפעילים השבתת מסחר מיידית.</li>
            </ul>
        </div>

        <!-- Audit & Decision Block -->
        <div class="card">
            <div class="card-header">
                🔍 מבחני סף ועדת השקעות (Audit)
            </div>
            <div style="margin-bottom: 14px;">
                <p style="font-size: 15px; font-weight: 700; color:{v['status_color']}; margin-bottom: 12px;">
                    {v['verdict_he']}
                </p>
                {audit_html}
            </div>
        </div>
    </div>

    <!-- Grid 2: Trade Plan ($10,000) & Reference Benchmark Card -->
    <div class="grid-2">
        {trade_plan_card_html}

        <!-- Reference Benchmark: QQQ -->
        <div class="card" style="border-right: 4px solid var(--accent-blue);">
            <div class="card-header" style="color:var(--accent-blue);">
                📌 כרטסת ייחוס: מדד הבסיס QQQ (נאסד"ק 100)
            </div>
            <div class="metric-row">
                <span class="metric-label">שער מדד הבסיס QQQ</span>
                <span class="metric-val">${m['qqq_close']:.2f} ({m['qqq_change']:+.2f}%)</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">ממוצע נע EMA 20 (יומי)</span>
                <span class="metric-val">${m['ema_20']:.2f} (מרחק: {m['dist_ema20_pct']:+.2f}%)</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">ממוצע נע ראשי EMA 200</span>
                <span class="metric-val">${m['ema_200']:.2f} (מרחק: {m['dist_ema200_pct']:+.2f}%)</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">מתנד עוצמה RSI(14)</span>
                <span class="metric-val">{m['rsi_14']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">מדד הפחד VIX</span>
                <span class="metric-val">{m['vix']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">מגמת שוק ראשית</span>
                <span class="metric-val" style="color:var(--accent-green);">שורי (מעל EMA 200)</span>
            </div>
        </div>
    </div>

    <!-- Interactive TradingView Chart Section -->
    <div class="chart-box">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
            <div class="card-header" style="margin-bottom:0; border-bottom:none; padding-bottom:0;">
                📈 גרף מסחר ראשי: TQQQ (45 ימי מסחר אחרונים עם סימוני עסקאות)
            </div>
            <div class="chart-legend">
                <div class="legend-item"><div class="legend-dot" style="background:#38bdf8;"></div><span>EMA 20</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div><span>EMA 50</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#a855f7;"></div><span>EMA 200</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div><span>🟢 כניסה TQQQ</span></div>
                <div class="legend-item"><div class="legend-dot" style="background:#d69e2e;"></div><span>🎯 יעד 1%</span></div>
            </div>
        </div>
        <div id="tv_chart"></div>
    </div>

    <!-- 45-Day Historical Performance Log -->
    <div class="card" style="margin-bottom: 30px;">
        <div class="card-header" style="justify-content:space-between;">
            <span>📋 ריכוז עסקאות פוטנציאליות ב-45 ימי המסחר האחרונים</span>
            <span style="font-size:13px; color:var(--text-muted); font-weight:normal;">
                סה"כ עסקאות: <strong>{sim['summary']['total_trades']}</strong> | 
                אחוז הצלחה: <strong>{sim['summary']['win_rate_pct']}%</strong> | 
                רווח נקי מצטבר: <strong>${sim['summary']['total_net_pnl_usd']:+.2f}</strong> | 
                החזקה ממוצעת: <strong>{sim['summary']['avg_hold_days']} ימים</strong>
            </span>
        </div>
        <div style="overflow-x:auto;">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>תאריך כניסה</th>
                        <th>מחיר כניסה TQQQ</th>
                        <th>תאריך יציאה</th>
                        <th>מחיר יציאה</th>
                        <th style="text-align:center;">ימי החזקה</th>
                        <th style="text-align:center;">תוצאה</th>
                        <th style="text-align:center;">רווח/הפסד נקי ($)</th>
                    </tr>
                </thead>
                <tbody>
                    {trade_rows_html}
                </tbody>
            </table>
        </div>
    </div>

</div>

<!-- TradingView Lightweight Charts Script Execution -->
<script>
document.addEventListener("DOMContentLoaded", function () {{
    const chartContainer = document.getElementById('tv_chart');
    if (!chartContainer || typeof LightweightCharts === 'undefined') return;

    const chart = LightweightCharts.createChart(chartContainer, {{
        width: chartContainer.clientWidth,
        height: 440,
        layout: {{
            background: {{ color: '#1e293b' }},
            textColor: '#94a3b8',
        }},
        grid: {{
            vertLines: {{ color: '#334155' }},
            horzLines: {{ color: '#334155' }},
        }},
        rightPriceScale: {{
            borderColor: '#475569',
        }},
        timeScale: {{
            borderColor: '#475569',
            timeVisible: true,
            secondsVisible: false,
        }},
    }});

    // Candlestick Series (TQQQ Traded Asset)
    const candleSeries = chart.addCandlestickSeries({{
        upColor: '#10b981',
        downColor: '#ef4444',
        borderVisible: false,
        wickUpColor: '#10b981',
        wickDownColor: '#ef4444',
    }});

    // Moving Averages on TQQQ
    const ema20Series = chart.addLineSeries({{ color: '#38bdf8', lineWidth: 2, title: 'TQQQ EMA 20' }});
    const ema50Series = chart.addLineSeries({{ color: '#f59e0b', lineWidth: 1.5, title: 'TQQQ EMA 50' }});
    const ema200Series = chart.addLineSeries({{ color: '#a855f7', lineWidth: 2, title: 'TQQQ EMA 200' }});

    // Injected Data
    const rawData = {json.dumps(chart_bars)};
    const candleData = rawData.map(d => ({{
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close
    }}));

    const ema20Data = rawData.map(d => ({{ time: d.time, value: d.ema20 }}));
    const ema50Data = rawData.map(d => ({{ time: d.time, value: d.ema50 }}));
    const ema200Data = rawData.map(d => ({{ time: d.time, value: d.ema200 }}));

    candleSeries.setData(candleData);
    ema20Series.setData(ema20Data);
    ema50Series.setData(ema50Data);
    ema200Series.setData(ema200Data);

    // Set Markers for Entries and Exits
    const markers = {json.dumps(markers)};
    candleSeries.setMarkers(markers);

    // Responsive Resize
    window.addEventListener('resize', () => {{
        chart.applyOptions({{ width: chartContainer.clientWidth }});
    }});
}});
</script>
</body>
</html>
"""
    return html_content


def send_telegram_alert(data: dict):
    """Dispatches a push notification to Telegram with an inline button to GitHub Pages."""
    try:
        from config.config import Config
        from telegram_bridge import send_message
        
        token = Config.TELEGRAM_TOKEN
        chat_id = Config.TELEGRAM_CHAT_ID
        if not token or not chat_id:
            print("[-] Telegram credentials not configured, skipping push.")
            return False
            
        as_of = data['as_of_date']
        m = data['market_data']
        v = data['committee_verdict']
        tp = data['trade_plan']
        is_active = v.get('action_allowed', False)
        
        if is_active:
            status_emoji = "🟢"
            headline = f"🎯 *ועדת השקעות TQQQ: איתות קנייה פעיל!*"
            details = (
                f"שער סגירה QQQ: `${m['qqq_close']:.2f}` (מרחק: `{m['dist_ema20_pct']:+.2f}%` מ-EMA 20)\n"
                f"שער כניסה TQQQ: `${tp['tqqq_price']:.2f}`\n"
                f"כמות מניות: `{tp['shares']}` (${tp['allocated_usd']:,.2f})\n"
                f"🎯 יעד 1%+: `${tp['target_1pct_price']:.2f}` (רווח נקי: `+${tp['net_pocket_profit']:.2f}`)\n"
                f"⚡ פקודת שידור: `Buy Limit` בשער `${tp['tqqq_price']:.2f}` עם Profit Taker צמוד"
            )
        else:
            status_emoji = "⏸️"
            headline = f"🎯 *ועדת השקעות TQQQ: מצב המתנה (Standby)*"
            details = (
                f"מדד QQQ: `${m['qqq_close']:.2f}` (מרחק: `{m['dist_ema20_pct']:+.2f}%` מ-EMA 20, RSI: `{m['rsi_14']}`)\n"
                f"סטטוס: *100% מזומן (Cash)* — תנאי הדיפ לא התקיימו, אין לשדר פקודות."
            )
            
        message_text = f"{status_emoji} {headline}\nתאריך: {as_of}\n\n{details}"
        
        buttons = [
            [
                {
                    "text": "📊 פתח דוח מלא ב-GitHub Pages",
                    "url": "https://avibal.github.io/StockMarket-Agent/"
                }
            ]
        ]
        
        res = send_message(token=token, chat_id=chat_id, text=message_text, buttons=buttons, parse_mode="Markdown")
        if res and res.get("ok"):
            print("[+] Telegram push notification sent successfully!")
            return True
        else:
            print(f"[-] Telegram dispatch error: {res}")
            return False
    except Exception as e:
        print(f"[-] Failed to send Telegram alert: {e}")
        return False


def run_and_save_report(notify: bool = False):
    """Execute analysis and write HTML report."""
    print("Running market analysis...")
    data = analyze_market()
    
    html = generate_html_report(data)
    
    # Save path in stock_analysis_reports
    reports_dir = os.path.join(PROJECT_ROOT, 'stock_analysis_reports', 'QQQ_Volatility')
    os.makedirs(reports_dir, exist_ok=True)
    
    date_str = data['as_of_date']
    report_filename = f"QQQ_Volatility_Report_{date_str}.html"
    report_path = os.path.join(reports_dir, report_filename)
    latest_path = os.path.join(reports_dir, "latest_report.html")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    # Save to docs/index.html for GitHub Pages
    docs_dir = os.path.join(PROJECT_ROOT, 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    docs_index_path = os.path.join(docs_dir, "index.html")
    with open(docs_index_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Report saved to: {report_path}")
    print(f"Latest report copy saved to: {latest_path}")
    print(f"GitHub Pages report saved to: {docs_index_path}")
    
    if notify:
        send_telegram_alert(data)
        
    return report_path, data


if __name__ == '__main__':
    notify_flag = '--notify' in sys.argv
    run_and_save_report(notify=notify_flag)
