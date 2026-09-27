import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "stock_analysis_reports", "Report_Template"))

from render_report import render_debate_report

data = {
    "TICKER": "JPM",
    "NAME": "JPMorgan Chase & Co.",
    "EXCHANGE": "NYSE",
    "TIMEFRAME": "יומי (1D)",
    "DATE": "17 בספטמבר 2026",
    "DATE_RAW": "20260917",
    "CONSENSUS_CLASS": "amber",
    "CONSENSUS_TEXT": "הימנעות מומנטום / קנייה בבדיקת תמיכה (ACCUMULATE AT SUPPORT)",
    "PRICE": "$348.92 (-1.26%)",
    "NET_SCORE": "-5 (מומנטום) | +3 (תמיכה)",
    "CONFIDENCE": "גבוהה (85%)",
    "TRADE_QUALITY_SCORE": "80/100 (תמיכת EMA 50 + יחס סיכוי/סיכון חריג 1:4.55)",
    
    # Options Pulse
    "OPTIONS_BADGE_CLASS": "bullish",
    "OPTIONS_BADGE_TEXT": "שורי חזק • יחס פוט/קול 0.54",
    "PUT_CALL_RATIO": "0.54 (שורי מובהק - פי 2 קולים מפוטים)",
    "OPTIONS_PC_RATIO": "0.54 (שורי מובהק - פי 2 קולים מפוטים)",
    "OPTIONS_CALL_VOL": "25,194",
    "OPTIONS_PUT_VOL": "13,599",
    "OPTIONS_VOLUME_DIST": "25,194 Calls מול 13,599 Puts",
    "OPTIONS_DOMINANCE": "זרימת כסף חכם אגרסיבית לחוזי Call בסטרייקים $352.50 ו-$355.00 לפקיעת מחר!",
    "OPTIONS_SUMMARY": "הפעילות בשוק הנגזרים מלמדת על צפי מוסדי חזק להיפוך מהיר מעלה בחזרה מעל $353–$355.",

    # 1-Year Backtest
    "HISTORICAL_WINNER": "RSI Oversold/Overbought",
    "HISTORICAL_WINNER_STATS": "+10.31% תשואה • 66.7% הצלחה • מקסימום Drawdown מזערי של -0.27% בלבד!",
    "HISTORICAL_TRAP": "Supertrend (-19.39%) ו-EMA Golden Cross (-11.71%)",
    "HISTORICAL_VALIDATION": "הבקטסט חושף שרכישת תיקונים במתנד RSI ובולינגר ב-JPM מניבה 100% הצלחה (Bollinger Mean Reversion: 4 מתוך 4 טריידים מנצחים!), בעוד מרדף אחר מומנטום מוביל להפסדים.",

    # Agents Debate
    "TECH_SCORE_CLASS": "red",
    "TECH_STANCE": "דובי קצר-טווח (-3)",
    "TECH_ITEMS": """
        <li>מחיר מניה $348.92 סמוך לרצועת בולינגר תחתונה ($348.93).</li>
        <li>שבירה זמנית של EMA 20 ($354.48) ומבחן תמיכה קריטי ב-EMA 50 ($349.43).</li>
        <li>מתנד RSI ברמת 43.3 (אזור תיקון אידיאלי לקראת היפוך מעלה).</li>
    """,
    "TECH_SUMMARY": "הלחץ הטכני המיידי שלילי, אך הנכס הגיע בדיוק לאזור התמיכה המרכזי שבו צפוי באונס.",

    "SENT_SCORE_CLASS": "red",
    "SENT_STANCE": "מומנטום שלילי (-2)",
    "SENT_ITEMS": """
        <li>לחץ מכירות תוך-יומי עם שינוי יומי של 1.26%-.</li>
        <li>חיתוך דובי במתנד MACD (קו MACD: -0.31 מול Signal: +0.92).</li>
        <li>נר יומי אדום המעיד על שליטת מוכרים זמנית.</li>
    """,
    "SENT_SUMMARY": "המומנטום היומי עדיין לא התהפך; יש להמתין לנר 15 דקות ירוק (Confirmation) טרם כניסה.",

    "RISK_SCORE_CLASS": "blue",
    "RISK_STANCE": "סיכון נמוך (Score 0)",
    "RISK_ITEMS": """
        <li>מחיר נסחר גבוה מעל ממוצע 200 ראשי ($323.31) - מגמה ראשית שורית חזקה.</li>
        <li>קיומו של Golden Cross פעיל (EMA 50 מעל EMA 200).</li>
        <li>תנודתיות ATR יומית מתונה של $6.82 (1.96% בלבד).</li>
    """,
    "RISK_SUMMARY": "הסיכון המבני של הנכס נמוך מאוד; תמיכת $347.38 מספקת עוגן הגנה הדוק ומצוין.",

    # Quantitative Confluence
    "SUPPORT_LEVEL": "S1: $348.76 • EMA 50: $349.43",
    "PIVOT_LEVEL": "$357.63",
    "RESISTANCE_LEVEL": "$354.48 (EMA 20) • $360.99 (בולינגר עליון)",
    "ATR_VALUE": "$6.82 (תנודתיות מתונה 1.96%)",
    "CALCULATED_RR": "1:4.55 (יחס סיכוי/סיכון יוצא דופן!)",
    "CONFLUENCE_STATUS": "תמיכת EMA 50 + בולינגר תחתון + Call Flow שורי מובהק",
    "CONFLUENCE_SUMMARY": "התלכדות נדירה בין תמיכת ממוצע נע 50, רצועת בולינגר תחתונה, וזרימת אופציות שורית (P/C: 0.54) מייצרת נקודת כניסה בסבירות גבוהה.",

    # Scorecard Table
    "TABLE_ROWS": """
        <tr>
            <td><strong>אנליסט טכני</strong></td>
            <td><span class="badge-consensus sell" style="padding: 4px 10px; font-size: 13px;">דובי (-3)</span></td>
            <td>-3</td>
            <td>שבירת EMA 20, בדיקת תמיכת EMA 50 ($349.43), RSI ברמת 43.3 בתיקון בריא.</td>
        </tr>
        <tr>
            <td><strong>אנליסט סנטימנט ומומנטום</strong></td>
            <td><span class="badge-consensus sell" style="padding: 4px 10px; font-size: 13px;">דובי (-2)</span></td>
            <td>-2</td>
            <td>נר יורד יומי וחיתוך דובי במתנד MACD הממליצים על המתנה לאישור היפוך.</td>
        </tr>
        <tr>
            <td><strong>מנהל סיכונים</strong></td>
            <td><span class="badge-consensus" style="background: var(--accent-blue-bg); color: var(--accent-blue); padding: 4px 10px; font-size: 13px;">מוגן / סיכון נמוך</span></td>
            <td>0</td>
            <td>מעל EMA 200 ב-7.9%, Golden Cross שורי, ATR מתון (1.96%), רמת סיכון נמוכה.</td>
        </tr>
    """,

    # Swing Strategy
    "SWING_DIRECTION": "לונג סווינג (Long Swing Pullback)",
    "SWING_ENTRY": "$348.92 (לימיט פסיבי) או $349.79 (אישור היפוך)",
    "SWING_ENTRY_MODE": "לימיט פסיבי בתמיכה או אישור היפוך 15 דקות",
    "SWING_STOP": "$347.38 (-0.44% הדוק) או $345.35 (-1.02% שמרני)",
    "SWING_TARGET": "$355.90 (+2.00% ברוטו)",
    "SWING_RR": "1:4.55 (רווח $6.98 מול סיכון $1.54 ליחידה)",
    "SWING_NET_PROFIT": "+$142.83 (תשואה נטו: +1.43% לאחר עמלת IBKR ומס 25%)",
    "SWING_SUMMARY": "הזדמנות סווינג מהשורה הראשונה: סיכון דולרי מזערי של $43.12 בלבד בהקצאת $10,000, מול פוטנציאל רווח של $142.83 נטו בכיס תוך 2-5 ימי מסחר.",

    # Long Strategy
    "LONG_BIAS": "שורי חזק (Bullish Core Bank Leader)",
    "LONG_MA_STATUS": "+7.9% מעל EMA 200 ($323.31)",
    "LONG_STRUCTURE": "מבנה מגמה עולה רב-שנתי + Golden Cross פעיל",
    "LONG_ENTRY_METHOD": "איסוף מדורג (DCA) באזורי $340-$348",
    "LONG_PROTECTION": "$320.00 (שבירת ממוצע נע 200)",
    "LONG_SUMMARY": "הבנק הגדול והאיכותי בעולם. נהנה מסביבת ריבית גבוהה, רווחיות שיא ותשואת דיבידנד יציבה. מניית עוגן אידיאלית להשקעה ארוכת טווח."
}

res = render_debate_report(data)

# Also save standalone copy to artifacts directory
artifacts_dir = r"C:\Users\aviba\.gemini\antigravity\brain\5dfab7ef-76a3-4612-8cc7-1106a637d084"
if os.path.exists(artifacts_dir):
    art_path = os.path.join(artifacts_dir, "jpm_debate_report.html")
    with open(res["file_path"], "r", encoding="utf-8") as rf:
        content = rf.read()
    # Embed style.css
    style_path = os.path.join(PROJECT_ROOT, "stock_analysis_reports", "Report_Template", "style.css")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as sf:
            css = sf.read()
        content = content.replace('<link rel="stylesheet" href="Report_Template/style.css">', f"<style>\n{css}\n</style>")
    with open(art_path, "w", encoding="utf-8") as af:
        af.write(content)
    print(f"[+] Artifact copy saved: {art_path}")
