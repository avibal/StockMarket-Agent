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

   🛡️ **פרוטוקול חובה למנהל הסיכונים (Risk Manager Hard Veto & Nearest Obstacle Audit)**:
   מנהל הסיכונים בוועדה מחזיק ב**זכות וטו מוחלטת (Hard Veto)** על כל המלצת קנייה:
   - **מבחן התקרה הקרובה (Nearest Obstacle Test - TP1)**: יחס הסיכוי-סיכון נמדד **תמיד מול רמת ההתנגדות הראשונה והמשמעותית ביותר** (למשל ממוצע 20 או התנגדות R1). אסור להכשיר טרייד שבו היעד הקרוב מניב R:R מתחת ל-**1:1.5** או רווח ברוטו קטן מ-**1.5%** באמצעות יעד TP2 רחוק!
   - **זכות וטו והכרעת הימנעות (HOLD / AVOID on No Man's Land)**: אם ה-R:R מול התקרה הקרובה נמוך מ-1:1.5, מנהל הסיכונים **מטיל וטו מיידי**, והכרעת הוועדה הכוללת **מחויבת להיות 🟡 הימנעות / המתנה (HOLD)** — גם אם המגמה הראשית שורית וסנטימנט האופציות חיובי!
   - **הגדרת תנאי סף חלופיים לכניסה**: במצב של הימנעות, הוועדה תמליץ על המתנה לאחד משני תרחישים בלבד:
     1. *תרחיש איסוף בתמיכה*: נסיגה עמוקה יותר לרמת התמיכה (מצמצמת את הסיכון לסטופ ומקפיצה את ה-R:R ל-1:2+).
     2. *תרחיש פריצה*: פריצה וסגירה מעל התקרה הקרובה (הפיכתה מתקרה לתמיכה ללא מכשול בדרך).
   - **מבחן ATR ומניעת ניעור (Whipsaw Shield)**: מרחק הסטופ חייב להיות לפחות $0.75\times$ עד $0.85\times$ מה-ATR היומי ומעוגן תמיד **מתחת** לתמיכות הנבדקות (EMA 50, רצועת בולינגר תחתונה, שפל נרות אחרונים).
   - **מודל הגנה היברידי דו-שכבתי (Hybrid Two-Tier Stop Architecture)**:
     כדי לפתור את דילמת הניעורים (ציד סטופים תוך-יומי מול סכנת גאפ-דאון), הוועדה מגדירה תמיד שתי שכבות הגנה:
     1. *שכבה 1: סטופ טקטי מנוהל (התראת TradingView)*: רמת התמיכה המבנית הקרובה. לא מזינים פקודת שוק בברוקר; סוגרים ידנית אך ורק אם נר שעתי (1H) או יומי (1D) נסגר מוכח מתחת לרמה. כמות המניות, יחס הסיכוי-סיכון (R:R) וההפסד המתוכנן מחושבים לפי שכבה זו.
     2. *שכבה 2: סטופ קטסטרופה קשיח בברוקר (IBKR Hard Disaster Stop)*: ממוקם מתחת לתמיכת מאקרו רחבה (כגון שבירת ממוצע 200 ימים או מרווח 1.8x). מוזן ישירות כפקודה קשיחה ב-Interactive Brokers ומשמש פוליסת ביטוח מפני קריסות פתע, גאפ-דאון בין ימי מסחר ואירועי ברבור שחור.
   - **בדיקת משטר שוק (Market Regime Audit - Trend vs. Chop)**:
     מנהל הסיכונים בוחן את מדד ה-ADX (מתוך `combined_analysis`):
     - אם ADX < 20: השוק מוגדר כ-**דשדוש (Chop / Range)**.
     - **חוק ברזל - איסור פריצות בדשדוש (Breakout Ban in Chop)**: בדשדוש פריצות שיא הן מלכודות שווא וציד נזילות. מנהל הסיכונים פוסל אוטומטית עסקאות פריצה, ומאשר אך ורק איסוף היפוך ברצפת הטווח באזור Discount.
   - **בדיקת אזור תמחור (Pricing Zone & OTE Audit - SMC)**:
     מנהל הסיכונים מחשב את יחס הטווח של הגל האחרון:
     - **Premium Zone (מעל 50% מהגל / נסיגה קטנה מ-45%)**: סכנת FOMO מובהקת – כניסה באזור יקר מגדילה את המרחק לסטופ ומקטינה את הרווח לשיא (R:R נחות הפוסל את הטרייד).
     - **Discount Zone (מתחת ל-50% מהגל) ו-OTE (61.8%–78.6%)**: Sweet Spot מוסדי המאפשר סטופ הדוק ויעד מרווח עם R:R $\ge 1:1.8$.
   - **פילטר מלכודת גאפ (Gap-Up FOMO Filter)**:
     במידה והמניה פתחה בגאפ-אפ של מעל 1%, חל איסור כניסה בלימיט פסיבי במחיר הגאפ. חובה להמתין למילוי חלקי (Gap Fill) או בדיקת תמיכה (Retest) באישור נר 15 דקות.
    - **מודל 3 השכבות המוסדי ורוטציה סקטוריאלית (Tri-Layer Confluence & Sector RRG Audit)**:
      הוועדה מחייבת אימות שכבתי מלא מלמעלה למטה (Top-Down):
      1. *שכבה 1 (Market Benchmark)*: בחינת מדד הייחוס (SPY/QQQ) ומדד ADX (מגמה Trend מול דשדוש Chop).
      2. *שכבה 2 (Sector RRG)*: בחינת רביע הרוטציה של הסקטור מול SPY:
         - 🚀 **Improving**: צבירת כסף חכם מוקדמת (בונוס ציון).
         - 🟢 **Leading**: רוח גבית מוסדית מקסימלית (בונוס ציון).
         - 🟡 **Weakening**: נסיגה יחסית (יעדים שמרניים בלבד).
         - 🔴 **Lagging**: פיגור ויציאת הון (קנס ניקוד כבד; אסור לקנות בדשדוש ללא OTE עמוק).
   - **בקרת סיכון לפי גודל פוזיציה ($75 Max Dollar Risk)**: כמות המניות תותאם לתקרת סיכון של \$75:
     $$\text{Shares} = \min\left(\lfloor \frac{\$10,000}{\text{Price}} \rfloor,\ \lfloor \frac{\$75}{\text{Entry} - \text{Stop}} \rfloor\right)$$
   - **חוק הקפאת מאקרו (Macro Event Freeze & Liquidity Vacuum Rule)**:
     בדיקת לוח השנה הכלכלי (`scripts/macro_calendar.py`) היא חובה. במידה ומתקיים אירוע פד / ריבית / נאום פאוול / מדד מחירים (CPI) במהלך שעות המסחר (16:30–18:30 שעון ישראל) — **חל איסור מוחלט על כניסה בסווינג לפני השעה 18:00** (לפחות 30 דקות לאחר סיום האירוע והתייצבות הנזילות בספר הפקודות). פקודות Limit עיוורות לפני/בפתיחה אסורות לחלוטין.
   - **איסור פקודות לימיט מראש בסקטור מפגר (Lagging Sector Limit Prohibition & Breakout-Only)**:
     במידה והסקטור של המניה נמצא ברביע **Lagging 🔴 (מפגר)** ברוטציית RRG:
     1. *איסור לימיט פסיבי*: חל איסור מוחלט על הזנת פקודות Limit מראש בפתיחת המסחר ("סכין נופלת").
     2. *כניסה אך ורק בפריצת שיא (HOD Breakout)*: הכניסה תותר אך ורק באישור פריצה של שיא נר השעה הראשונה (לאחר 17:30) כדי להוכיח שהקונים סופגים את כוח המשיכה השלילי של הסקטור.
     3. *תקרת ציון קונצנזוס*: נאסר מתן ציון "+4 קנייה שורית מובהקת" למניה שהסקטור שלה ב-Lagging; הציון המקסימלי מוגבל ל-`+2 (קנייה מתונה באישור)`.
   - **מסנן מלכודת גאמא של עושי שוק בימי פקיעה (0-DTE / Weekly Options Gamma Trap Filter)**:
     בבחינת זרימת האופציות (`stock_options_unusual_activity`), אם זוהה ריכוז קולים חריג שפוקע באותו שבוע או באותו יום מסחר (0-DTE):
     אנליסט הסנטימנט ומנהל הסיכונים מחויבים לבחון את האינטרס הנגדי של **עושי השוק (Market Makers)**. עושי שוק שכתבו עשרות אלפי קולים מפעילים לחץ מכירות אגרסיבי בנכס הבסיס (Delta Hedging / Pinning) כדי לדכא את המחיר מתחת לסטרייק עד לסגירת המסחר. הוועדה תסמן זאת כ**אזהרת גאמא** ותחייב המתנה לספיגת ההיצע.

2. **Render & Save HTML Report**:
   - Automated Visual Swing Simulation Chart:
     Runs `scripts/chart_simulator.py` to generate `YYYYMMDD_<TICKER>_chart.png` (TradingView Dark Theme, 45-day history, EMA 20/50, and 10-bar projection boxes for targets/stops or No Man's Land traps). Embeds this high-res visual chart directly inside the Swing Strategy Card.
   - Populate `stock_analysis_reports/Report_Template/template.html` with full deep-dive intelligence (Debate arguments, Confluence levels, Options flow, 1-Year Backtest, Swing financial table, Long strategy, and interactive tooltips).
   - Ensure header consensus badge is colored dynamically: green (קנייה / BUY), amber (הימנעות / ניטרלי / HOLD), or red (מכירה / SELL).
   - Save the rendered report to:
     `C:\AB\Dev\StockMarket\StockMarket-Agent\stock_analysis_reports\YYYYMMDD_<TICKER>_DEBATE.html`
   - Also save a self-contained copy with embedded CSS to:
     `<appDataDir>\brain\<conversation-id>\<ticker_lowercase>_debate_report.html`
   - Dynamically resolve current local machine IPv4 via `get_local_ip()` (never hardcode).
   - Ensure local HTTP server daemon is running (`python -m http.server 8080 --directory stock_analysis_reports`).

3. **Format Chat Response (Fast, High-Impact Executive Alert)**:
   - Since the full analysis, debate arguments, options data, backtest, and financial calculations already exist in the rich HTML report with interactive tooltips, **do NOT duplicate the long analysis in the chat**.
   - Output a concise, clean, 8-10 line executive summary in pure RTL (`<div dir="rtl" style="text-align: right;">...</div>`):
     - 🚨 **באנר התראת מאקרו (אם יש אירוע High-Impact היום):** התראה מודגשת עם שעות האירוע והנחיית איסור לימיט פסיבי.
     - 🏛️ **כותרת:** נכס, מחיר נוכחי ושינוי יומי.
     - ⚖️ **הכרעת הוועדה:** תגית צבעונית בולטת (🟢 קנייה / 🟡 הימנעות-ניטרלי / 🔴 מכירה) + ציון Net Score + רמת ביטחון ואיכות טרייד.
     - 🎯 **תמצית סווינג (עד שבועיים):** המלצה ממוקדת בשורה אחת (כיוון, כניסה פסיבית vs אישור היפוך, סטופ מותאם לנכס, ויעד רווח נטו בכיס).
     - 🏦 **תמצית לונג (השקעה):** המלצה ממוקדת בשורה אחת (מגמת מאקרו ושיטת איסוף DCA).
     - 📄 **קישורי צפייה ישירים לדוח המלא:**
       - 💻 **במחשב:** `[פתח את דוח ה-HTML המלא בדפדפן](file:///C:/AB/Dev/StockMarket/StockMarket-Agent/stock_analysis_reports/YYYYMMDD_<TICKER>_DEBATE.html)`
       - 📱 **בטלפון הנייד (Wi-Fi):** `http://<DYNAMIC_IP>:8080/YYYYMMDD_<TICKER>_DEBATE.html`
       - 📱 **בתוך Antigravity:** זמין בטאב ה-Artifacts (`<ticker_lowercase>_debate_report.html`).
