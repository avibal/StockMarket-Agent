---
name: trade-post-mortem
description: >-
  Automated Trade Post-Mortem & Lessons Learned Generator (`/post-mortem`, `/tahkir`, "תחקיר טרייד", "הפקת לקחים", "לנתח טרייד כושל"). Analyzes executed trades (entry/exit prices, timing, shares, macro events, intraday liquidity sweeps, stop-loss placement audit, financial loss, and Israeli tax shield 25%). Generates a gorgeous, self-contained RTL HTML post-mortem report in `stock_analysis_reports/Post_Mortems/` with 1-click links for desktop and mobile Wi-Fi viewing.
---

# Trade Post-Mortem & Lessons Learned Generator (מנוע תחקיר טריידים והפקת לקחים)

An autonomous, institutional-grade trade post-mortem engine designed to analyze executed trades (whether stopped out, breakeven, or profitable) to extract systemic improvements, audit stop-loss placement against institutional liquidity sweeps, assess macro calendar impacts, and calculate exact financial outcomes including Israeli tax shields.

## Triggers
- Slash command: `/post-mortem <TICKER>`
- Slash command: `/tahkir <TICKER>`
- Natural language (Hebrew):
  - "תחקיר טרייד [טיקר]"
  - "הפקת לקחים מטרייד [טיקר]"
  - "בוא נתחקר את הטרייד על [טיקר]"
  - "תחקיר על טרייד כושל"

## Engine Script
- Script: [scripts/trade_post_mortem.py](file:///c:/AB/Dev/StockMarket/StockMarket-Agent/scripts/trade_post_mortem.py)
- Destination folder: `stock_analysis_reports/Post_Mortems/`
- Command format:
  ```powershell
  .\.venv\Scripts\python.exe scripts/trade_post_mortem.py --ticker <TICKER> --entry-price <ENTRY> --exit-price <EXIT> --shares <SHARES> --date <YYYY-MM-DD> [--exit-time <HH:MM>] [--next-price <PRICE>]
  ```

## Execution Workflow

1. **Parameter Gathering**:
   If the user provides the ticker and execution parameters (e.g. "קניתי QQQM ב-290.9 ויצאתי בסטופ 288.67 עם 34 מניות בתאריך 2026-09-16 בשעה 22:19"), parse them immediately.
   If parameters are missing, ask the user concisely:
   - מחיר כניסה (Entry Price)
   - מחיר יציאה בסטופ (Exit Price)
   - כמות מניות (Shares)
   - תאריך ושעת הביצוע (Date & Time)

2. **Run Engine**:
   Execute `scripts/trade_post_mortem.py` with the collected parameters.
   The engine will automatically:
   - Check the macro calendar (`macro_calendar.py`) for high-impact US events (FOMC, CPI, NFP, Powell).
   - Classify asset volatility (Index ETF vs Single Stock).
   - Measure distance from the day's absolute low to identify institutional stop hunts / liquidity sweeps.
   - Verify if price recovered above entry (thesis validity test).
   - Calculate optimal adaptive stop loss distance and survival test.
   - Calculate gross loss, IBKR commission, net loss, and 25% Israeli capital gains tax shield.
   - Generate a beautiful, standalone HTML report with embedded CSS in `stock_analysis_reports/Post_Mortems/YYYYMMDD_<TICKER>_POST_MORTEM.html`.
   - Copy to conversation artifacts for instant viewing in Antigravity.

3. **Format Chat Response (Pure RTL Executive Summary)**:
   Output a crisp, high-impact 8-10 line executive summary in pure Hebrew RTL (`<div dir="rtl" style="text-align: right;">...</div>`):
   - 📋 **כותרת תחקיר:** נכס, תאריך טרייד ומחיר כניסה מול יציאה.
   - 🛑 **תוצאה פיננסית:** הפסד כספי מדויק, אחוז מההקצאה (למשל: -0.79%), והון שנשמר בכיס (למשל: 99.21%).
   - 🚨 **הקשר מאקרו:** האם הופעל אירוע מאקרו קריטי (כגון החלטת ריבית הפד / פאוול).
   - 🎯 **מבחן התזה וציד נזילות:** האם הנכס ביצע באונס מעל מחיר הקנייה והאם הסטופ הופעל בשפל המוחלט של היום.
   - 📏 **סטופ לוס אדפטיבי מומלץ:** מה היה הסטופ המבני הנכון והאם הוא היה שורד את הניעור.
   - 🛡️ **מגן מס בישראל:** סכום מגן המס (25%) הזמין לקיזוז מול רווחי סווינג עתידיים.
   - 📄 **קישורי צפייה ישירים לדוח התחקיר המלא:**
     - 💻 **במחשב:** `[פתח את דוח התחקיר המעוצב בדפדפן](file:///C:/AB/Dev/StockMarket/StockMarket-Agent/stock_analysis_reports/Post_Mortems/YYYYMMDD_<TICKER>_POST_MORTEM.html)`
     - 📱 **בטלפון הנייד (Wi-Fi):** `http://<DYNAMIC_IP>:8080/Post_Mortems/YYYYMMDD_<TICKER>_POST_MORTEM.html`
     - 📱 **בתוך Antigravity:** זמין בטאב ה-Artifacts (`<ticker_lowercase>_post_mortem.html`).
