---
name: swing-scanner
description: >-
  Automated Swing Opportunity Scanner (`/scan-swing`, `/find-swing`, "סורק סווינג", "הזדמנויות סווינג"). Scans 60+ highly liquid US leaders (Tech, Semis, AI Energy, S&P leaders) in ~2-3 seconds using vectorized yfinance and pandas to detect high-probability 2-week swing pullbacks (Price > EMA 200, 1.5%-8% pullback, at key support EMA 20/50/BB, RSI 32-55). Calculates trade plan with exact $10,000 allocation, +1.5% to +2.5% gross target, IBKR Israel fees ($5), 25% Israeli tax, and net pocket profit. Outputs a concise RTL executive alert table in chat with 1-click links to launch the full multi-agent debate report.
---

# Swing Opportunity Scanner (סורק הזדמנויות סווינג קצר)

Scans a curated universe of 60+ top liquid US stocks and benchmark ETFs to identify immediate swing opportunities matching our defined investment rules:
- **Horizon**: Up to 2 weeks (1-10 trading days).
- **Capital**: $10,000 allocation (with adaptive $75 max dollar risk capping).
- **Gross Target**: 1.5% to 2.5% (median 2.0%).
- **Financial Model**: Includes IBKR Israel commissions ($5 full turn) + Israeli Capital Gains Tax (25%) ➡️ Outputs **Net Profit in Pocket**.
- **Adaptive Technical Model**: 
  - Pullback in Uptrend (Price > EMA 200, healthy dip 1.5%-8%, resting on EMA 20/50 or lower Bollinger Band, RSI 32-55).
  - **Whipsaw Shield (הגנת ניעור)**: Anchors stops safely below the deepest tested support ($\min(\text{Low}_{3}, \text{EMA}_{50}, \text{Lower BB})$ minus buffer), combined with an ATR noise floor ($\ge 0.75\times \text{ATR}$ for ETFs, $\ge 0.85\times \text{ATR}$ for Equities). Stops are NEVER placed inside intraday noise or above moving average supports.
  - **Tiered Real R:R Filter & Blended Target**: 
    - Index ETFs: Minimum R:R $\ge 1.5$ (high base rate mean-reversion) | Blended R:R $\ge 1.2$.
    - Single Stocks: Minimum R:R $\ge 1.8$ (higher beta) | Blended R:R $\ge 1.35$.
  - **Overhead Resistance & Nearest Obstacle Collision Check (מבחן התקרה הקרובה וסנכרון מלא לוועדת ההשקעות)**: 
    - When entry price is below EMA 20, upside is strictly capped at EMA 20 (TP1).
    - If upside to EMA 20 is < 1.4% (ETFs) or < 1.6% (Equities), candidate is **immediately disqualified** (No Man's Land trap).
    - If R:R to EMA 20 is < 0.85 (risking more than gaining to the first obstacle), candidate is **immediately disqualified**.
    - This fully guarantees that any candidate produced by the scanner will pass the Investment Committee Risk Manager audit without hitting a Hard Veto!
  - **Dynamic Position Sizing ($75 Max Risk)**: Retail risk protection allocates shares based on fixed dollar risk ($\le \$75$) rather than blindly deploying \$10,000, ensuring maximum survivability during market turbulence.
  - **Dual Entry Engine**: Passive Limit (for calm days) vs Reversal Confirmation (15m green candle for high volatility/macro days).
- **Automated Macro Shield**: Built-in 0.2s check of high-impact US events (FOMC, CPI, NFP, Powell speeches) with automatic trading directives.

## Triggers
- Slash command: `/scan-swing`
- Slash command: `/find-swing`
- Slash command: `/swing`
- Natural language (Hebrew): "סורק סווינג", "מצא הזדמנויות סווינג", "יש הזדמנויות סווינג היום?", "הזדמנויות סווינג"

## Engine Script
- Script: [scripts/swing_scanner.py](file:///c:/AB/Dev/StockMarket/StockMarket-Agent/scripts/swing_scanner.py)
- Command: `.\.venv\Scripts\python.exe scripts/swing_scanner.py --json`

## Execution Workflow

1. **Run Scanner**:
   Execute the vectorized Python engine:
   ```powershell
   .\.venv\Scripts\python.exe scripts/swing_scanner.py --json
   ```

2. **Format Response (Pure RTL Executive Summary)**:
   Format the chat output directly in clean Hebrew RTL (`<div dir="rtl" style="text-align: right;">...</div>`):
   - 🚨 **באנר התראת מאקרו (אם יש אירוע High-Impact היום)**:
     - אם `macro_risk.has_high_impact` הוא `True`: הצג באנר אדום/כתום בולט בראש ההודעה עם שמות האירועים, שעות ישראל והנחיית פעולה (איסור על פקודות Limit פסיביות עד לאחר האירוע).
   - 🎯 **כותרת**: סורק הזדמנויות סווינג (הון מירבי: $10,000 | תקרת סיכון מוגדרת: $75 | מודל R:R מדורג).
   - ⚡ **סטטוס סריקה**: נסרקו 60+ נכסים ב-X שניות | נמצאו Y התאמות איכותיות.
   - 📊 **טבלת / כרטיסי מועמדים מובילים (Top 3-4)**:
     - **סימול, סוג נכס וציון**: (לדוגמה: 🟢 **QQQM** [Index ETF | 95/100])
     - **מחיר ושינוי**: מחיר סגירה ושינוי יומי.
     - **מצב טכני**: עומק התיקון משיא, תמיכה נבדקת (EMA 20 / EMA 50 / BB), ו-RSI.
     - **מצב כניסה מומלץ**:
       - *כניסת לימיט פסיבית*: מחיר לימיט בתמיכה (לימים שקטים בלבד).
       - *כניסת אישור (Confirmation)*: כניסה מעל נר היפוך 15 דקות ירוק (חובה בימי מאקרו).
     - **תוכנית טרייד מותאמת סיכון ($75 Max Risk | הגנת ניעור)**:
       - כמות מניות מומלצת והון מוקצה (למשל: 75 מניות | $4,680).
       - יעדים מדורגים: TP1 (יעד שמרני) ו-TP2 (יעד ריצה מלא).
       - סטופ מבני בטוח (מתחת לתמיכות עם מרווח רעש ATR).
       - יחס R:R אמיתי (לפחות 1:1.5 למדדים, 1:1.8 למניות).
     - **רווח נטו בכיס**: רווח דולרי נטו ורווח באחוזים נטו (לאחר עמלת אינטראקטיב $5 ומס רווחי הון 25%).
     - **פעולה ישירה (1-Click)**: לינק מהיר להפעלת דיבייט מלא: `/debate <TICKER>`.

3. **Next Step Advice**:
   Prompt the user to choose any candidate to run a full multi-agent debate report (`/debate <TICKER>`) to inspect hedge fund agent consensus, institutional options flow, and 1-year backtest validation before opening the position.
