"""
Macro Economic Calendar Filter (מנוע לוח שנה כלכלי ומסנן אירועי מאקרו)
Fetches high-impact US economic events (FOMC, CPI, NFP, Powell speeches) 
to warn swing traders against entering passive limit orders during high-volatility events.
"""

import os
import sys
import json
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calendar_cache.json")
CACHE_TTL_SECONDS = 7200  # 2 hours cache

# Key high-impact keywords in event titles (Only real market-shaking events)
CRITICAL_KEYWORDS = [
    "Federal Funds Rate", "FOMC Statement", "FOMC Economic Projections",
    "FOMC Press Conference", "Fed Chair Powell", "Powell Speaks",
    "CPI", "Consumer Price Index", "Non-Farm Employment", "Non-Farm Payrolls", "NFP",
    "Core PCE Price Index", "Jackson Hole"
]


def fetch_weekly_events() -> List[Dict]:
    """Fetches this week's economic events with local caching and 429 rate-limit fallback."""
    # 1. Check local cache first
    if os.path.exists(CACHE_FILE):
        try:
            mtime = os.path.getmtime(CACHE_FILE)
            if (time.time() - mtime) < CACHE_TTL_SECONDS:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    if cached_data:
                        return cached_data
        except Exception:
            pass

    # 2. Fetch fresh data with realistic browser headers
    req = urllib.request.Request(
        CALENDAR_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.forexfactory.com/"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            data = response.read().decode("utf-8")
            parsed = json.loads(data)
            if parsed:
                try:
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(parsed, f, ensure_ascii=False)
                except Exception:
                    pass
                return parsed
    except Exception:
        # Fallback to existing cache if available (even if expired)
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

# Built-in Official Schedule for Federal Reserve FOMC Decisions (100% deterministic safety net)
BUILTIN_CRITICAL_SCHEDULE = {
    "2026-01-28": [
        {"title": "FOMC Federal Funds Rate Decision", "impact": "High", "time_israel": "21:00", "time_us": "14:00"},
        {"title": "FOMC Press Conference (Fed Chair Powell)", "impact": "High", "time_israel": "21:30", "time_us": "14:30"}
    ],
    "2026-03-18": [
        {"title": "FOMC Federal Funds Rate Decision & Projections", "impact": "High", "time_israel": "21:00", "time_us": "14:00"},
        {"title": "FOMC Press Conference (Fed Chair Powell)", "impact": "High", "time_israel": "21:30", "time_us": "14:30"}
    ],
    "2026-04-29": [
        {"title": "FOMC Federal Funds Rate Decision", "impact": "High", "time_israel": "21:00", "time_us": "14:00"},
        {"title": "FOMC Press Conference (Fed Chair Powell)", "impact": "High", "time_israel": "21:30", "time_us": "14:30"}
    ],
    "2026-06-17": [
        {"title": "FOMC Federal Funds Rate Decision & Projections", "impact": "High", "time_israel": "21:00", "time_us": "14:00"},
        {"title": "FOMC Press Conference (Fed Chair Powell)", "impact": "High", "time_israel": "21:30", "time_us": "14:30"}
    ],
    "2026-07-29": [
        {"title": "FOMC Federal Funds Rate Decision", "impact": "High", "time_israel": "21:00", "time_us": "14:00"},
        {"title": "FOMC Press Conference (Fed Chair Powell)", "impact": "High", "time_israel": "21:30", "time_us": "14:30"}
    ],
    "2026-09-16": [
        {"title": "FOMC Federal Funds Rate Decision & Projections", "impact": "High", "time_israel": "21:00", "time_us": "14:00"},
        {"title": "FOMC Press Conference (Fed Chair Powell)", "impact": "High", "time_israel": "21:30", "time_us": "14:30"}
    ],
    "2026-10-28": [
        {"title": "FOMC Federal Funds Rate Decision", "impact": "High", "time_israel": "21:00", "time_us": "14:00"},
        {"title": "FOMC Press Conference (Fed Chair Powell)", "impact": "High", "time_israel": "21:30", "time_us": "14:30"}
    ],
    "2026-12-09": [
        {"title": "FOMC Federal Funds Rate Decision & Projections", "impact": "High", "time_israel": "21:00", "time_us": "14:00"},
        {"title": "FOMC Press Conference (Fed Chair Powell)", "impact": "High", "time_israel": "21:30", "time_us": "14:30"}
    ],
}

def get_today_macro_risk(target_date: Optional[str] = None) -> Dict:
    """
    Checks if there are High-Impact US events on the specified date (default: today).
    target_date format: YYYY-MM-DD
    """
    # Israel time zone is UTC+3 in summer / daylight saving
    israel_tz = timezone(timedelta(hours=3))
    now_israel = datetime.now(israel_tz)
    
    if not target_date:
        target_date_str = now_israel.strftime("%Y-%m-%d")
    else:
        target_date_str = target_date

    today_high_impact = []
    seen_titles = set()

    # 1. Check built-in official schedule first (guaranteed offline safety net)
    if target_date_str in BUILTIN_CRITICAL_SCHEDULE:
        for ev in BUILTIN_CRITICAL_SCHEDULE[target_date_str]:
            today_high_impact.append(ev)
            seen_titles.add(ev["title"].lower())

    # 2. Augment with dynamic online feed
    events = fetch_weekly_events()
    for item in events:
        if item.get("country") != "USD":
            continue
        
        impact = item.get("impact", "")
        title = item.get("title", "")
        raw_date = item.get("date", "") # e.g. "2026-09-16T14:00:00-04:00"

        # Filter out routine FOMC member speeches unless marked High impact or by Fed Chair Powell
        is_routine_member_speech = ("member" in title.lower() and "speaks" in title.lower())
        if is_routine_member_speech and "chair" not in title.lower() and "powell" not in title.lower():
            if impact != "High":
                continue

        # Check if event is High Impact or matches critical market moving keywords
        is_critical_event = any(kw.lower() in title.lower() for kw in CRITICAL_KEYWORDS)
        is_high_impact = (impact == "High") or is_critical_event
        if not is_high_impact:
            continue

        # Extract date portion (YYYY-MM-DD)
        if "T" in raw_date:
            event_dt_str = raw_date.split("T")[0]
            event_time_us = raw_date.split("T")[1][:5]
        else:
            event_dt_str = raw_date[:10]
            event_time_us = ""

        if event_dt_str == target_date_str:
            if any(w in title.lower() for w in ["fomc", "federal funds"]) and any("fomc" in s for s in seen_titles):
                continue

            try:
                dt_obj = datetime.fromisoformat(raw_date)
                dt_israel = dt_obj.astimezone(israel_tz)
                time_israel_str = dt_israel.strftime("%H:%M")
                # Events before 14:00 Israel time (07:00 ET) are absorbed before US market open unless critical
                if dt_israel.hour < 14 and not is_critical_event:
                    continue
            except Exception:
                time_israel_str = "במהלך המסחר"

            today_high_impact.append({
                "title": title,
                "impact": impact,
                "time_us": event_time_us,
                "time_israel": time_israel_str,
                "forecast": item.get("forecast", ""),
                "previous": item.get("previous", "")
            })
            seen_titles.add(title.lower())

    has_risk = len(today_high_impact) > 0
    is_critical = any(any(kw.lower() in e["title"].lower() for kw in CRITICAL_KEYWORDS) for e in today_high_impact)

    warning_level = "CRITICAL" if is_critical else ("HIGH" if has_risk else "NORMAL")

    if is_critical:
        guidance = "⛔ איסור מוחלט על פקודות Limit פסיביות! השוק צפוי לניעור אלגוריתמי אלים. חובה להמתין עד לסיום מסיבת העיתונאים/ההודעה טרם פתיחת טריידים."
    elif has_risk:
        guidance = "⚠️ תנודתיות מאקרו גבוהה צפויה בשעות האירוע. מומלץ להשתמש בפקודות אישור היפוך (Confirmation) בלבד ולא בלימיט עיוור."
    else:
        guidance = "✅ יום שגרתי ללא אירועי מאקרו מדרגה ראשונה. ניתן לפעול לפי תוכנית הסווינג הרגילה."

    banner_hebrew = ""
    if has_risk:
        events_desc = ", ".join([f"{e['title']} ({e['time_israel']} שעון ישראל)" for e in today_high_impact])
        banner_hebrew = f"🚨 התראת מאקרו ({warning_level}): היום צפויים אירועים בעלי השפעה חריגה על השווקים: {events_desc}. {guidance}"

    return {
        "date": target_date_str,
        "has_high_impact": has_risk,
        "warning_level": warning_level,
        "events_count": len(today_high_impact),
        "events": today_high_impact,
        "guidance": guidance,
        "banner_hebrew": banner_hebrew
    }

if __name__ == "__main__":
    test_date = sys.argv[1] if len(sys.argv) > 1 else None
    res = get_today_macro_risk(test_date)
    print(json.dumps(res, indent=2, ensure_ascii=False))
