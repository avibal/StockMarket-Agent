import urllib.request
import urllib.parse
import json
import time
import sys
import os

def clean_markdown_for_telegram(text: str) -> str:
    """
    Sanitizes standard markdown text to be compatible with Telegram's legacy Markdown parser.
    Converts standard markdown bold '**text**' to Telegram legacy bold '*text*'.
    Balances asterisks and backticks to prevent parse errors.
    """
    if not text:
        return ""
        
    # Convert standard markdown bold '**' to Telegram legacy bold '*'
    text = text.replace("**", "*")
    
    # Balance asterisks '*'
    asterisk_count = text.count("*")
    if asterisk_count % 2 != 0:
        parts = text.rsplit("*", 1)
        text = "".join(parts)
        
    # Balance backticks '`'
    backtick_count = text.count("`")
    if backtick_count % 2 != 0:
        parts = text.rsplit("`", 1)
        text = "".join(parts)
        
    return text

def split_message(text: str, max_chars: int = 4000) -> list:
    """
    Splits a long message into multiple chunks that do not exceed max_chars.
    Splits at the nearest newline character or space to preserve readability.
    """
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
        
    chunks = []
    while text:
        if len(text) <= max_chars:
            chunks.append(text)
            break
            
        # Find the best split point before max_chars
        split_idx = text.rfind("\n", 0, max_chars)
        if split_idx == -1:
            split_idx = text.rfind(" ", 0, max_chars)
            
        if split_idx == -1 or split_idx < 1000:
            split_idx = max_chars
            
        chunks.append(text[:split_idx].strip())
        text = text[split_idx:].strip()
        
    return chunks

def send_message(token, chat_id, text, buttons=None, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Split text into chunks to respect Telegram's 4096-character limit (with a 4000 char safety margin)
    chunks = split_message(text, max_chars=4000)
    
    def _execute_request(payload_data):
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload_data).encode("utf-8"), 
            headers={"Content-Type": "application/json"}, 
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))

    results = []
    for i, chunk in enumerate(chunks):
        chunk_text = chunk
        
        # Paginate chunk if there are multiple parts
        if len(chunks) > 1:
            if parse_mode == "Markdown":
                chunk_text = clean_markdown_for_telegram(chunk_text)
            chunk_text += f"\n\n*(חלק {i+1}/{len(chunks)})*"
        else:
            if parse_mode == "Markdown":
                chunk_text = clean_markdown_for_telegram(chunk_text)
                
        data = {
            "chat_id": chat_id,
            "text": chunk_text
        }
        if parse_mode:
            data["parse_mode"] = parse_mode
            
        # Attach interactive reply buttons to the final chunk only
        if buttons and i == len(chunks) - 1:
            data["reply_markup"] = {"inline_keyboard": buttons}
            
        try:
            res = _execute_request(data)
            results.append(res)
        except Exception as e:
            telegram_error_msg = ""
            if hasattr(e, 'read'):
                try:
                    err_data = json.loads(e.read().decode('utf-8'))
                    telegram_error_msg = err_data.get("description", "")
                except Exception:
                    pass
            
            print(f"Error sending chunk {i+1}/{len(chunks)} (parse_mode={parse_mode}): {e}", file=sys.stderr)
            if telegram_error_msg:
                print(f"Telegram API Error Details: {telegram_error_msg}", file=sys.stderr)
                
            # Graceful Fallback: retry sending this specific chunk without parse_mode (plain text)
            if parse_mode and ("can't parse" in telegram_error_msg.lower() or "bad request" in str(e).lower() or "too long" in telegram_error_msg.lower()):
                print(f"[!] Warning: Retrying chunk {i+1}/{len(chunks)} dispatch as plain text...", file=sys.stderr)
                fallback_data = data.copy()
                fallback_data.pop("parse_mode", None)
                try:
                    res = _execute_request(fallback_data)
                    results.append(res)
                except Exception as retry_err:
                    print(f"Error sending plain text fallback for chunk {i+1}/{len(chunks)}: {retry_err}", file=sys.stderr)
                    results.append(None)
            else:
                results.append(None)
                
    return results[-1] if results and any(results) else None

def send_document(token, chat_id, filepath, caption=None):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    boundary = "----TelegramBotBoundary"
    try:
        with open(filepath, "rb") as f:
            file_data = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return None

    filename = os.path.basename(filepath)
    body = []
    body.append(f"--{boundary}".encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="chat_id"'.encode('utf-8'))
    body.append(b'')
    body.append(str(chat_id).encode('utf-8'))
    
    if caption:
        body.append(f"--{boundary}".encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="caption"'.encode('utf-8'))
        body.append(b'')
        body.append(caption.encode('utf-8'))
        
    body.append(f"--{boundary}".encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="document"; filename="{filename}"'.encode('utf-8'))
    body.append(b'Content-Type: text/markdown')
    body.append(b'')
    body.append(file_data)
    body.append(f"--{boundary}--".encode('utf-8'))
    body.append(b'')
    
    payload = b"\r\n".join(body)
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(payload))
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"Error sending document: {e}", file=sys.stderr)
        return None

def get_updates(token, offset=None):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    if offset: 
        url += f"?offset={offset}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8")).get("result", [])
    except Exception as e:
        print(f"Error getting updates: {e}", file=sys.stderr)
        return []

def answer_callback(token, callback_query_id, text):
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    data = {"callback_query_id": callback_query_id, "text": text}
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode("utf-8"), 
        headers={"Content-Type": "application/json"}, 
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res: 
            return True
    except Exception as e:
        print(f"Error answering callback: {e}", file=sys.stderr)
        return False

# ---------------------------------------------------------------------------
# Mode: --notify  (fire-and-forget milestone notification)
# Usage: py telegram_bridge.py <TOKEN> <CHAT_ID> --notify "<message>"
# ---------------------------------------------------------------------------
def run_notify(token, chat_id, message):
    result = send_message(token, chat_id, message, parse_mode=None)
    if result:
        safe_msg = message.encode('ascii', errors='replace').decode('ascii')
        print(f"NOTIFY_SENT: {safe_msg}")
        sys.exit(0)
    else:
        print("Failed to send notification.", file=sys.stderr)
        sys.exit(3)

# ---------------------------------------------------------------------------
# Mode: approval  (interactive plan review with buttons + polling)
# Usage: py telegram_bridge.py <TOKEN> <CHAT_ID> <TICKET_ID> <FEATURE> <PLAN_PATH>
# ---------------------------------------------------------------------------
def run_approval(token, chat_id, ticket_id, feature, plan_path):
    # Clean old updates
    updates = get_updates(token)
    offset = max(u["update_id"] for u in updates) + 1 if updates else None
    
    modified_files = []
    new_files = []
    tests = []
    
    # Parse implementation plan for details
    try:
        if os.path.exists(plan_path):
            with open(plan_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                line_str = line.strip()
                if "#### [MODIFY]" in line_str or "#### [NEW]" in line_str:
                    parts = line_str.split("] ")
                    if len(parts) > 1:
                        fname = parts[1].split("(")[0].strip()
                        fname = fname.strip("`[]")
                        if "#### [MODIFY]" in line_str:
                            modified_files.append(fname)
                        else:
                            new_files.append(fname)
                elif line_str.startswith("-") or line_str.startswith("*"):
                    cleaned = line_str.lstrip("-* ").strip()
                    if any(x in cleaned.lower() for x in ["test", "spec", "playwright", "assert"]):
                        tests.append(cleaned)
    except Exception as e:
        print(f"Warning: Could not parse plan file details: {e}", file=sys.stderr)
        
    # Build beautiful executive summary message
    summary_parts = [
        f"🔔 *Approval Request*",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"🎫 *Ticket ID:* `{ticket_id}`",
        f"📝 *Feature:* {feature}",
        ""
    ]
    
    if modified_files:
        summary_parts.append("🛠️ *Modified Files:*")
        for f in modified_files[:5]:
            summary_parts.append(f"  • `{f}`")
        if len(modified_files) > 5:
            summary_parts.append(f"  • _and {len(modified_files)-5} more_")
        summary_parts.append("")
        
    if new_files:
        summary_parts.append("✨ *New Files:*")
        for f in new_files[:5]:
            summary_parts.append(f"  • `{f}`")
        if len(new_files) > 5:
            summary_parts.append(f"  • _and {len(new_files)-5} more_")
        summary_parts.append("")
        
    if tests:
        summary_parts.append("🧪 *Automated Verification Tests:*")
        for t in tests[:3]:
            summary_parts.append(f"  • {t}")
        summary_parts.append("")
        
    summary_parts.append("💬 _Review the attached Markdown file for full architectural details._")
    summary_parts.append("💡 *Reply directly with text feedback to request revisions, or click a button:*")
    
    text = "\n".join(summary_parts)
    buttons = [[
        {"text": "🟢 APPROVED", "callback_data": f"approved_{ticket_id}"},
        {"text": "🔴 REJECTED", "callback_data": f"rejected_{ticket_id}"}
    ]]
    
    # 1. Send executive summary
    if not send_message(token, chat_id, text, buttons): 
        print("Failed to send Telegram notification.", file=sys.stderr)
        sys.exit(3)
        
    # 2. Upload full plan document
    if os.path.exists(plan_path):
        print("Uploading Full Plan Document to Telegram...")
        send_document(token, chat_id, plan_path, caption=f"📄 Full Work Plan for {ticket_id}")
        
    # 3. Listen for responses (polling loop)
    print("Waiting for your input via Telegram...")
    while True:
        time.sleep(2)
        updates = get_updates(token, offset)
        for u in updates:
            offset = u["update_id"] + 1
            
            # Case A: Callback query from buttons
            if "callback_query" in u:
                cb = u["callback_query"]
                sender = str(cb.get("from", {}).get("id", ""))
                cb_data, cb_id = cb.get("data", ""), cb.get("id", "")
                
                if sender != chat_id: 
                    continue
                    
                if cb_data == f"approved_{ticket_id}":
                    answer_callback(token, cb_id, "Plan Approved! Starting deployment...")
                    print("APPROVED")
                    sys.exit(0)
                elif cb_data == f"rejected_{ticket_id}":
                    answer_callback(token, cb_id, "Plan Rejected. Halting pipeline.")
                    print("REJECTED")
                    sys.exit(1)
                    
            # Case B: Free-text reply (feedback)
            elif "message" in u:
                msg = u["message"]
                sender = str(msg.get("from", {}).get("id", ""))
                
                if sender != chat_id: 
                    continue
                    
                feedback = msg.get("text")
                if feedback:
                    # Save feedback file in implementation_plans directory
                    feedback_file = os.path.join(os.path.dirname(plan_path), "telegram_feedback.txt")
                    with open(feedback_file, "w", encoding="utf-8") as f:
                        f.write(feedback)
                    print(f"FEEDBACK_RECEIVED: {feedback}")
                    sys.exit(2) # Exit code 2 triggers re-planning

def main():
    if len(sys.argv) < 3:
        print("Usage:", file=sys.stderr)
        print("  Approval mode: py telegram_bridge.py <TOKEN> <CHAT_ID> <TICKET_ID> <FEATURE> <PLAN_PATH>", file=sys.stderr)
        print("  Notify mode:   py telegram_bridge.py <TOKEN> <CHAT_ID> --notify \"<message>\"", file=sys.stderr)
        sys.exit(3)

    token, chat_id = sys.argv[1], sys.argv[2]

    # Detect mode
    if len(sys.argv) >= 4 and sys.argv[3] == "--notify":
        if len(sys.argv) < 5:
            print("Missing message argument for --notify mode.", file=sys.stderr)
            sys.exit(3)
        notify_message = sys.argv[4]
        run_notify(token, chat_id, notify_message)
    else:
        if len(sys.argv) < 6:
            print("Missing arguments for approval mode. Format: token chat_id ticket_id feature plan_path", file=sys.stderr)
            sys.exit(3)
        ticket_id, feature, plan_path = sys.argv[3], sys.argv[4], sys.argv[5]
        run_approval(token, chat_id, ticket_id, feature, plan_path)

if __name__ == '__main__':
    main()
