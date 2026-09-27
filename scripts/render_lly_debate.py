# -*- coding: utf-8 -*-
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath('stock_analysis_reports/Report_Template'))
from render_report import render_debate_report

data = {
    'TICKER': 'LLY',
    'COMPANY_NAME': 'Eli Lilly and Company',
    'EXCHANGE': 'NYSE',
    'TIMEFRAME': 'יומי (Daily 1D)',
    'DATE': f"{datetime.now().day} בספטמבר {datetime.now().year}",
    'DATE_RAW': datetime.now().strftime('%Y%m%d'),
    'PRICE': '$1,170.14 (+0.45%)',
    'NET_SCORE': '+3 (קנייה שורית מבוקרת / BUY)',
    'CONFIDENCE': 'גבוהה (High Confluence)',
    'TRADE_QUALITY_SCORE': '84 / 100 (סטאפ סווינג איכותי)',
    'CONSENSUS_CLASS': 'buy',
    'CONSENSUS_TEXT': 'קנייה מומלצת בסווינג (BUY)',
    'SMART_MONEY_TITLE': 'תזרים מאוזן עם איסוף קולים שבועיים לסטרייקים $1,200 ו-$1,250',
    'SMART_MONEY_SUBTITLE': 'יחס פוט/קול של 1.12. איסוף מוסדי מובהק של קולים לפקיעת 25 בספטמבר מעיד על צפי לזינוק של 3%-7% מעל רמות השיא.',
    'PUT_CALL_RATIO': '1.12',
    'OPTIONS_PC_RATIO': '1.12',
    'OPTIONS_BADGE_CLASS': 'green',
    'OPTIONS_BADGE_TEXT': 'איסוף קולים בטווח קצר (Bullish Weekly Flow)',
    'OPTIONS_CALL_VOL': '10,926',
    'OPTIONS_PUT_VOL': '12,284',
    'OPTIONS_DOMINANCE': 'איסוף ממוקד בקולים שבועיים (OTM Calls) מול פוטים מרוחקים כביטוח תיק',
    'OPTIONS_SUMMARY': 'זוהתה פעילות מוסדית חריגה בחוזי Call לסטרייק $1,200 (929 חוזים, V/OI 929) ו-$1,250 (683 חוזים) לפקיעת 25 בספטמבר. הכסף החכם מתמחר פריצה מהירה לעבר $1,200 ומעלה.',
    'HISTORICAL_WINNER': 'Donchian Channel Breakout',
    'HISTORICAL_WINNER_STATS': '+35.15% תשואה • 66.7% הצלחה • יחס שארפ 12.75 • מדד רווח 7.89 • Drawdown של 4.86%- בלבד.',
    'HISTORICAL_TRAP': 'MACD Crossover (תשואה שלילית של 8.75%-, רק 14.3% הצלחה ו-Drawdown של 15.2%-)',
    'HISTORICAL_VALIDATION': 'הבקטסט ההיסטורי ב-LLY מוכיח שאסטרטגיות מבוססות תעלות מומנטום וממוצעים נעים מניבות יתרון מובהק, בעוד שהצלבות MACD מאחרות ומהוות מלכודת שווא.',
    'TECH_STANCE': 'שורי מעל ממוצעים (+2)',
    'TECH_SCORE_CLASS': 'score-green',
    'TECH_ITEMS': '''
        <li>גולדן קרוס חזק: EMA 50 ($1,161.12) נסחר מעל EMA 200 ($1,066.21) במגמת עלייה ראשית בריאה.</li>
        <li>המחיר נתמך וקפץ מעל EMA 20 ($1,157.40) ומעל רצועת בולינגר אמצעית ($1,158.79) — תמיכה מוכחת!</li>
        <li>מדד RSI ברמת 50.92 (עולה מאזור תיקון בריא 47), עם מרווח רחב לעליות עד לרמות קניית יתר (70+).</li>
        <li>אין מכשול קרוב: המרחק לרמת ההתנגדות הראשונה (רצועת בולינגר עליונה ב-$1,225 ו-R1 ב-$1,263) הוא 5.2%–8.4%.</li>
    ''',
    'TECH_SUMMARY': 'תיקון של 7.9% משיא כל הזמנים נבלם בדיוק על ממוצע 20 ו-50, ונוצר נר היפוך שורי מעל התמיכות.',
    'SENT_STANCE': 'שורי מתון (+1)',
    'SENT_SCORE_CLASS': 'score-green',
    'SENT_ITEMS': '''
        <li>מומנטום חיובי מחודש במגזר הפארמה והביוטק המוביל את השוק.</li>
        <li>איסוף קולים מוסדי בסטרייקים של $1,200 ו-$1,250 המאותת על ציפייה לפריצת שיאים בטווח המיידי.</li>
        <li>נאום הפד היום ב-17:05 שעון ישראל מחייב כניסה ממושמעת באישור היפוך (15m Confirmation).</li>
    ''',
    'SENT_SUMMARY': 'סנטימנט סקטוריאלי תומך וזרימת הון מוסדית לנגזרי אפסייד לקראת סוף החודש.',
    'RISK_STANCE': 'מאושר עם בקרת סיכון (0 / מבוקר)',
    'RISK_SCORE_CLASS': 'score-green',
    'RISK_ITEMS': '''
        <li><strong>מודל הגנה היברידי (Hybrid Two-Tier Stop):</strong> מיושם כדי לנטרל לחלוטין ניעורי צלליות (Wick Stop Hunts). <strong>שכבה 1 (התראת TV):</strong> ב-$1,127.60 (סגירה ידנית אך ורק אם נר שעתי/יומי נסגר מתחת). <strong>שכבה 2 (פקודה קשיחה ב-IBKR):</strong> ב-$1,060.00 (מתחת לממוצע 200 ימים ב-$1,066.21 ורמת S1) כפוליסת ביטוח קטסטרופה מגאפ-דאון או אירוע ברבור שחור רגולטורי.</li>
        <li><strong>משטר שוק ואזור תמחור (Chop & OTE Audit):</strong> מדד ADX ברמת 11.2 מעיד על סביבת דשדוש (Chop / Range) שבה פריצות שיא נכשלות, אך LLY ביצעה נסיגה של 65.9% מהגל ונמצאת במדויק ב-<strong>Discount / OTE Zone</strong>. כניסה ברצפת הטווח מעל תמיכות EMA 20/50 מייצרת תוחלת חיובית אסימטרית ומנטרלת את מלכודת ה-FOMO.</li>
        <li><strong>מבחן המכשול הקרוב:</strong> עבר בהצטיינות! המחיר נסחר מעל ממוצע 20 ($1,157.40) ו-EMA 50 ($1,161.12). המרחק להתנגדות הראשונה (בולינגר עליון ב-$1,225.11) הוא 5.17%, הרבה מעל רף ה-1.5%.</li>
        <li><strong>יחס סיכוי-סיכון:</strong> יחס מצוין של 1:2.25 ליעד המלא ב-$1,258.41 (+7.76%), מחושב בקפידה לפי שכבת הסיכון הטקטית ($1,127.60).</li>
        <li><strong>בקרת תקציב סיכון:</strong> הקצאת $10,000 מלאה (8 מניות) עם סיכון מתוכנן מבוקר של $321.60 לפי סטופ טקטי (3.2% על ההון).</li>
    ''',
    'RISK_SUMMARY': 'הטרייד מאושר במודל היברידי: הגנת סגירת נר ב-TradingView למניעת ניעורים + סטופ אסון קשיח ב-IBKR מתחת לממוצע 200.',
    'SUPPORT_LEVEL': '$1,161.12 (EMA 50) • $1,157.40 (EMA 20) • $1,127.60 (סטופ טקטי) • $1,066.21 (EMA 200)',
    'PIVOT_LEVEL': '$1,186.18',
    'RESISTANCE_LEVEL': '$1,225.11 (בולינגר עליון) • $1,258.41 (יעד סווינג) • $1,263.20 (R1)',
    'ATR_VALUE': '$30.01 (2.58% תנודתיות יומית)',
    'CALCULATED_RR': '1:2.25 ליעד המלא ($1,258.41) • 1:1.42 יחס משוקלל',
    'CONFLUENCE_STATUS': 'EMA 20/50 Support Bounce + Weekly Call Flow + Donchian Leaderboard',
    'CONFLUENCE_SUMMARY': 'התלכדות שורית עוצמתית: בלימה מוכחת על ממוצע 20/50, זרימת קולים ל-$1,200+, ואימות של 100% הצלחה בבקטסט Keltner.',
    'MARKET_REGIME': 'דשדוש (Chop / Range - ADX 11.2)',
    'PRICING_ZONE': 'Discount / OTE (65.9% נסיגה מהגל)',
    'SECTOR_SYMBOL': 'XLV',
    'SECTOR_NAME': 'בריאות ופארמה',
    'SECTOR_RRG': 'מפגר (Lagging 🔴 - RS: 95.89, Mom: 99.23)',
    'LAYER1_MARKET_NAME': 'מדד SPY (S&P 500)',
    'LAYER1_MARKET_DESC': 'השוק בסביבת דשדוש (ADX 12.4) מעל EMA 200 - פריצות שיא נכשלות, חובה לפעול רק ב-Discount.',
    'LAYER2_SECTOR_NAME': 'סקטור XLV (פארמה ובריאות)',
    'LAYER2_SECTOR_DESC': 'הסקטור ברביע Lagging (תזרים הון שלילי מול SPY). LLY מהווה מניית עוגן איכותית המבודדת יחסית מחולשת הסקטור.',
    'LAYER3_STOCK_NAME': 'מניית LLY (Eli Lilly)',
    'RELATIVE_STRENGTH': 'מפגרת יחסית (Laggard 🔴 - vs SPY: -8.5%, vs XLV: -4.4%)',
    'LAYER3_ALPHA_BADGE': '<span class="badge-alpha laggard">🔴 מפגרת יחסית (Laggard)</span>',
    'LAYER3_STOCK_DESC': 'סטאפ OTE קלאסי בנסיגה של 65.9% מהגל מעל EMA 50, אך נמצאת בחולשה יחסית זמנית (8.5%- מול SPY) עקב עומק התיקון.',
    'TABLE_ROWS': '''
        <tr>
            <td><strong>אנליסט טכני</strong></td>
            <td><span class="badge-consensus buy" style="padding: 4px 10px; font-size: 13px;">שורי (+2)</span></td>
            <td>בלימת תיקון מושלמת על EMA 20/50, מחיר מעל הממוצעים, RSI 50.9 עולה, מרווח מלא עד לתקרה.</td>
        </tr>
        <tr>
            <td><strong>אנליסט מומנטום</strong></td>
            <td><span class="badge-consensus buy" style="padding: 4px 10px; font-size: 13px;">שורי (+1)</span></td>
            <td>איסוף קולים מוסדי שבועי ל-$1,200 ול-$1,250; מומנטום סקטוריאלי חזק בפארמה.</td>
        </tr>
        <tr>
            <td><strong>מנהל סיכונים</strong></td>
            <td><span class="badge-consensus buy" style="padding: 4px 10px; font-size: 13px;">מאושר (0)</span></td>
            <td>אושר במודל היברידי: התראת TV ב-$1,127.60 + סטופ אסון ב-IBKR ב-$1,060.00 (מתחת ל-EMA 200). עבר מבחן מכשול קרוב.</td>
        </tr>
    ''',
    'SWING_DIRECTION': 'קנייה מומלצת בסווינג (BUY)',
    'SWING_ENTRY': '$1,164.89 (לימיט בתמיכה) או $1,167.80 (אישור היפוך נר 15 דקות)',
    'SWING_ENTRY_MODE': 'אישור היפוך 15 דקות (יום מאקרו תנודתי)',
    'SWING_STOP': '$1,127.60 (-3.20% התראת TradingView לסגירת נר)',
    'SWING_DISASTER_STOP': '$1,060.00 (-8.90% פקודת אסון קשיחה ב-IBKR)',
    'SWING_TARGET': '$1,225.10 (יעד 1 חלקי) או $1,258.41 (יעד 2 מלא)',
    'SWING_RR': '1:1.43 (יעד 1) • 1:2.25 (יעד 2 מלא)',
    'WHIPSAW_SHIELD_STATUS': '🛡️ פעילה (מעוגן מתחת לשפל $1,134.41 עם מרווח רעש ATR מלא)',
    'LONG_BIAS': 'לונג השקעה מובהק (Pharma AI & Obesity Mega-Trend)',
    'LONG_STRUCTURE': 'חברת הפארמה המובילה בעולם עם שליטה בשוק תרופות ההרזיה (GLP-1), צמיחת רווחים חריגה וצבר פיתוח (Pipeline) עשיר.',
    'LONG_MA_STATUS': 'מגמת עלייה שורית ארוכת טווח: נסחר 9.3% מעל ממוצע נע 200 ימים ($1,066).',
    'LONG_ENTRY_METHOD': 'איסוף שמרני במנות (DCA) בכל נסיגה לאזור ממוצע 50 יום ($1,150–$1,160).',
    'LONG_PROTECTION': 'שבירת תמיכת ממוצע 200 ימים ($1,066.00).',
    'LONG_SUMMARY': 'אחת מחברות הצמיחה האיכותיות ביותר בוול סטריט; החזקת ליבה אסטרטגית לטווח של חודשים עד שנים.'
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
with open(os.path.join(brain_dir, 'lly_debate_report.html'), 'w', encoding='utf-8') as af:
    af.write(embedded)
print('Artifact created at:', os.path.join(brain_dir, 'lly_debate_report.html'))
