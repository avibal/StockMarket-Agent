---
name: qqq-volatility
description: >-
  Automated QQQ Volatility & Leveraged TQQQ Mean-Reversion Committee Agent (`/qqq`, `/tqqq`, `/qqq-vol`, "סוכן qqq", "ועדת qqq", "ועדת השקעות qqq"). Analyzes QQQ underlying index for clean mean-reversion setups (QQQ > EMA 200, dip >= 1.0% below EMA 20, RSI <= 45), executes via TQQQ (3x leverage) with a fixed $10,000 allocation, +1.0% profit target, and Tiered Time-Stop (Days 1-5 1%, Days 6-9 Break-Even, Day 10 Cut-Off). Generates an RTL executive summary in chat and a self-contained HTML Investment Committee report with embedded TradingView charts and 30-day trade markers.
---

# QQQ Volatility & Leveraged TQQQ Committee Agent (סוכן ועדת השקעות QQQ Volatility)

Monitors the primary benchmark index **$QQQ** for clean, low-noise mean-reversion dips, and structures short leveraged trades on **$TQQQ** (3x daily leverage) to capture quick +1.0% profit bites while enforcing a strict **Tiered Time-Stop** to eliminate 3x volatility drag.

## Strategy Core Rules (חוקי הברזל)
- **Capital Allocation**: Fixed **$10,000 USD** per trade ($\text{Shares} = \lfloor \$10,000 / P_{\text{TQQQ}} \rfloor$).
- **Regime Filter**: QQQ must be trading **above EMA 200** on the daily chart (Bull Market only; zero long trades in a bear regime).
- **Mean-Reversion Trigger**:
  - QQQ stretched $\ge 1.0\%$ below daily EMA 20 (or touching lower Bollinger Band 20,2).
  - RSI(14) $\le 50.0$ (oversold pressure).
  - Pure Dip Buying execution at day close (capturing next day's overnight bounce gap).
- **Profit Target**: **+1.0% on TQQQ** (requires only ~0.33%-0.5% bounce in QQQ). Net pocket profit ~$70-$75 after fees and 25% Israeli tax.
- **Tiered Time-Stop (ניהול סיכונים מבוסס זמן)**:
  - **Days 1 to 5 (Peak Target)**: Full target +1.0%.
  - **Days 6 to 9 (Break-Even Scratch)**: Target lowered to Break-Even (+0.25%) to cover fees on any bounce.
  - **Day 10 (Cut-Off)**: Market exit at day close to halt volatility drag and release the $10,000 for the next monthly setup.
- **Black Swan Circuit Breaker**: Emergency suspension if QQQ drops > 3% below EMA 200 or VIX $\ge 35$.

## Triggers
- Slash command: `/qqq`
- Slash command: `/tqqq`
- Slash command: `/qqq-vol`
- Natural language (Hebrew): "סוכן qqq", "ועדת qqq", "ועדת השקעות qqq", "אסטרטגיית qqq", "סטטוס tqqq", "הזדמנות ב-qqq"

## Execution Workflow

1. **Run the Report Generator & Engine**:
   Execute the Python engine to compute real-time metrics and update the HTML report:
   ```powershell
   .\.venv\Scripts\python.exe strategies\qqq_volatility\report_generator.py
   ```

2. **Present RTL Executive Summary in Chat**:
   Format response directly in clean Hebrew RTL (`<div dir="rtl">...</div>`):
   - 🎯 **כרטיס סטטוס החלטה**: תאריך, שער QQQ, שער TQQQ, ובאדג' החלטת הוועדה (מאושר / ממתין / וטו / ברבור שחור).
   - 📜 **תמצית חוקי האסטרטגיה**: 4 בולטים תמציתיים.
   - 💼 **תוכנית הטרייד ($10,000)**: כמות מניות, שער כניסה, יעד 1%+, מחירי חילוץ באיזון, ורווח נקי משוער.
   - 📊 **מבחני סף (Audit)**: בדיקת EMA 200, מרחק מ-EMA 20, RSI, נר היפוך, ומדד VIX.
   - 📈 **ביצועי 30 ימי מסחר אחרונים**: סה"כ עסקאות, אחוז הצלחה, רווח נקי מצטבר, וזמן החזקה ממוצע.
   - 🔗 **קישור ישיר לדוח ה-HTML המלא עם גרף TradingView האינטראקטיבי**:
     `[צפה בדוח המלא עם גרף TradingView אינטראקטיבי](file:///c:/AB/Dev/StockMarket/StockMarket-Agent/stock_analysis_reports/QQQ_Volatility/latest_report.html)`
