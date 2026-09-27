---
name: multi-agent-debate
description: >-
  Executes an advanced multi-agent investment committee debate (Technical Analyst, Sentiment & Momentum Analyst, and Risk Manager) combined with deep quantitative confluence analysis, smart money options flow, and historical backtest strategy validation using TradingView MCP tools (multi_agent_analysis, combined_analysis, stock_options_unusual_activity, and compare_strategies) for any stock symbol. Formats the output into a beautifully structured, right-aligned (RTL) executive summary report in Hebrew with visual badges, scorecards, pivot levels, smart money pulse, and actionable trading takeaways (Swing & Long). Triggered by `/debate <ticker>`, "דיבייט", "ועדת השקעות", or multi-agent queries.
---

# Multi-Agent Debate & Intelligence Skill (ועדת השקעות ומודיעין שוק מרובת סוכנים)

Integrates four specialized TradingView MCP power tools:
1. `multi_agent_analysis` - The simulated Hedge Fund Committee debate between Technical Analyst, Sentiment & Momentum Analyst, and Risk Manager.
2. `combined_analysis` - Deep quantitative engine providing pivot points, support/resistance, ATR volatility, algorithmic trade setups (entries, stops, targets, R:R), and news confluence.
3. `stock_options_unusual_activity` - Institutional Smart Money pulse: Put/Call volume ratio and unusual options contract concentrations.
4. `compare_strategies` - 1-year historical backtest ranking the top 9 strategies to identify the single winning edge and the biggest statistical trap (without cognitive overload).

## Triggers
- Slash command: `/debate <ticker>` (e.g. `/debate NVDA`, `/debate QQQM`, `/debate TSLA`)
- Slash command: `/committee <ticker>`
- Natural language: "תריץ דיבייט סוכנים על [טיקר]", "מה ועדת ההשקעות אומרת על [טיקר]"

## Template Location
HTML and CSS templates are cleanly decoupled in:
- **Template HTML**: [Report_Template/template.html](file:///c:/AB/Dev/StockMarket/StockMarket-Agent/stock_analysis_reports/Report_Template/template.html)
- **Stylesheet CSS**: [Report_Template/style.css](file:///c:/AB/Dev/StockMarket/StockMarket-Agent/stock_analysis_reports/Report_Template/style.css)
- **Render Script**: [Report_Template/render_report.py](file:///c:/AB/Dev/StockMarket/StockMarket-Agent/stock_analysis_reports/Report_Template/render_report.py)

## Execution Workflow

1. **Multi-Tool MCP Ingestion**:
   - Exchange resolution: `NASDAQ` for tech/ETFs (QQQM, NVDA, AAPL, MSFT, TSLA, AMZN, GOOGL, META), `NYSE` for traditional US stocks.
   - Run `tradingview:multi_agent_analysis` (timeframe="1D") ⬅️ Committee voting & consensus.
   - Run `tradingview:combined_analysis` (timeframe="1D") ⬅️ Pivot levels, ATR, algorithmic trade setup.
   - Run `tradingview:stock_options_unusual_activity` (symbol) ⬅️ Put/Call ratio and institutional flow.
   - Run `tradingview:compare_strategies` (symbol, period="1y") ⬅️ Top winning strategy and worst statistical trap.

2. **Dual Strategic Recommendations**:
   - 🎯 **אסטרטגיית סווינג (טווח קצר - ימים עד שבועות):**
     - כניסה מומלצת (Pullback או Breakout).
     - סטופ לוס מוגן על בסיס רמות תמיכה מחושבות.
     - יעד רווח מהיר (1.5% עד 2.5%) לפי רצועות בולינגר ו-R1.
     - יחס סיכוי-סיכון (R:R) מחושב.
   - 🏦 **אסטרטגיית לונג / השקעה (טווח בינוני-ארוך - חודשים עד שנים):**
     - תמונת מאקרו רב-זמנית (ממוצע 200, Golden Cross).
     - חלוקת מנות (DCA) מומלצת.
     - רמת שבירת מגמה ארוכת-טווח.

3. **Format Chat Response**:
   - Output in pure RTL (`<div dir="rtl" style="text-align: right;">...</div>`).
   - Executive consensus banner with pill badges.
   - Smart Money Options Pulse (Put/Call ratio, institutional leaning).
   - Historical Strategy Validation (2-line decision box: Winner vs Trap).
   - Voting scorecard table (RTL aligned).
   - Quantitative Confluence Card (Pivot, S1, R1, ATR, Algo R:R).
   - Dual strategy action plans (Swing vs Long).

4. **Render & Save HTML Report**:
   - Populate `stock_analysis_reports/Report_Template/template.html`.
   - Save the rendered report to:
     `C:\AB\Dev\StockMarket\StockMarket-Agent\stock_analysis_reports\YYYYMMDD_<TICKER>_DEBATE.html`
   - Provide a clickable link in the response:
     `[צפה בדוח המעוצב בדפדפן (HTML)](file:///C:/AB/Dev/StockMarket/StockMarket-Agent/stock_analysis_reports/YYYYMMDD_<TICKER>_DEBATE.html)`
