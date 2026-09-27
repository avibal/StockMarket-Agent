import os
import json
import sys
from datetime import datetime

import socket

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(TEMPLATE_DIR, "template.html")
REPORTS_DIR = os.path.abspath(os.path.join(TEMPLATE_DIR, ".."))

def get_local_ip() -> str:
    """Dynamically detects the current machine LAN IPv4 address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def render_debate_report(data: dict, filename: str = None) -> dict:
    """
    Renders the debate template using provided data dictionary and saves it
    to stock_analysis_reports/YYYYMMDD_<TICKER>_DEBATE.html.
    """
    if not os.path.exists(TEMPLATE_FILE):
        raise FileNotFoundError(f"Template not found at: {TEMPLATE_FILE}")
        
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        html = f.read()
        
    ticker = data.get("TICKER", "UNKNOWN")
    date_str = data.get("DATE_RAW", datetime.now().strftime("%Y%m%d"))
    
    if not filename:
        filename = f"{date_str}_{ticker}_DEBATE.html"
        
    output_path = os.path.join(REPORTS_DIR, filename)
    
    # Aliases for company name
    if "NAME" not in data:
        data["NAME"] = data.get("COMPANY_NAME", ticker)
    if "COMPANY_NAME" not in data:
        data["COMPANY_NAME"] = data.get("NAME", ticker)
    
    # Ensure consensus class is normalized
    consensus_class = data.get("CONSENSUS_CLASS", "amber").lower().replace(" ", "-")
    if "buy" in consensus_class:
        data["CONSENSUS_CLASS"] = "buy"
    elif "sell" in consensus_class:
        data["CONSENSUS_CLASS"] = "sell"
    else:
        data["CONSENSUS_CLASS"] = "amber"

    # Date defaults
    if "DATE" not in data:
        data["DATE"] = datetime.now().strftime("%d/%m/%Y")

    def _derive_score_class(stance_text):
        s = str(stance_text)
        if any(w in s for w in ["+", "שורי", "חיובי", "קנייה"]):
            return "score-green"
        elif any(w in s for w in ["-", "דובי", "שלילי", "מכירה", "וטו", "הימנעות"]):
            return "score-red"
        return "score-neutral"

    if "TECH_SCORE_CLASS" not in data:
        data["TECH_SCORE_CLASS"] = _derive_score_class(data.get("TECH_STANCE", ""))
    if "SENT_SCORE_CLASS" not in data:
        data["SENT_SCORE_CLASS"] = _derive_score_class(data.get("SENT_STANCE", ""))
    if "RISK_SCORE_CLASS" not in data:
        data["RISK_SCORE_CLASS"] = _derive_score_class(data.get("RISK_STANCE", ""))

    # Default financial net calculation if not provided
    if "SWING_NET_PROFIT" not in data:
        data["SWING_NET_PROFIT"] = "$108.75 עד $183.75 (תשואה נטו: +1.09% עד +1.84%)"
    if "SWING_ALLOCATION" not in data:
        data["SWING_ALLOCATION"] = "$10,000 (הקצאה מלאה)"
    if "WHIPSAW_SHIELD_STATUS" not in data:
        data["WHIPSAW_SHIELD_STATUS"] = "פעילה (מעוגן מתחת לתמיכות עם מרווח רעש ATR)"

    # Auto-populate MACRO_ALERT_BANNER and SWING_ENTRY_MODE if not provided
    if "MACRO_ALERT_BANNER" not in data:
        try:
            scripts_dir = os.path.abspath(os.path.join(TEMPLATE_DIR, "..", "..", "scripts"))
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from macro_calendar import get_today_macro_risk
            macro_info = get_today_macro_risk()
            if macro_info.get("has_high_impact"):
                lvl = macro_info.get("warning_level", "HIGH").lower()
                events_str = ", ".join([f"<strong>{e['title']}</strong> ({e['time_israel']})" for e in macro_info.get("events", [])])
                data["MACRO_ALERT_BANNER"] = f"""
    <div class="macro-alert-banner {lvl}">
        <div class="macro-alert-icon">🚨</div>
        <div class="macro-alert-content">
            <h4>התראת מאקרו תנודתית להיום ({macro_info.get('warning_level')}): {events_str}</h4>
            <p>{macro_info.get('guidance')}</p>
        </div>
    </div>"""
                if "SWING_ENTRY_MODE" not in data:
                    data["SWING_ENTRY_MODE"] = "אישור היפוך בלבד (Confirmation 15m) • אסור לימיט פסיבי!"
            else:
                data["MACRO_ALERT_BANNER"] = ""
                if "SWING_ENTRY_MODE" not in data:
                    data["SWING_ENTRY_MODE"] = "לימיט פסיבי בתמיכה או אישור היפוך 15 דקות"
        except Exception as e:
            data["MACRO_ALERT_BANNER"] = ""
            if "SWING_ENTRY_MODE" not in data:
                data["SWING_ENTRY_MODE"] = "לימיט פסיבי או אישור היפוך"
    # Options variables normalization & aliases
    if "PUT_CALL_RATIO" not in data:
        if "OPTIONS_PC_RATIO" in data:
            data["PUT_CALL_RATIO"] = data["OPTIONS_PC_RATIO"]
        else:
            data["PUT_CALL_RATIO"] = "0.75"

    if "OPTIONS_PC_RATIO" not in data:
        data["OPTIONS_PC_RATIO"] = data["PUT_CALL_RATIO"]

    if "OPTIONS_VOLUME_DIST" in data:
        vol_str = str(data["OPTIONS_VOLUME_DIST"])
        if "Calls" in vol_str and "Puts" in vol_str:
            parts = vol_str.split("Calls")
            if "OPTIONS_CALL_VOL" not in data:
                data["OPTIONS_CALL_VOL"] = parts[0].strip()
            if "OPTIONS_PUT_VOL" not in data:
                data["OPTIONS_PUT_VOL"] = parts[1].replace("מול", "").replace("Puts", "").strip()

    if "OPTIONS_CALL_VOL" not in data:
        data["OPTIONS_CALL_VOL"] = "15,000"
    if "OPTIONS_PUT_VOL" not in data:
        data["OPTIONS_PUT_VOL"] = "10,000"

    try:
        pc_val = float(str(data.get("PUT_CALL_RATIO", "0.75")).replace(",", "").strip())
    except Exception:
        pc_val = 0.75

    # Auto-derive options badge class & text
    if "OPTIONS_BADGE_CLASS" not in data:
        if pc_val <= 0.70:
            data["OPTIONS_BADGE_CLASS"] = "green"
        elif pc_val >= 1.0:
            data["OPTIONS_BADGE_CLASS"] = "red"
        else:
            data["OPTIONS_BADGE_CLASS"] = "amber"

    if "OPTIONS_BADGE_TEXT" not in data:
        if pc_val <= 0.70:
            data["OPTIONS_BADGE_TEXT"] = "איסוף שורי (Bullish Flow)"
        elif pc_val >= 1.0:
            data["OPTIONS_BADGE_TEXT"] = "הגנות דוביות (Bearish / Hedging)"
        else:
            data["OPTIONS_BADGE_TEXT"] = "תזרים מאוזן (Neutral Flow)"

    if "OPTIONS_DOMINANCE" not in data:
        if pc_val <= 0.70:
            data["OPTIONS_DOMINANCE"] = "דומיננטיות שורית מובהקת (יתרון משמעותי לרוכשי Calls)"
        elif pc_val >= 1.0:
            data["OPTIONS_DOMINANCE"] = "דומיננטיות דובית / הגנתית (יתרון לרוכשי Puts)"
        else:
            data["OPTIONS_DOMINANCE"] = "שיווי משקל יחסי בין קולים לפוטים"

    if "OPTIONS_SUMMARY" not in data:
        if "SMART_MONEY_SUBTITLE" in data:
            data["OPTIONS_SUMMARY"] = data["SMART_MONEY_SUBTITLE"]
        else:
            data["OPTIONS_SUMMARY"] = f"יחס פוט/קול של {pc_val:.2f} מעיד על סנטימנט {'שורי וצפי לעליות' if pc_val <= 0.70 else 'זהיר עם הגנות על התיק'}."

    # Auto-derive Market Regime Badge (Trend vs Chop)
    if "MARKET_REGIME_BADGE" not in data:
        regime_text = str(data.get("MARKET_REGIME", ""))
        if "דשדוש" in regime_text or "Chop" in regime_text:
            data["MARKET_REGIME_BADGE"] = '<span class="badge-regime chop">↔️ דשדוש (Chop / Range)</span>'
        elif "מגמה" in regime_text or "Trend" in regime_text:
            data["MARKET_REGIME_BADGE"] = '<span class="badge-regime trend">📈 מגמה ברורה (Trend)</span>'
        else:
            data["MARKET_REGIME_BADGE"] = '<span class="badge-regime chop">↔️ סביבת דשדוש (Chop / Range)</span>'
    elif not str(data["MARKET_REGIME_BADGE"]).startswith("<span"):
        raw_reg = str(data["MARKET_REGIME_BADGE"])
        is_tr = "מגמה" in raw_reg or "Trend" in raw_reg
        cls = "trend" if is_tr else "chop"
        ico = "📈" if is_tr else "↔️"
        data["MARKET_REGIME_BADGE"] = f'<span class="badge-regime {cls}">{ico} {raw_reg}</span>'

    # Auto-derive Pricing Zone Badge (Discount / OTE vs Premium)
    if "PRICING_ZONE_BADGE" not in data:
        zone_text = str(data.get("PRICING_ZONE", ""))
        if "Discount" in zone_text or "OTE" in zone_text or "מבצע" in zone_text:
            data["PRICING_ZONE_BADGE"] = '<span class="badge-zone discount">🎯 אזור מבצע (Discount / OTE)</span>'
        elif "Premium" in zone_text or "יקר" in zone_text:
            data["PRICING_ZONE_BADGE"] = '<span class="badge-zone premium">⚠️ אזור יקר (Premium Zone)</span>'
        else:
            data["PRICING_ZONE_BADGE"] = '<span class="badge-zone discount">🎯 אזור מבצע (Discount / OTE)</span>'
    elif not str(data["PRICING_ZONE_BADGE"]).startswith("<span"):
        raw_zone = str(data["PRICING_ZONE_BADGE"])
        is_disc = "Discount" in raw_zone or "OTE" in raw_zone or "מבצע" in raw_zone
        cls = "discount" if is_disc else "premium"
        ico = "🎯" if is_disc else "⚠️"
        data["PRICING_ZONE_BADGE"] = f'<span class="badge-zone {cls}">{ico} {raw_zone}</span>'

    # Auto-derive Sector RRG Badge (Leading, Improving, Weakening, Lagging)
    if "SECTOR_RRG_BADGE" not in data:
        sec_text = str(data.get("SECTOR_RRG", data.get("SECTOR_ROTATION", "")))
        if "מוביל" in sec_text or "Leading" in sec_text:
            data["SECTOR_RRG_BADGE"] = '<span class="badge-rrg leading">🟢 מוביל (Leading)</span>'
        elif "משתפר" in sec_text or "Improving" in sec_text:
            data["SECTOR_RRG_BADGE"] = '<span class="badge-rrg improving">🚀 משתפר (Improving)</span>'
        elif "נחלש" in sec_text or "Weakening" in sec_text:
            data["SECTOR_RRG_BADGE"] = '<span class="badge-rrg weakening">🟡 נחלש (Weakening)</span>'
        elif "מפגר" in sec_text or "Lagging" in sec_text:
            data["SECTOR_RRG_BADGE"] = '<span class="badge-rrg lagging">🔴 מפגר (Lagging)</span>'
        else:
            data["SECTOR_RRG_BADGE"] = '<span class="badge-rrg improving">🚀 רוטציה משתפרת (Improving)</span>'
    elif not str(data["SECTOR_RRG_BADGE"]).startswith("<span"):
        raw_sec = str(data["SECTOR_RRG_BADGE"])
        if "Leading" in raw_sec or "מוביל" in raw_sec:
            cls = "leading"; ico = "🟢"
        elif "Improving" in raw_sec or "משתפר" in raw_sec:
            cls = "improving"; ico = "🚀"
        elif "Weakening" in raw_sec or "נחלש" in raw_sec:
            cls = "weakening"; ico = "🟡"
        else:
            cls = "lagging"; ico = "🔴"
        data["SECTOR_RRG_BADGE"] = f'<span class="badge-rrg {cls}">{ico} {raw_sec}</span>'

    # Auto-derive Tri-Layer Confluence Strip placeholders (Layer 1: Market, Layer 2: Sector, Layer 3: Stock)
    if "LAYER1_MARKET_NAME" not in data:
        data["LAYER1_MARKET_NAME"] = "מדד SPY (S&P 500)"
    if "LAYER1_MARKET_BADGE" not in data:
        data["LAYER1_MARKET_BADGE"] = data.get("MARKET_REGIME_BADGE", '<span class="badge-regime trend">📈 מגמה ברורה (Trend)</span>')
    if "LAYER1_MARKET_DESC" not in data:
        reg_str = str(data.get("MARKET_REGIME", ""))
        if "דשדוש" in reg_str or "Chop" in reg_str:
            data["LAYER1_MARKET_DESC"] = "השוק הכללי בסביבת דשדוש (ADX נמוך) - פריצות שווא נפוצות, חובה לקנות אך ורק בתמיכות מבניות עמוקות."
        else:
            data["LAYER1_MARKET_DESC"] = "השוק הכללי נסחר במבנה מגמתי בריא מעל ממוצעים מרכזיים, מעניק רוח גבית לפוזיציות סווינג."

    if "LAYER2_SECTOR_NAME" not in data:
        sec_sym = data.get("SECTOR_SYMBOL", data.get("SECTOR", "XLK"))
        sec_nm = data.get("SECTOR_NAME", "טכנולוגיה" if sec_sym == "XLK" else ("בריאות ופארמה" if sec_sym == "XLV" else "סקטור מוביל"))
        data["LAYER2_SECTOR_NAME"] = f"סקטור {sec_sym} ({sec_nm})"
    if "LAYER2_SECTOR_BADGE" not in data:
        data["LAYER2_SECTOR_BADGE"] = data.get("SECTOR_RRG_BADGE", '<span class="badge-rrg leading">🟢 מוביל (Leading)</span>')
    if "LAYER2_SECTOR_DESC" not in data:
        rrg_str = str(data.get("SECTOR_RRG_BADGE", ""))
        if "lagging" in rrg_str or "מפגר" in rrg_str:
            data["LAYER2_SECTOR_DESC"] = "הסקטור מפגר יחסית ל-SPY (תזרים הון שלילי). נדרשת זהירות מרבית, הקטנת חשיפה והמתנה לאישור היפוך ודאי."
        elif "improving" in rrg_str or "משתפר" in rrg_str:
            data["LAYER2_SECTOR_DESC"] = "הסקטור ברוטציה משתפרת (צובר מומנטום מול השוק). כסף חכם מתחיל להצטבר - הזדמנות לכניסה מוקדמת."
        elif "leading" in rrg_str or "מוביל" in rrg_str:
            data["LAYER2_SECTOR_DESC"] = "הסקטור מוביל את השוק בעוצמה יחסית ובמומנטום. רוח גבית מוסדית חזקה התומכת בהמשך עליות."
        else:
            data["LAYER2_SECTOR_DESC"] = "הסקטור נחלש במומנטום היחסי מול השוק. יעד הרווח מוגבל להתנגדות קרובה."

    if "LAYER3_STOCK_NAME" not in data:
        data["LAYER3_STOCK_NAME"] = f"מניית {ticker}"
    if "LAYER3_STOCK_BADGE" not in data:
        data["LAYER3_STOCK_BADGE"] = data.get("PRICING_ZONE_BADGE", '<span class="badge-zone discount">🎯 אזור מבצע (Discount / OTE)</span>')

    # Auto-derive Relative Strength / Alpha Badge
    if "RELATIVE_STRENGTH_BADGE" not in data and "LAYER3_ALPHA_BADGE" in data:
        data["RELATIVE_STRENGTH_BADGE"] = data["LAYER3_ALPHA_BADGE"]

    if "RELATIVE_STRENGTH_BADGE" not in data:
        alpha_text = str(data.get("RELATIVE_STRENGTH", data.get("STOCK_ALPHA", "")))
        if "מובילת" in alpha_text or "Leader" in alpha_text:
            data["RELATIVE_STRENGTH_BADGE"] = '<span class="badge-alpha leader">🌟 מובילת סקטור (Alpha Leader)</span>'
        elif "מנצחת" in alpha_text or "Outperformer" in alpha_text:
            data["RELATIVE_STRENGTH_BADGE"] = '<span class="badge-alpha outperformer">🟢 מנצחת שוק (Outperformer)</span>'
        elif "ספיגת" in alpha_text or "Divergence" in alpha_text:
            data["RELATIVE_STRENGTH_BADGE"] = '<span class="badge-alpha divergence">⚡ ספיגת היצע (Divergence)</span>'
        elif "מפגרת" in alpha_text or "Laggard" in alpha_text:
            data["RELATIVE_STRENGTH_BADGE"] = '<span class="badge-alpha laggard">🔴 מפגרת יחסית (Laggard)</span>'
        else:
            data["RELATIVE_STRENGTH_BADGE"] = '<span class="badge-alpha neutral">🟡 תואמת מדד (Neutral)</span>'
    elif not str(data["RELATIVE_STRENGTH_BADGE"]).startswith("<span"):
        raw_alpha = str(data["RELATIVE_STRENGTH_BADGE"])
        if "מובילת" in raw_alpha or "Dual" in raw_alpha:
            cls = "leader"; ico = "🌟"
        elif "מנצחת" in raw_alpha or "Outperformer" in raw_alpha:
            cls = "outperformer"; ico = "🟢"
        elif "מפגרת" in raw_alpha or "Laggard" in raw_alpha:
            cls = "laggard"; ico = "🔴"
        else:
            cls = "neutral"; ico = "🟡"
        data["RELATIVE_STRENGTH_BADGE"] = f'<span class="badge-alpha {cls}">{ico} {raw_alpha}</span>'

    # Auto-derive LAYER3_ALPHA_BADGE
    if "LAYER3_ALPHA_BADGE" not in data:
        data["LAYER3_ALPHA_BADGE"] = data.get("RELATIVE_STRENGTH_BADGE", '<span class="badge-alpha outperformer">🟢 מנצחת שוק (Outperformer)</span>')

    if "LAYER3_STOCK_DESC" not in data:
        zone_str = str(data.get("PRICING_ZONE_BADGE", ""))
        alpha_str = str(data.get("RELATIVE_STRENGTH_BADGE", ""))
        if "premium" in zone_str or "יקר" in zone_str:
            data["LAYER3_STOCK_DESC"] = "המניה נסחרת בקרבת שיא הטווח (אזור יקר). יחס סיכוי/סיכון נחות וסכנת FOMO מוגברת."
        else:
            alpha_desc = "עם ביצועי יתר מול המדד." if ("outperformer" in alpha_str or "leader" in alpha_str) else "נדרשת זהירות מול חולשה יחסית."
            data["LAYER3_STOCK_DESC"] = f"המניה נסוגה לעומק 50%-78.6% מגל העליות (Discount/OTE) מעל תמיכה מבנית, {alpha_desc}"

    if "CONFLUENCE_SUMMARY" not in data:
        data["CONFLUENCE_SUMMARY"] = data.get("CONFLUENCE_STATUS", "התלכדות אינדיקטורים מלאה בתמיכה מבנית עם יחס סיכוי/סיכון מוגדר היטב.")

    # Auto-derive 4 Filter Micro-Notes for the Institutional Matrix
    if "MARKET_REGIME_MICRO" not in data:
        regime_text = str(data.get("MARKET_REGIME_BADGE", data.get("MARKET_REGIME", "")))
        if "trend" in regime_text.lower() or "מגמה" in regime_text:
            data["MARKET_REGIME_MICRO"] = "✅ מגמה עולה בריאה מעל ממוצע 200 — רוח גבית תומכת"
        else:
            data["MARKET_REGIME_MICRO"] = "⚠️ שוק מדשדש (Chop) — פריצות עלולות להיכשל"

    if "SECTOR_RRG_MICRO" not in data:
        rrg_text = str(data.get("SECTOR_RRG_BADGE", data.get("SECTOR_RRG", "")))
        if "leading" in rrg_text.lower() or "מוביל" in rrg_text:
            data["SECTOR_RRG_MICRO"] = "🟢 מנהיג שוק מובהק — תזרים הון מוסדי חזק ביותר"
        elif "improving" in rrg_text.lower() or "משתפר" in rrg_text:
            data["SECTOR_RRG_MICRO"] = "🚀 שלב צבירה מוקדם של כסף חכם — תזמון כניסה אידיאלי"
        elif "weakening" in rrg_text.lower() or "נחלש" in rrg_text:
            data["SECTOR_RRG_MICRO"] = "🟡 אובדן תנופה יחסית — סכנת מימושים ודשדוש"
        else:
            data["SECTOR_RRG_MICRO"] = "🔴 תזרים שלילי (Lagging) — אזהרה לכניסה באישור בלבד"

    if "PRICING_ZONE_MICRO" not in data:
        zone_text = str(data.get("PRICING_ZONE_BADGE", data.get("PRICING_ZONE", "")))
        if "discount" in zone_text.lower() or "מבצע" in zone_text or "ote" in zone_text.lower():
            data["PRICING_ZONE_MICRO"] = "🎯 נסיגה עמוקה (50%-78%) — יחס סיכון/סיכוי אופטימלי"
        else:
            data["PRICING_ZONE_MICRO"] = "⚠️ אזור יקר (Premium) סמוך לשיא — סכנת FOMO מוגברת"

    if "RELATIVE_STRENGTH_MICRO" not in data:
        alpha_text = str(data.get("RELATIVE_STRENGTH_BADGE", data.get("RELATIVE_STRENGTH", "")))
        if "leader" in alpha_text.lower() or "מוביל" in alpha_text:
            data["RELATIVE_STRENGTH_MICRO"] = "🌟 מובילה מובהקת המנצחת את המדד ואת הסקטור"
        elif "outperformer" in alpha_text.lower() or "מנצחת" in alpha_text:
            data["RELATIVE_STRENGTH_MICRO"] = "🟢 ביצועי יתר עקביים מול מדד S&P 500 (Alpha+)"
        elif "divergence" in alpha_text.lower() or "ספיגת" in alpha_text:
            data["RELATIVE_STRENGTH_MICRO"] = "⚡ ספיגת היצע אגרסיבית — עולה כשהמדד מתקן"
        elif "laggard" in alpha_text.lower() or "מפגר" in alpha_text:
            data["RELATIVE_STRENGTH_MICRO"] = "🔴 חולשה יחסית מול השוק — גוררת רגליים"
        else:
            data["RELATIVE_STRENGTH_MICRO"] = "🟡 תואמת לקצב המדד — עוצמה ממוצעת"

    # Auto-derive Institutional Verdict & Traffic Light
    reg_pass = ("trend" in str(data.get("MARKET_REGIME_BADGE", "")).lower() or "מגמה" in str(data.get("MARKET_REGIME_BADGE", "")))
    sec_pass = ("leading" in str(data.get("SECTOR_RRG_BADGE", "")).lower() or "מוביל" in str(data.get("SECTOR_RRG_BADGE", "")) or
                "improving" in str(data.get("SECTOR_RRG_BADGE", "")).lower() or "משתפר" in str(data.get("SECTOR_RRG_BADGE", "")))
    zone_pass = ("discount" in str(data.get("PRICING_ZONE_BADGE", "")).lower() or "מבצע" in str(data.get("PRICING_ZONE_BADGE", "")) or "ote" in str(data.get("PRICING_ZONE_BADGE", "")).lower())
    alpha_pass = ("leader" in str(data.get("RELATIVE_STRENGTH_BADGE", "")).lower() or "מוביל" in str(data.get("RELATIVE_STRENGTH_BADGE", "")) or
                  "outperformer" in str(data.get("RELATIVE_STRENGTH_BADGE", "")).lower() or "מנצחת" in str(data.get("RELATIVE_STRENGTH_BADGE", "")) or
                  "divergence" in str(data.get("RELATIVE_STRENGTH_BADGE", "")).lower())

    filter_score = sum([1 for p in [reg_pass, sec_pass, zone_pass, alpha_pass] if p])

    if "VERDICT_BOX_CLASS" not in data:
        if filter_score == 4:
            data["VERDICT_BOX_CLASS"] = "verdict-pass"
            data["VERDICT_ICON"] = "🟢"
            data["VERDICT_SCORE_CLASS"] = "score-green"
            data["VERDICT_SCORE_TEXT"] = "ציון מסננים: 4/4 (100% אישור מוסדי מלא)"
            if "VERDICT_ACTION_TEXT" not in data:
                data["VERDICT_ACTION_TEXT"] = "אור ירוק מלא: כל ארבעת המסננים המוסדיים מסונכרנים! אישור כניסה מלא בכל גודל הפוזיציה המתוכנן ($10,000) לפי תוכנית הסווינג."
        elif filter_score == 3:
            data["VERDICT_BOX_CLASS"] = "verdict-warn"
            data["VERDICT_ICON"] = "🟡"
            data["VERDICT_SCORE_CLASS"] = "score-amber"
            data["VERDICT_SCORE_TEXT"] = "ציון מסננים: 3/4 (אישור מותנה • 75%)"
            if "VERDICT_ACTION_TEXT" not in data:
                reason = "הסקטור מפגר (Lagging 🔴)" if not sec_pass else ("המניה תואמת מדד/מפגרת" if not alpha_pass else "השוק בדשדוש")
                data["VERDICT_ACTION_TEXT"] = f"אור כתום (חצי גז): המחיר באזור מבצע והשוק תומך, אך {reason}. הנחיית ביצוע: חובה להמתין לאישור נר היפוך (15 דקות), ללא לימיט פסיבי, להציב סטופ טקטי הדוק, ולקחת יעד רווח ראשון בהתנגדות הקרובה."
        else:
            data["VERDICT_BOX_CLASS"] = "verdict-fail"
            data["VERDICT_ICON"] = "🔴"
            data["VERDICT_SCORE_CLASS"] = "score-red"
            data["VERDICT_SCORE_TEXT"] = f"ציון מסננים: {filter_score}/4 (וטו מוסדי • תנאים נחותים)"
            if "VERDICT_ACTION_TEXT" not in data:
                data["VERDICT_ACTION_TEXT"] = "אור אדום (הימנעות): יחס הסיכוי-סיכון נחות או שישנה חולשה מוסדית מובהקת. מומלץ להימנע מכניסה עד לשיפור התנאים או לבחור מובילת שוק חלופית."


    # 0. Macro Economic Calendar & Event Freeze Filter
    if "MACRO_ALERT_BANNER" not in data or not data["MACRO_ALERT_BANNER"]:
        try:
            scripts_dir = os.path.abspath(os.path.join(TEMPLATE_DIR, "..", "..", "scripts"))
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from macro_calendar import get_today_macro_risk
            date_raw = data.get("DATE_RAW", "")
            target_d = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}" if len(date_raw) == 8 else None
            macro_risk = get_today_macro_risk(target_d)
            if macro_risk.get("has_high_impact", False):
                w_lvl = macro_risk.get("warning_level", "HIGH")
                events_list = macro_risk.get("events", [])
                ev_desc = ", ".join([f"{e['title']} ({e['time_israel']} שעון ישראל)" for e in events_list])
                guidance = macro_risk.get("guidance", "")
                data["MACRO_ALERT_BANNER"] = f"""
    <div class="macro-alert-banner {w_lvl.lower()}">
        <div class="macro-banner-icon">🚨</div>
        <div class="macro-banner-content">
            <div class="macro-banner-title">התראת מאקרו מוסדית ({w_lvl}): {ev_desc}</div>
            <div class="macro-banner-desc">{guidance}</div>
        </div>
    </div>"""
            else:
                data["MACRO_ALERT_BANNER"] = ""
        except Exception as e:
            print(f"[-] Macro calendar fetch skipped: {e}")
            data["MACRO_ALERT_BANNER"] = ""

    # Dual-State Swing Card Generation (Clean 3 Hero Badges + $10K Financial Breakdown OR Minimal Avoid State)
    try:
        import re
        is_avoid = ("הימנעות" in str(data.get("SWING_DIRECTION", "")) or 
                    "HOLD" in str(data.get("CONSENSUS_TEXT", "")) or 
                    "AVOID" in str(data.get("CONSENSUS_TEXT", "")) or 
                    "שטח הפקר" in str(data.get("NET_SCORE", "")) or
                    "וטו" in str(data.get("RISK_STANCE", "")))

        is_sector_lagging = ("lagging" in str(data.get("SECTOR_RRG", "")).lower() or 
                             "מפגר" in str(data.get("SECTOR_RRG", "")) or
                             "lagging" in str(data.get("SECTOR_RRG_BADGE", "")).lower())

        # Extract numeric prices for active setup or avoid setup
        entry_str = str(data.get("SWING_ENTRY", ""))
        stop_str = str(data.get("SWING_STOP", ""))
        target_str = str(data.get("SWING_TARGET", ""))
        entry_mode_str = str(data.get("SWING_ENTRY_MODE", "אישור היפוך"))
        
        def _parse_dollars(text):
            return [float(p.replace(",", "")) for p in re.findall(r"\$([\d,]+(?:\.\d+)?)", str(text))]

        entry_matches = _parse_dollars(entry_str)
        if len(entry_matches) >= 2:
            if is_sector_lagging:
                active_entry = entry_matches[1]
                entry_badge_sub = "אישור פריצה (HOD)"
            elif "אישור" in entry_mode_str or "Confirmation" in entry_mode_str:
                active_entry = entry_matches[1]
                entry_badge_sub = "אישור 15 דק'"
            else:
                active_entry = entry_matches[0]
                entry_badge_sub = "פקודת לימיט"
        elif len(entry_matches) == 1:
            active_entry = entry_matches[0]
            entry_badge_sub = "אישור פריצה (HOD)" if is_sector_lagging else "מחיר כניסה"
        else:
            raw_p = [float(p.replace(",", "")) for p in re.findall(r"[\d,]+(?:\.\d+)?", str(data.get("PRICE", "100.0")))]
            active_entry = raw_p[0] if raw_p else 100.0
            entry_badge_sub = "כניסה"

        stop_matches = _parse_dollars(stop_str)
        active_stop = stop_matches[0] if stop_matches else (active_entry * 0.98)

        target_matches = _parse_dollars(target_str)
        active_target = target_matches[-1] if target_matches else (active_entry * 1.03)

        # Scale-Out Two-Tier Target resolution:
        # Target 1 (TP1): First intermediate resistance for 50% scale-out & move stop to Break-Even
        # Target 2 (TP2): Full swing target
        if len(target_matches) >= 2:
            target1_price = target_matches[0]
            target2_price = target_matches[-1]
        elif "SWING_TARGET_1" in data:
            target1_matches = _parse_dollars(data["SWING_TARGET_1"])
            target1_price = target1_matches[0] if target1_matches else round(active_entry + ((active_target - active_entry) * 0.5), 2)
            target2_price = active_target
        else:
            # Check if nearest resistance in RESISTANCE_LEVEL is between entry and active_target
            res_matches = _parse_dollars(data.get("RESISTANCE_LEVEL", ""))
            valid_res = [r for r in res_matches if active_entry < r < active_target]
            if valid_res:
                target1_price = valid_res[0]
            else:
                target1_price = round(active_entry + ((active_target - active_entry) * 0.45), 2)
            target2_price = active_target

        risk_per_share = max(0.01, active_entry - active_stop)
        reward_per_share = max(0.01, active_target - active_entry)
        risk_pct = round((risk_per_share / active_entry) * 100, 2)
        target_pct = round((reward_per_share / active_entry) * 100, 2)
        rr_val = round(reward_per_share / risk_per_share, 2)

        target1_gain = max(0.01, target1_price - active_entry)
        target1_pct = round((target1_gain / active_entry) * 100, 2)
        target1_rr = round(target1_gain / risk_per_share, 2)

        # Hybrid Stop Loss resolution:
        # Layer 1: Tactical Stop (TV Alert) = active_stop
        # Layer 2: Hard Disaster Stop (IBKR) = disaster_stop
        disaster_str = str(data.get("SWING_DISASTER_STOP", ""))
        disaster_matches = _parse_dollars(disaster_str)
        if disaster_matches:
            disaster_stop = disaster_matches[0]
        elif len(stop_matches) >= 2 and stop_matches[1] < active_stop:
            disaster_stop = stop_matches[1]
        else:
            # Check if EMA 200 is available in support or report data
            ema200_match = re.findall(r"(?:EMA|ממוצע)\s*200[^\$]*\$([\d,]+(?:\.\d+)?)", str(data))
            if ema200_match:
                ema200_val = float(ema200_match[0].replace(",", ""))
                if ema200_val < active_stop:
                    disaster_stop = round(ema200_val * 0.99, 2)
                else:
                    disaster_stop = round(active_stop * 0.965, 2)
            else:
                derived_disaster = active_entry - (risk_per_share * 1.8)
                min_safe_dist = active_stop * 0.965
                disaster_stop = round(min(derived_disaster, min_safe_dist), 2)

        disaster_risk = max(0.01, active_entry - disaster_stop)
        disaster_pct = round((disaster_risk / active_entry) * 100, 2)

        avoid_reason = data.get("SWING_AVOID_REASON")
        if not avoid_reason:
            avoid_reason = data.get("RISK_SUMMARY", "שטח הפקר גיאומטרי ויחס סיכוי-סיכון נחות מול התקרה הקרובה — הטרייד נפסל לפי חוקי הסיסטם.")

        # Automated Swing Simulation Chart Generation
        chart_filename = f"{date_str}_{ticker}_chart.png"
        chart_path = os.path.join(REPORTS_DIR, chart_filename)
        chart_html = ""
        try:
            scripts_dir = os.path.abspath(os.path.join(TEMPLATE_DIR, "..", "..", "scripts"))
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from chart_simulator import generate_swing_simulation_chart
            
            gen_res = generate_swing_simulation_chart(
                ticker=ticker,
                entry_price=active_entry,
                stop_price=active_stop,
                target_price=active_target,
                output_path=chart_path,
                is_avoid=is_avoid,
                avoid_reason=avoid_reason if is_avoid else "",
                disaster_stop_price=disaster_stop if not is_avoid else None,
                target1_price=target1_price if not is_avoid else None
            )
            if gen_res and os.path.exists(chart_path):
                badge_type = "⚠️ הדמיית שטח הפקר (Avoid)" if is_avoid else f"🎯 הדמיית טרייד (R:R 1:{rr_val:.2f})"
                badge_color = "var(--accent-amber)" if is_avoid else "var(--accent-green)"
                caption_text = ("המלבן המפוספס ממחיש את המלכודת: מרווח צר אל מול ממוצע 20 החוסם את הדרך (תוחלת R:R שלילית)."
                                if is_avoid else 
                                f"הדמיית פריסת הטרייד לטווח של עד שבועיים (10 נרות): יעד 1 למימוש 50% ב-${target1_price:.2f} (+{target1_pct:.1f}%), יעד 2 מלא ב-${active_target:.2f} (+{target_pct:.1f}%), קופסת סיכון טקטית (-{risk_pct:.1f}% בהתראת TV), וסטופ אסון קשיח ב-IBKR ב-${disaster_stop:.2f} (-{disaster_pct:.1f}%).")
                chart_html = f"""
                <div class="swing-chart-container">
                    <div class="swing-chart-header">
                        <div class="chart-header-title">
                            <span>📈 סימולציה ויזואלית של תוכנית הסווינג</span>
                            <span class="chart-status-pill" style="color: {badge_color};">{badge_type}</span>
                        </div>
                        <button type="button" class="chart-zoom-btn" onclick="openChartModal('{chart_filename}', '📊 הדמיית גרף מסחר ({ticker})')">
                            <span>🔍</span>
                            <span>הגדל גרף</span>
                        </button>
                    </div>
                    <div class="chart-img-wrapper" onclick="openChartModal('{chart_filename}', '📊 הדמיית גרף מסחר ({ticker})')" title="לחץ להגדלה במסך מלא">
                        <img src="{chart_filename}" alt="סימולציית גרף {ticker}" class="swing-chart-img" />
                        <div class="chart-hover-overlay">
                            <span>🔍 לחץ לפתיחה במסך מלא</span>
                        </div>
                    </div>
                    <div class="swing-chart-caption">{caption_text}</div>
                </div>"""
        except Exception as chart_err:
            print(f"[-] Chart simulation skipped: {chart_err}")
            chart_html = ""

        if is_avoid:
            if "SWING_BADGE_TEXT" not in data:
                data["SWING_BADGE_TEXT"] = "הימנעות • אין טרייד היום"
                
            support_trig = data.get("SWING_SUPPORT_TRIGGER", "המתנה לנסיגה ובדיקת תמיכה באזור $61.85 (מניב R:R מעולה של 1:4.0)")
            breakout_trig = data.get("SWING_BREAKOUT_TRIGGER", "סגירה יומית מוכחת מעל ממוצע 20 ($63.55+) להפיכת התקרה לרצפה (יעד R1 ב-$64.80)")
            
            data["SWING_CARD_CONTENT"] = f"""
            <div class="swing-avoid-container">
                <div class="swing-avoid-header">
                    <span class="avoid-icon">🛑</span>
                    <div>
                        <div class="avoid-title">סטטוס סווינג להיום: אין כניסה (יושבים על הגדר)</div>
                        <div class="avoid-subtitle">הטרייד אינו מאושר במחיר הנוכחי עקב תוחלת שלילית וסיכון אסימטרי</div>
                    </div>
                </div>
                <div class="avoid-reasons">
                    <div class="avoid-reason-item">
                        <strong>❌ סיבת הפסילה:</strong> {avoid_reason}
                    </div>
                    <div class="avoid-reason-item">
                        <strong>🎯 תנאי סף חלופיים לכניסה עתידית (להמתין לאחד מהשניים):</strong>
                        <ul style="margin: 8px 0 0 0; padding-right: 20px; color: #cbd5e1; font-size: 13.5px; line-height: 1.7;">
                            <li><strong>איסוף בתמיכה:</strong> {support_trig}</li>
                            <li><strong>פריצת מומנטום:</strong> {breakout_trig}</li>
                        </ul>
                    </div>
                </div>
                {chart_html}
            </div>"""
        else:
            if "SWING_BADGE_TEXT" not in data:
                data["SWING_BADGE_TEXT"] = "סווינג פעיל • עד שבועיים"
                
            capital = 10000.0
            shares_10k = int(capital / active_entry)
            shares_half = shares_10k // 2
            shares_rem = shares_10k - shares_half
            invested_10k = round(shares_10k * active_entry, 2)
            dollar_loss = round(risk_per_share * shares_10k, 2)
            ibkr_fee = 5.00

            # Scenario A: Scale-Out 50/50 (Institutional Protocol)
            gross_gain_tp1 = round(shares_half * target1_gain, 2)
            gross_gain_tp2 = round(shares_rem * reward_per_share, 2)
            scaleout_gross = round(gross_gain_tp1 + gross_gain_tp2, 2)
            scaleout_taxable = max(0.0, scaleout_gross - ibkr_fee)
            scaleout_tax = round(scaleout_taxable * 0.25, 2)
            scaleout_net = round(scaleout_taxable - scaleout_tax, 2)
            scaleout_roi = round((scaleout_net / invested_10k) * 100, 2)

            # Scenario B: Full Target 100% (Maximum Momentum)
            full_gross = round(reward_per_share * shares_10k, 2)
            full_taxable = max(0.0, full_gross - ibkr_fee)
            full_tax = round(full_taxable * 0.25, 2)
            full_net = round(full_taxable - full_tax, 2)
            full_roi = round((full_net / invested_10k) * 100, 2)

            extra_protocol_notes = []
            if is_sector_lagging:
                extra_protocol_notes.append("⚠️ <strong>איסור פקודת לימיט מראש (סקטור Lagging 🔴):</strong> חל איסור מוחלט על פקודות Limit עיוורות לפני/בפתיחה! כניסה אך ורק בפריצת שיא נר שעה ראשונה (HOD Breakout) לאחר שהקונים מוכיחים ספיגת חולשת הסקטור.")
            
            has_gamma_pinning_risk = any(k in str(data.get("OPTIONS_SUMMARY", "")) for k in ["פקיע", "0-DTE", "השבוע", "היום"]) and "call" in str(data.get("OPTIONS_DOMINANCE", "")).lower()
            if has_gamma_pinning_risk:
                extra_protocol_notes.append("⚡ <strong>אזהרת גאמא של עושי שוק (Gamma Pinning & Max Pain):</strong> פקיעת אופציות השבוע עלולה להפעיל לחץ מכירות אגרסיבי של עושי שוק (Delta Hedging) בפתיחה כדי למחוק קולים — חובה להמתין לספיגת הלחץ.")
            
            extra_protocol_html = ("<br>" + "<br>".join(extra_protocol_notes)) if extra_protocol_notes else ""

            data["SWING_CARD_CONTENT"] = f"""
            <!-- 3 Hero Badges (With Hybrid Stop & Two-Tier Scale-Out Target) -->
            <div class="swing-hero-grid">
                <div class="swing-hero-box entry">
                    <div class="hero-label">מחיר כניסה מומלץ</div>
                    <div class="hero-val">${active_entry:.2f}</div>
                    <div class="hero-sub">{entry_badge_sub}</div>
                </div>
                <div class="swing-hero-box stop hybrid">
                    <div class="hero-label">
                        <span>🛡️ סטופ היברידי (דו-שכבתי)</span>
                        <span class="tooltip-container">
                            <span class="tooltip-trigger">?</span>
                            <span class="tooltip-text">מודל הגנה היברידי: שכבה 1 (התראת TV) מונעת ניעור רגעי בצלליות נרות ומחייבת סגירה ידנית רק בסגירת נר; שכבה 2 (פקודת IBKR קשיחה) פועלת כפוליסת ביטוח מפני גאפים ואסונות מאקרו.</span>
                        </span>
                    </div>
                    <div class="hybrid-levels-container">
                        <div class="hybrid-level-item tactical">
                            <span class="hybrid-pill tv">התראת TV</span>
                            <span class="hybrid-price">${active_stop:.2f}</span>
                            <span class="hybrid-pct">(-{risk_pct:.2f}%)</span>
                        </div>
                        <div class="hybrid-level-item disaster">
                            <span class="hybrid-pill ibkr">אסון ב-IBKR</span>
                            <span class="hybrid-price">${disaster_stop:.2f}</span>
                            <span class="hybrid-pct">(-{disaster_pct:.2f}%)</span>
                        </div>
                    </div>
                    <div class="hero-sub">שכבה 1: סגירת נר • שכבה 2: ביטוח גאפ</div>
                </div>
                <div class="swing-hero-box target scaleout">
                    <div class="hero-label">
                        <span>🎯 יעד רווח (דו-שלבי Scale-Out)</span>
                        <span class="tooltip-container">
                            <span class="tooltip-trigger">?</span>
                            <span class="tooltip-text">מימוש מדורג מוסדי (Scale-Out): הגעה ליעד 1 (התנגדות קרובה) מאפשרת נעילת 50% מהרווח בכיס והזזת הסטופ למחיר הכניסה (Break-Even) להמשך טרייד באפס סיכון; יעד 2 פועל כמימוש סופי למלוא המהלך.</span>
                        </span>
                    </div>
                    <div class="hybrid-levels-container">
                        <div class="hybrid-level-item tp1">
                            <span class="hybrid-pill tp1">יעד 1 (50%)</span>
                            <span class="hybrid-price">${target1_price:.2f}</span>
                            <span class="hybrid-pct profit">(+{target1_pct:.2f}%)</span>
                        </div>
                        <div class="hybrid-level-item tp2">
                            <span class="hybrid-pill tp2">יעד 2 (מלא)</span>
                            <span class="hybrid-price">${active_target:.2f}</span>
                            <span class="hybrid-pct profit">(+{target_pct:.2f}%)</span>
                        </div>
                    </div>
                    <div class="hero-sub">יעד 1: נעילת חצי רווח + BE • יעד 2: R:R 1:{rr_val:.1f}</div>
                </div>
            </div>

            <!-- Visual Swing Simulation Chart -->
            {chart_html}

            <!-- Clean Financial Box with Dual Scenarios -->
            <div class="financial-box clean">
                <div class="financial-title-wrapper">
                    <div class="financial-title" style="margin-bottom: 0;">
                        <span>💰 תחשיב פיננסי מדויק לחשבון (הקצאת $10,000)</span>
                        <span class="tooltip-container">
                            <span class="tooltip-trigger">?</span>
                            <span class="tooltip-text">חישוב מדויק של הכסף שיוצא ונכנס: כמה מניות קונים ב-$10,000, מה ההפסד המרבי בדולרים אם הסטופ הטקטי פוגע, ומה הרווח הנקי המדויק שנכנס לחשבון הבנק שלך לאחר עמלת IBKR $5 ומס רווחי הון 25%.</span>
                        </span>
                    </div>
                    <span class="fin-badge-allocation">{shares_10k} מניות • ${invested_10k:,.2f} הון מושקע</span>
                </div>

                <!-- Top Metric Row -->
                <div class="fin-top-row">
                    <div class="fin-metric-card">
                        <span class="fin-metric-label">הקצאת הון מלאה וכמות מניות:</span>
                        <span class="fin-metric-val">{shares_10k} מניות (${invested_10k:,.2f})</span>
                    </div>
                    <div class="fin-metric-card risk">
                        <span class="fin-metric-label">סיכון מרבי (סטופ טקטי ${active_stop:.2f}):</span>
                        <span class="fin-metric-val risk">-${dollar_loss:,.2f} (-{risk_pct:.2f}% מההון)</span>
                    </div>
                </div>

                <!-- Two Scenarios Side-by-Side -->
                <div class="fin-scenarios-grid">
                    <!-- Scenario A: Recommended Scale-Out -->
                    <div class="fin-scenario-card recommended">
                        <div class="scenario-header">
                            <span class="scenario-tag tag-scaleout">תרחיש א' — מומלץ (Scale-Out 50/50)</span>
                            <span class="scenario-status-pill">נעילת רווח + אפס סיכון</span>
                        </div>
                        <div class="scenario-steps">
                            <div class="scenario-step-item">
                                <span>מימוש 50% ביעד 1 (${target1_price:.2f}):</span>
                                <strong style="color: #34d399;">{shares_half} מניות ➔ +${gross_gain_tp1:,.2f} ברוטו</strong>
                            </div>
                            <div class="scenario-step-item">
                                <span>קידום סטופ ליתרה ({shares_rem} מניות):</span>
                                <strong style="color: #38bdf8;">מחיר כניסה (BE = Risk Free!)</strong>
                            </div>
                            <div class="scenario-step-item">
                                <span>מימוש יתרה ביעד 2 (${active_target:.2f}):</span>
                                <strong style="color: #34d399;">{shares_rem} מניות ➔ +${gross_gain_tp2:,.2f} ברוטו</strong>
                            </div>
                        </div>
                        <div class="scenario-net-box">
                            <span class="net-title">רווח נקי בכיס (אחרי עמלה $5 ומס 25%):</span>
                            <span class="net-amount">+${scaleout_net:,.2f} <small>(+{scaleout_roi:.2f}% על ההון)</small></span>
                        </div>
                    </div>

                    <!-- Scenario B: Full Target Run -->
                    <div class="fin-scenario-card full">
                        <div class="scenario-header">
                            <span class="scenario-tag tag-full">תרחיש ב' — יעד מלא (100% ביעד 2)</span>
                            <span class="scenario-status-pill">מיצוי מהלך מקסימלי</span>
                        </div>
                        <div class="scenario-steps">
                            <div class="scenario-step-item">
                                <span>מימוש 100% מהעסקה ביעד 2 (${active_target:.2f}):</span>
                                <strong style="color: #38bdf8;">{shares_10k} מניות ➔ +${full_gross:,.2f} ברוטו</strong>
                            </div>
                            <div class="scenario-step-item">
                                <span>יחס סיכוי-סיכון לכל המהלך (R:R):</span>
                                <strong style="color: #10b981;">1:{rr_val:.2f} אסימטרי</strong>
                            </div>
                            <div class="scenario-step-item">
                                <span>עלות עמלת ביצוע כוללת (IBKR):</span>
                                <strong style="color: #94a3b8;">$5.00 פלט</strong>
                            </div>
                        </div>
                        <div class="scenario-net-box full">
                            <span class="net-title">רווח נקי בכיס (אחרי עמלה $5 ומס 25%):</span>
                            <span class="net-amount full">+${full_net:,.2f} <small>(+{full_roi:.2f}% על ההון)</small></span>
                        </div>
                    </div>
                </div>

                <!-- Institutional Protocol Note -->
                <div class="financial-hybrid-note">
                    <span>🛡️ <strong>פרוטוקול ביצוע מוסדי:</strong> כניסה ב-${active_entry:.2f}. בהגעה ליעד 1 (${target1_price:.2f}) מממשים 50% מהפוזיציה ({shares_half} מניות) ומקדמים מיד סטופ למחיר הכניסה (Break-Even = Risk Free!). ביתרת {shares_rem} המניות מאפשרים לרווח לרוץ ליעד 2 (${active_target:.2f}). במקביל מוגדרת פקודת אסון קשיחה ב-IBKR ב-${disaster_stop:.2f}.{extra_protocol_html}</span>
                </div>
            </div>"""
    except Exception as e:
        import traceback
        traceback.print_exc()

    # Replace all placeholders
    for key, val in data.items():
        html = html.replace(f"{{{{{key}}}}}", str(val))
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    local_ip = get_local_ip()
    mobile_url = f"http://{local_ip}:8080/{filename}"
    print(f"[+] Report generated successfully: {output_path}")
    print(f"[+] Mobile URL (Dynamic LAN IP): {mobile_url}")
    return {"file_path": output_path, "mobile_url": mobile_url, "local_ip": local_ip}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
        render_debate_report(data)
    else:
        print("Usage: python render_report.py <data.json>")
