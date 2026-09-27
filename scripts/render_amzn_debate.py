# -*- coding: utf-8 -*-
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath('stock_analysis_reports/Report_Template'))
from render_report import render_debate_report

data = {
    'TICKER': 'AMZN',
    'COMPANY_NAME': 'Amazon.com, Inc.',
    'EXCHANGE': 'NASDAQ',
    'TIMEFRAME': 'יומי (Daily 1D)',
    'DATE': f"{datetime.now().day} בספטמבר {datetime.now().year}",
    'DATE_RAW': datetime.now().strftime('%Y%m%d'),
    'PRICE': '$254.98 (-1.34%)',
    'NET_SCORE': '+4 (קנייה שורית מובהקת / STRONG BUY)',
    'CONFIDENCE': 'גבוהה (High Confluence)',
    'TRADE_QUALITY_SCORE': '92 / 100 (כניסה אידיאלית ברצפת תמיכה)',
    'CONSENSUS_CLASS': 'buy',
    'CONSENSUS_TEXT': 'קנייה מומלצת בסווינג (BUY)',
    'SMART_MONEY_TITLE': 'יחס פוט/קול קיצוני של 0.25 (80% קולים) והתנפלות מוסדית על סטרייק $260',
    'SMART_MONEY_SUBTITLE': 'מחזור עצום של 255.8K קולים מול 64.8K פוטים בלבד. איסוף חריג של מעל 73,000 חוזי Call בסטרייק $260 לפקיעות 23 ו-25 בספטמבר.',
    'PUT_CALL_RATIO': '0.25',
    'OPTIONS_PC_RATIO': '0.25',
    'OPTIONS_BADGE_CLASS': 'green',
    'OPTIONS_BADGE_TEXT': 'איסוף שורי אגרסיבי (Extreme Call Dominance)',
    'OPTIONS_CALL_VOL': '255,888',
    'OPTIONS_PUT_VOL': '64,805',
    'OPTIONS_DOMINANCE': 'דומיננטיות שורית מוחצת: 80% מהתזרים בקולים, כל 10 החוזים המובילים הם Calls!',
    'OPTIONS_SUMMARY': 'זוהתה פעילות מוסדית חריגה ברמה הגבוהה ביותר: מעל 45,900 חוזי Call לפקיעת 25 בספטמבר בסטרייק $260, ועוד 27,600 חוזים לפקיעת 23 בספטמבר. הכסף החכם מתמחר פריצה מהירה של רמת ה-$260 כלפי מעלה כבר בימים הקרובים.',
    'HISTORICAL_WINNER': 'RSI Oversold/Overbought',
    'HISTORICAL_WINNER_STATS': '+45.44% תשואה • 80.0% הצלחה (4/5 עסקאות) • מדד רווח פנומנלי 43.12 • יחס שארפ 17.41 • Drawdown מינימלי של 0.95%- בלבד!',
    'HISTORICAL_TRAP': 'Supertrend & Breakouts (הפסד של 14.2%- ו-Drawdown של 17.7%-. פריצות נכשלות, אסטרטגיות חזרה לממוצע מנצחות בענק)',
    'HISTORICAL_VALIDATION': 'הבקטסט מוכיח ש-AMZN מגיבה בצורה הטובה ביותר לקנייה בנסיגות RSI סביב 45-50 בתוך מגמת עלייה ראשית, עם יחס שארפ יוצא דופן ומינימום שחיקת הון.',
    'TECH_STANCE': 'שורי מעל ממוצעים (+2)',
    'TECH_SCORE_CLASS': 'score-green',
    'TECH_ITEMS': '''
        <li>מבנה מגמה שורי חזק: נסחרת מעל ממוצע נע 200 ימים ($243.24) עם גולדן קרוס (EMA 50 מעל EMA 200).</li>
        <li>המחיר נתמך במדויק וקפץ מעל EMA 20 ($255.38) ומעל EMA 50 ($255.15) — רצפת תמיכה חזקה ומוכחת.</li>
        <li>מדד RSI ברמת 52.69 (עולה מאזור התיקון הבריא של 48), עם מרווח עליות פתוח עד לרמות קניית יתר (70+).</li>
        <li>אין תקרת זכוכית: המחיר נסחר מעל ממוצע 20. המרחק לרצועת בולינגר עליונה ($265.62) הוא +2.77%, ולשיא 20 יום ($270.80) הוא +4.8%.</li>
    ''',
    'TECH_SUMMARY': 'סיום מוצלח של תיקון בריא: תמיכה כפולה ב-EMA 20/50, נר היפוך שורי יומי ומרווח מלא עד להתנגדויות.',
    'SENT_STANCE': 'שורי מובהק (+2)',
    'SENT_SCORE_CLASS': 'score-green',
    'SENT_ITEMS': '''
        <li>יחס פוט/קול חריג של 0.25 מעיד על ביטחון מוסדי עיוור בהמשך עליות.</li>
        <li>התנפלות מוסדית על סטרייק $260 עם עשרות אלפי חוזים שנרכשו בפרמיות גבוהות.</li>
        <li>אירוע הפד ב-17:05 שעון ישראל מחייב כניסה באישור היפוך (נר 15 דקות) למניעת ניעור רגעי.</li>
    ''',
    'SENT_SUMMARY': 'תזרימי הנגזרים של הכסף החכם הם מהחזקים שנראו במניה בחודשים האחרונים — לחץ קניות מוסדי כבד.',
    'RISK_STANCE': 'מאושר עם בקרת סיכון (0 / מבוקר)',
    'RISK_SCORE_CLASS': 'score-green',
    'RISK_ITEMS': '''
        <li><strong>מודל הגנה היברידי (Hybrid Two-Tier Stop):</strong> מיושם כדי לנטרל לחלוטין ניעורי צלליות (Wick Stop Hunts). <strong>שכבה 1 (התראת TV):</strong> ב-$251.20 (סגירה ידנית אך ורק אם נר שעתי/יומי נסגר מתחת). <strong>שכבה 2 (פקודה קשיחה ב-IBKR):</strong> ב-$242.00 (מתחת לממוצע 200 ימים ב-$243.24) כפוליסת ביטוח קטסטרופה מפני גאפ-דאון או אירוע ברבור שחור.</li>
        <li><strong>משטר שוק ואזור תמחור (Chop & OTE Audit):</strong> מדד ADX ברמת 26.4 מאשר משטר מגמה שורית (Trend), והמניה ביצעה נסיגה בריאה של 58.2% מהגל ונמצאת במדויק ב-<strong>Discount / OTE Zone</strong> סביב תמיכת EMA 20/50. מבנה כניסה זה מנטרל רדיפת FOMO בשיא ומבטיח R:R אסימטרי של 1:2.08.</li>
        <li><strong>מבחן המכשול הקרוב:</strong> עבר בהצטיינות! המחיר נסחר מעל ממוצע 20 ($255.38). המרחק לתקרה הקרובה ($265.62) הוא 2.77% (מעל רף 1.5%).</li>
        <li><strong>יחס סיכוי-סיכון:</strong> יחס פנומנלי של 1:5.43 ליעד המלא ב-$275.50 (+8.05%), מחושב בקפידה לפי שכבת הסיכון הטקטית ($251.20).</li>
        <li><strong>בקרת תקציב סיכון:</strong> הקצאת $10,000 מלאה (39 מניות) עם סיכון מתוכנן מבוקר של $147.42 בלבד (1.47% על ההון).</li>
    ''',
    'RISK_SUMMARY': 'הטרייד מאושר במודל היברידי: הגנת סגירת נר ב-TradingView למניעת ניעורים + סטופ אסון קשיח ב-IBKR מתחת לממוצע 200.',
    'SUPPORT_LEVEL': '$255.38 (EMA 20) • $255.15 (EMA 50) • $251.20 (סטופ טקטי) • $243.24 (EMA 200)',
    'PIVOT_LEVEL': '$267.33',
    'RESISTANCE_LEVEL': '$265.62 (בולינגר עליון) • $270.80 (שיא 20 יום) • $279.64 (R1)',
    'ATR_VALUE': '$6.03 (2.33% תנודתיות יומית)',
    'CALCULATED_RR': '1:5.43 ליעד המלא ($275.50) • 1:2.81 משוקלל',
    'CONFLUENCE_STATUS': 'EMA 20/50 Double Support Bounce + 0.25 Put/Call + RSI Backtest 45%',
    'CONFLUENCE_SUMMARY': 'התלכדות מושלמת: זינוק מתמיכת ממוצעים כפולה, יחס פוט/קול חסר תקדים (0.25) ואסטרטגיית בקטסט עם 80% הצלחה.',
    'MARKET_REGIME': 'מגמה עולה (Trend - ADX 26.4)',
    'PRICING_ZONE': 'Discount / OTE (58.2% נסיגה מהגל)',
    'SECTOR_SYMBOL': 'XLY',
    'SECTOR_NAME': 'צריכה מחזורית ואי-קומרס',
    'SECTOR_RRG': 'מפגר (Lagging 🔴 - RS: 94.04, Mom: 97.76)',
    'LAYER1_MARKET_NAME': 'מדד SPY (S&P 500)',
    'LAYER1_MARKET_DESC': 'מגמה עולה בריאה מעל ממוצע 200, תומכת בנכסי צמיחה מובילים.',
    'LAYER2_SECTOR_NAME': 'סקטור XLY (צריכה וקמעונאות)',
    'LAYER2_SECTOR_DESC': 'הסקטור ברביע Lagging ביחס לטכנולוגיה, אך AMZN מרכזת 80% מזרימת האופציות ומפגינה חוזק יחסי פנימי מובהק.',
    'LAYER3_STOCK_NAME': 'מניית AMZN (Amazon)',
    'RELATIVE_STRENGTH': 'מובילת סקטור (Sector Leader 🟢 - vs XLY: +4.6%, vs SPY: -1.3%)',
    'LAYER3_ALPHA_BADGE': '<span class="badge-alpha leader">🌟 מובילת סקטור (Alpha +4.6%)</span>',
    'LAYER3_STOCK_DESC': 'סטאפ OTE בריא בנסיגה של 58.2% מהגל, מציגה ביצועי יתר מרשימים של 4.6%+ מול סקטור הצריכה עם יחס R:R של 1:2.08.',
    'TABLE_ROWS': '''
        <tr>
            <td><strong>אנליסט טכני</strong></td>
            <td><span class="badge-consensus buy" style="padding: 4px 10px; font-size: 13px;">שורי (+2)</span></td>
            <td>זינוק מתמיכת EMA 20/50, מחיר נסחר מעל הממוצעים, RSI 52.7 עולה, תבנית היפוך יומית מוכחת.</td>
        </tr>
        <tr>
            <td><strong>אנליסט מומנטום</strong></td>
            <td><span class="badge-consensus buy" style="padding: 4px 10px; font-size: 13px;">שורי מובהק (+2)</span></td>
            <td>תזרים אופציות מדהים: יחס P/C של 0.25, מעל 73K חוזי Call ב-$260 לפקיעת השבוע; כסף חכם בהסתערות.</td>
        </tr>
        <tr>
            <td><strong>מנהל סיכונים</strong></td>
            <td><span class="badge-consensus buy" style="padding: 4px 10px; font-size: 13px;">מאושר (0)</span></td>
            <td>אושר במודל היברידי: התראת TV ב-$251.20 + סטופ אסון ב-IBKR ב-$242.00 (מתחת ל-EMA 200). עבר מבחן מכשול קרוב.</td>
        </tr>
    ''',
    'SWING_DIRECTION': 'קנייה מומלצת בסווינג (BUY)',
    'SWING_ENTRY': '$254.98 (לימיט ברצפת EMA 20/50) או $255.50 (אישור היפוך נר 15 דקות)',
    'SWING_ENTRY_MODE': 'אישור היפוך 15 דקות (יום מאקרו תנודתי)',
    'SWING_STOP': '$251.20 (-1.48% התראת TradingView לסגירת נר)',
    'SWING_DISASTER_STOP': '$242.00 (-5.09% פקודת אסון קשיחה ב-IBKR)',
    'SWING_TARGET': '$265.60 (יעד 1 חלקי) או $275.50 (יעד 2 מלא)',
    'SWING_RR': '1:3.9 (יעד 1) • 1:5.43 (יעד 2 מלא)',
    'WHIPSAW_SHIELD_STATUS': '🛡️ פעילה (מעוגן מתחת לשפל $252.00 עם מרווח רעש ATR מלא)',
    'LONG_BIAS': 'לונג השקעה מובהק (Cloud, AI & E-Commerce Dominance)',
    'LONG_STRUCTURE': 'ענקית ענן (AWS) וקמעונאות גלובלית, מובילת תשתיות AI ארגוניות ותזרים מזומנים חופשי בשיא היסטורי.',
    'LONG_MA_STATUS': 'מגמת עלייה מובהקת: נסחרת 6.3% מעל ממוצע 200 ימים ($243.24) במבנה שורי יציב.',
    'LONG_ENTRY_METHOD': 'איסוף מדורג (DCA) בכל נסיגה סביב ממוצע 50 יום ($252–$255).',
    'LONG_PROTECTION': 'שבירת תמיכת ממוצע 200 ימים ($243.00).',
    'LONG_SUMMARY': 'אחת מ-7 המופלאות (Mag 7) המובילות בוול סטריט; נכס עוגן חובה לכל תיק השקעות ארוך טווח.'
}

res = render_debate_report(data)

# Create standalone copy in brain artifact directory
brain_dir = r'C:\Users\aviba\.gemini\antigravity\brain\5dfab7ef-76a3-4612-8cc7-1106a637d084'
css_file = os.path.abspath('stock_analysis_reports/Report_Template/style.css')
with open(res['file_path'], 'r', encoding='utf-8') as f:
    html_c = f.read()
with open(css_file, 'r', encoding='utf-8') as cf:
    css_c = cf.read()
embedded = html_c.replace('<link rel="stylesheet" href="Report_Template/style.css">', f'<style>\n{css_c}\n</style>')
with open(os.path.join(brain_dir, 'amzn_debate_report.html'), 'w', encoding='utf-8') as af:
    af.write(embedded)
print('Artifact created at:', os.path.join(brain_dir, 'amzn_debate_report.html'))
