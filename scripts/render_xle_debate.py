# -*- coding: utf-8 -*-
import os
import sys
import json
from datetime import datetime

# Path setup
sys.path.insert(0, os.path.abspath('stock_analysis_reports/Report_Template'))
from render_report import render_debate_report

data = {
    'TICKER': 'XLE',
    'COMPANY_NAME': 'Energy Select Sector SPDR Fund',
    'EXCHANGE': 'AMEX / NYSE Arca',
    'TIMEFRAME': 'יומי (Daily 1D)',
    'DATE': f"{datetime.now().day} בספטמבר {datetime.now().year}",
    'DATE_RAW': datetime.now().strftime('%Y%m%d'),
    'PRICE': '$62.46 (-1.12%)',
    'NET_SCORE': '0 (הימנעות מסווינג - וטו שטח הפקר ו-R:R נחות)',
    'CONFIDENCE': 'זהירה / המתנה (Wait & Observe)',
    'TRADE_QUALITY_SCORE': '54 / 100 (סווינג פסול במחיר הנוכחי)',
    'CONSENSUS_CLASS': 'amber',
    'CONSENSUS_TEXT': 'הימנעות מסווינג במחיר הנוכחי (AVOID SWING / HOLD)',
    'SMART_MONEY_TITLE': 'יחס פוט/קול שורי (0.63) ואיסוף קולים עמוקים בכסף (Deep ITM Calls)',
    'SMART_MONEY_SUBTITLE': 'תזרים של 62.4K קולים (61.5%) מול 39K פוטים. הצטברות חריגה של מעל 31,000 חוזי קול ל-30 בספטמבר בסטרייקים $48 ו-$57.50.',
    'PUT_CALL_RATIO': '0.63',
    'OPTIONS_PC_RATIO': '0.63',
    'OPTIONS_BADGE_CLASS': 'green',
    'OPTIONS_BADGE_TEXT': 'איסוף שורי חזק (Bullish Flow)',
    'OPTIONS_CALL_VOL': '62,399',
    'OPTIONS_PUT_VOL': '39,084',
    'OPTIONS_DOMINANCE': 'דומיננטיות שורית מובהקת (61.5% Calls מול 38.5% Puts)',
    'OPTIONS_SUMMARY': 'איסוף חריג של מעל 31,000 חוזי Deep ITM Calls לפקיעת 30 בספטמבר בסטרייקים $48 ו-$57.50 (יחס V/OI > 16,000). פעילות זו מעידה על מינוף כסף חכם מוסדי עם דלתא גבוהה וצפי לעליות.',
    'UNUSUAL_EXPIRY': '30 בספטמבר 2026',
    'UNUSUAL_STRIKE': '$48.00 Call & $57.50 Call',
    'UNUSUAL_VOLUME': '31,185 חוזים (V/OI > 16,000!)',
    'UNUSUAL_SENTIMENT': 'שורי מובהק (Bullish In-The-Money Call Accumulation)',
    'HISTORICAL_WINNER': 'RSI Oversold / Overbought',
    'HISTORICAL_WINNER_STATS': '+17.48% תשואה • 100% הצלחה (3/3 עסקאות מנצחות) • 0% מקסימום Drawdown! יחס שארפ 50.3.',
    'HISTORICAL_TRAP': 'Donchian Breakout (ירידה של 8.6%- ומקדם רווח 1.72 בלבד)',
    'HISTORICAL_VALIDATION': 'הבקטסט מוכיח שקרן XLE מגיבה בצורה מושלמת לקניות בתיקוני RSI (סביב 40-45) במגמת עלייה ראשית, ומניבה 100% הצלחה ללא שחיקת הון.',
    'TECH_STANCE': 'שורי מעל ממוצעים (+2)',
    'TECH_SCORE_CLASS': 'green',
    'TECH_ITEMS': '''
        <li>גולדן קרוס מובהק: EMA 50 ($61.78) נסחר הרבה מעל EMA 200 ($56.26).</li>
        <li>מחיר הקרן נסחר 11.0% מעל ממוצע 200 ימים ($56.26) — מבנה שורי ארוך טווח חזק ביותר.</li>
        <li>מדד RSI ברמת 44.4 (אזור תיקון קלאסי ואידיאלי לאיסוף בתוך מגמת עלייה).</li>
        <li>רצועת בולינגר תחתונה ($61.81) מספקת בלימה ותמיכה דינמית מיידית.</li>
    ''',
    'TECH_SUMMARY': 'תיקון בריא של 5.0% משיא 20 יום, התכנסות ישירה על ממוצע נע 50 ובולינגר תחתון.',
    'SENT_STANCE': 'ניטרלי / זהירות מאקרו (0)',
    'SENT_SCORE_CLASS': 'amber',
    'SENT_ITEMS': '''
        <li>נאום חבר הפד ויליאמס היום ב-17:05 שעון ישראל מייצר אי-ודאות רגעית.</li>
        <li>ירידה מתונה בחוזי הנפט הגולמי (WTI/Brent) שבלמה את המומנטום קצר הטווח.</li>
        <li>יחס פוט/קול מוסדי שורי (0.63) המעיד על היעדר פאניקת מכירות.</li>
    ''',
    'SENT_SUMMARY': 'המתנה מחושבת עד לסיום אירוע המאקרו של הפד לאישור פריצה בנר 15 דקות ירוק.',
    'RISK_STANCE': 'וטו מוחלט - שטח הפקר (-2 / וטו)',
    'RISK_SCORE_CLASS': 'red',
    'RISK_ITEMS': '''
        <li><strong>וטו מנהל הסיכונים:</strong> יחס הסיכוי-סיכון מול התקרה הקרובה (EMA 20 ב-$63.45) עומד על 1:0.71 בלבד (+1.33% מול סיכון 1.87%-). זהו יחס נחות הפוסל את הטרייד לפי חוקי הסיסטם!</li>
        <li><strong>מלכודת שטח הפקר (No Man's Land):</strong> המחיר כרגע קרוב מדי לתקרה ($0.83) ורחוק מדי מהתמיכה המוגנת ($1.17 ל-$61.45). כניסה כעת מהווה סיכון אסימטרי לרעת הסוחר.</li>
        <li><strong>איסור שימוש ב-TP2 כתירוץ:</strong> אסור לפתוח טרייד שמסתמך על פריצה של ממוצע 20 כשהמכשול הראשון מציע יחס עיוות. יעד TP2 אינו תחליף לכדאיות עסקית בסיסית.</li>
        <li><strong>הנחיית פעולה מותנית:</strong> המתנה לאחד משני תרחישים בלבד: בדיקת תמיכה ב-$61.85 (R:R של 1:4.0) או פריצה מוכחת מעל $63.55.</li>
    ''',
    'RISK_SUMMARY': 'וטו מוחלט על פתיחת סווינג ב-$62.62. יחס R:R של 1:0.71 לממוצע 20 מהווה סיכון מיותר.',
    'SUPPORT_LEVEL': '$61.81 (בולינגר תחתון) • $61.78 (EMA 50) • $61.45 (סטופ מבני מוגן)',
    'PIVOT_LEVEL': '$61.92',
    'RESISTANCE_LEVEL': '$63.77 (EMA 20) • $64.82 (R1) • $66.74 (R2)',
    'ATR_VALUE': '$1.32 (2.12% תנודתיות יומית)',
    'CALCULATED_RR': '1:0.71 מול ממוצע 20 (פסול!) • 1:4.0 בתרחיש תמיכה $61.85',
    'CONFLUENCE_STATUS': 'Golden Cross + Bollinger Lower Band Bounce + 0.63 Put/Call Flow',
    'CONFLUENCE_SUMMARY': 'התלכדות של 4 גורמים שווריים: תמיכת בולינגר, גולדן קרוס, רכישת קולים עמוקים בכסף, ו-100% הצלחה בבקטסט RSI.',
    'TABLE_ROWS': '''
        <tr>
            <td><strong>אנליסט טכני</strong></td>
            <td><span class="badge-consensus buy" style="padding: 4px 10px; font-size: 13px;">שורי (+2)</span></td>
            <td>מחיר מעל EMA 200 ב-11%, בדיקת תמיכה ב-EMA 50 ($61.78) ורצועת בולינגר, RSI 44.4 מושלם.</td>
        </tr>
        <tr>
            <td><strong>אנליסט מומנטום</strong></td>
            <td><span class="badge-consensus amber" style="padding: 4px 10px; font-size: 13px;">זהיר (0)</span></td>
            <td>אירוע פד ב-17:05 מחייב המתנה; תזרימי האופציות (P/C 0.63) מאשרים כניסת כסף חכם לקולים.</td>
        </tr>
        <tr>
            <td><strong>מנהל סיכונים</strong></td>
            <td><span class="badge-consensus red" style="padding: 4px 10px; font-size: 13px;">וטו מוחלט (-2)</span></td>
            <td>וטו על סווינג במחיר הנוכחי! R:R של 1:0.71 מול ממוצע 20 נפסל מיידית; שטח הפקר מסוכן.</td>
        </tr>
    ''',
    'SWING_DIRECTION': 'הימנעות מסווינג (עמדת המתנה מחוץ לשוק - No Trade)',
    'SWING_ENTRY': '$61.85 (תרחיש איסוף תמיכה) או מעל $63.55 (תרחיש פריצת מומנטום)',
    'SWING_ENTRY_MODE': "המתנה על הגדר • כניסה מותנית בלבד לפי התרחישים",
    'SWING_STOP': '$61.45 (בתרחיש תמיכה - סיכון $0.40 בלבד) • $63.00 (בתרחיש פריצה)',
    'WHIPSAW_SHIELD_STATUS': '🛡️ פעילה (מניעת כניסה בשטח הפקר ללא שולי ביטחון)',
    'SWING_TARGET': 'תרחיש תמיכה: $63.45 (+2.58%) • תרחיש פריצה: $64.80 (+1.97%)',
    'SWING_RR': '1:4.0 בתרחיש תמיכה • 1:2.7 בתרחיש פריצה (במחיר הנוכחי: 1:0.71 - פסול!)',
    'SWING_ALLOCATION': '0 מניות (המתנה מחוץ לשוק - $0 סיכון)',
    'SWING_NET_PROFIT': '$0.00 נטו (אין טרייד פעיל עד להתממשות תנאי סף)',
    'SWING_SUMMARY': 'הכרעת הוועדה: אין טרייד סווינג במחיר הנוכחי ($62.62)! הטרייד נפסל עסקית בשל יחס סיכוי-סיכון נחות (1:0.71 מול ממוצע 20) ורווח של 1.33% בלבד. הוועדה ממליצה להמתין על הגדר לאיסוף ב-$61.85 (R:R מעולה של 1:4.0) או לפריצה מעל $63.55.',
    'LONG_BIAS': 'לונג השקעה שורי (Macro Energy & Dividends)',
    'LONG_STRUCTURE': 'סקטור האנרגיה מציג תזרים מזומנים חופשי אדיר, רכישות חוזרות (Buybacks) ותשואת דיבידנד של ~3.2%.',
    'LONG_MA_STATUS': 'מגמת עלייה שנתית מובהקת (+42.5% ב-12 החודשים האחרונים), נסחר מעל ממוצע 200 ימים.',
    'LONG_ENTRY_METHOD': 'איסוף מדורג (DCA) באזורי $60–$62 סביב ממוצע 50 יום.',
    'LONG_PROTECTION': 'שבירת תמיכת ממוצע 200 ימים ($56.20).',
    'LONG_SUMMARY': 'נכס עוגן איכותי בתיק להגנה מאינפלציה ותשואת דיבידנד רציפה.'
}

res = render_debate_report(data)

# Also create standalone copy in brain artifact directory
brain_dir = r'C:\Users\aviba\.gemini\antigravity\brain\5dfab7ef-76a3-4612-8cc7-1106a637d084'
css_file = os.path.abspath('stock_analysis_reports/Report_Template/style.css')
with open(res['file_path'], 'r', encoding='utf-8') as f:
    html_c = f.read()
with open(css_file, 'r', encoding='utf-8') as cf:
    css_c = cf.read()
embedded = html_c.replace('<link rel="stylesheet" href="Report_Template/style.css">', f'<style>\n{css_c}\n</style>')
with open(os.path.join(brain_dir, 'xle_debate_report.html'), 'w', encoding='utf-8') as af:
    af.write(embedded)
print('Artifact created at:', os.path.join(brain_dir, 'xle_debate_report.html'))
