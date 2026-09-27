# ===========================================================================
# Stock Market AI Agent - Main Entry Point
# 
# Supported CLI Trigger Commands:
# 
# 1. Standard Single Stock Check (US or IL):
#    .\.venv\Scripts\python.exe main.py --ticker AAPL
#    .\.venv\Scripts\python.exe main.py --ticker TEVA.TA
# 
# 2. Market Portfolio Sweep (US or IL default lists):
#    .\.venv\Scripts\python.exe main.py --market us
#    .\.venv\Scripts\python.exe main.py --market il
# 
# 3. Custom Position Portfolio Analyzer (Hebrew report + CLI link):
#    .\.venv\Scripts\python.exe main.py --analyze-ticker OPAL.TA --purchase-price 1400
# 
# 4. Telegram Interactive Listener Daemon:
#    .\.venv\Scripts\python.exe main.py --listen
# ===========================================================================

import argparse
import sys
import os
import datetime
from config.config import Config
from data_fetcher import DataFetcher
from analyzer import Analyzer
from ai_agent import AIAgent
from telegram_bridge import send_message

# Force console standard output to UTF-8 to prevent Windows charmap print crashes (e.g. emojis)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def save_report_to_disk(symbol: str, report_text: str) -> str:
    """
    Saves the generated AI analysis report to the 'stock_analysis_reports' folder.
    Format: stock_analysis_reports/YYYYMMDD_[SYMBOL].md
    Returns the absolute path to the saved file, or None on failure.
    """
    folder = "stock_analysis_reports"
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            print(f"[+] Created directory: {folder}")
        except Exception as e:
            print(f"[-] Warning: Failed to create directory '{folder}': {e}")
            return None
            
    date_str = datetime.date.today().strftime("%Y%m%d")
    filename = f"{date_str}_{symbol}.md"
    filepath = os.path.join(folder, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)
        abs_path = os.path.abspath(filepath)
        print(f"[+] Saved analysis report to disk: {abs_path}")
        return abs_path
    except Exception as e:
        print(f"[-] Warning: Failed to write report file '{filepath}': {e}")
        return None

def process_ticker(symbol: str, publish_telegram: bool = True) -> bool:
    """
    Executes the quantitative stock analysis cycle: fetches historical & basic 
    fundamentals, calculates indicators, generates AI briefing, saves report to disk,
    and forwards to Telegram.
    """
    print(f"\n==================================================")
    print(f"🚀 PROCESSING TICKER: {symbol}")
    print(f"==================================================")
    
    # 1. Ingest stock metrics
    stock_data = DataFetcher.fetch_stock_data(symbol)
    if not stock_data:
        msg = f"I am not allow to check this ticker"
        print(f"[-] {msg}")
        if publish_telegram:
            is_valid, missing = Config.validate()
            if is_valid:
                send_message(
                    token=Config.TELEGRAM_TOKEN,
                    chat_id=Config.TELEGRAM_CHAT_ID,
                    text=f"⚠️ {msg}: {symbol}"
                )
        return False
        
    # 2. Analyze Technical and Fundamental thresholds
    analysis_results = Analyzer.analyze(stock_data)
    print(f"[+] Analytics successfully completed for {symbol}.")
    
    # 3. Request Gemini synthesis report
    print(f"[+] Synthesizing data with Gemini AI...")
    report = AIAgent.analyze_stock(analysis_results)
    
    # 4. Save the generated report to disk (Point 2)
    filepath = save_report_to_disk(symbol, report)
    
    # Output to stdout for terminal review
    print("\n--- AI FINANCIAL REPORT SUMMARY ---")
    if filepath:
        file_link = f"file:///{filepath.replace(os.sep, '/')}"
        print(f"[+] Report Link: {file_link}")
    else:
        print(report)
    print("------------------------------------\n")
    
    # 5. Broadcast channel update
    if publish_telegram:
        is_valid, missing = Config.validate()
        if not is_valid:
            print(f"[!] Alert: Cannot post to Telegram. Missing parameters in .env: {missing}")
            return False
            
        print(f"[+] Broadcasting update to Telegram channel...")
        result = send_message(
            token=Config.TELEGRAM_TOKEN,
            chat_id=Config.TELEGRAM_CHAT_ID,
            text=report,
            parse_mode="Markdown"
        )
        if result and result.get("ok"):
            print(f"[+] Successfully posted {symbol} report to Telegram!")
            return True
        else:
            print(f"[-] Telegram dispatch failed: {result}")
            return False
            
    return True

def process_portfolio_ticker(symbol: str, purchase_price: float, publish_telegram: bool = True) -> bool:
    """
    Executes the custom portfolio stock analysis cycle: fetches historical & fundamentals,
    calculates portfolio specific statistics (daily change, return, support/resistance, consolidation),
    generates AI briefing in Hebrew, saves the report to disk, and forwards to Telegram.
    """
    print(f"\n==================================================")
    print(f"💼 PROCESSING PORTFOLIO TICKER: {symbol} (Bought at: {purchase_price})")
    print(f"==================================================")
    
    # 1. Ingest stock metrics (fetch historical price candles based on config to discover purchase date)
    stock_data = DataFetcher.fetch_stock_data(symbol, lookback_days=Config.LOOKBACK_DAYS)
    if not stock_data:
        msg = f"I am not allowed to check this ticker"
        print(f"[-] {msg}")
        return False
        
    # 2. Analyze Portfolio metrics
    analysis_results = Analyzer.analyze_portfolio(stock_data, purchase_price)
    print(f"[+] Portfolio analytics successfully completed for {symbol}.")
    
    # 3. Request Gemini synthesis report in Hebrew
    print(f"[+] Synthesizing data with Gemini AI...")
    report = AIAgent.analyze_portfolio_stock(analysis_results)
    
    # 4. Save the generated report to disk
    filepath = save_report_to_disk(symbol, report)
    
    # Output only the link to stdout for terminal review
    print("\n--- AI FINANCIAL REPORT SUMMARY ---")
    if filepath:
        file_link = f"file:///{filepath.replace(os.sep, '/')}"
        print(f"[+] Report Link: {file_link}")
    else:
        print(report)
    print("------------------------------------\n")
    
    # 5. Broadcast channel update
    telegram_success = True
    if publish_telegram:
        is_valid, missing = Config.validate()
        if not is_valid:
            print(f"[!] Alert: Cannot post to Telegram. Missing parameters in .env: {missing}")
            telegram_success = False
        else:
            print(f"[+] Broadcasting update to Telegram channel...")
            result = send_message(
                token=Config.TELEGRAM_TOKEN,
                chat_id=Config.TELEGRAM_CHAT_ID,
                text=report,
                parse_mode="Markdown"
            )
            if result and result.get("ok"):
                print(f"[+] Successfully posted {symbol} portfolio report to Telegram!")
            else:
                print(f"[-] Telegram dispatch failed: {result}")
                telegram_success = False
                
    # 6. Send email notification
    from email_bridge import send_email_report
    email_subject = f"📊 דוח תיק השקעות: {symbol}"
    send_email_report(email_subject, report)
    
    return telegram_success

def process_strategic_ticker(symbol: str, purchase_price: float, investment_type: str, investment_period: str, publish_telegram: bool = True) -> bool:
    """
    Executes the strategy-based stock analysis cycle: fetches historical & fundamentals,
    calculates timeframe-specific statistics, generates strategic AI briefing in Hebrew,
    saves the report to disk, and broadcasts it to Telegram.
    """
    print(f"\n==================================================")
    print(f"🎯 PROCESSING STRATEGIC TICKER: {symbol} (Bought at: {purchase_price})")
    print(f"🎯 Strategy: {investment_type} | Timeframe: {investment_period}")
    print(f"==================================================")
    
    # 1. Ingest stock metrics
    stock_data = DataFetcher.fetch_stock_data(symbol, lookback_days=Config.LOOKBACK_DAYS)
    if not stock_data:
        msg = f"I am not allowed to check this ticker"
        print(f"[-] {msg}")
        return False
        
    # 2. Analyze Strategic Position metrics
    analysis_results = Analyzer.analyze_strategic_position(
        stock_data, purchase_price, investment_type, investment_period
    )
    print(f"[+] Strategic analytics successfully completed for {symbol}.")
    
    # 3. Request Gemini strategic synthesis report in Hebrew
    print(f"[+] Synthesizing data with Gemini AI...")
    report = AIAgent.analyze_strategic_stock(analysis_results, investment_type, investment_period)
    
    # 4. Save the generated report to disk
    filepath = save_report_to_disk(f"{symbol}_STRATEGY", report)
    
    # Output only the link to stdout for terminal review
    print("\n--- AI FINANCIAL REPORT SUMMARY ---")
    if filepath:
        file_link = f"file:///{filepath.replace(os.sep, '/')}"
        print(f"[+] Report Link: {file_link}")
    else:
        print(report)
    print("------------------------------------\n")
    
    # 5. Broadcast channel update
    telegram_success = True
    if publish_telegram:
        is_valid, missing = Config.validate()
        if not is_valid:
            print(f"[!] Alert: Cannot post to Telegram. Missing parameters in .env: {missing}")
            telegram_success = False
        else:
            print(f"[+] Broadcasting update to Telegram channel...")
            result = send_message(
                token=Config.TELEGRAM_TOKEN,
                chat_id=Config.TELEGRAM_CHAT_ID,
                text=report,
                parse_mode="Markdown"
            )
            if result and result.get("ok"):
                print(f"[+] Successfully posted {symbol} strategic report to Telegram!")
            else:
                print(f"[-] Telegram dispatch failed: {result}")
                telegram_success = False
                
    # 6. Send email notification
    from email_bridge import send_email_report
    email_subject = f"🎯 דוח אסטרטגי: {symbol} ({investment_type} - {investment_period})"
    send_email_report(email_subject, report)
    
    return telegram_success

def run_telegram_listener():
    """
    Listens for interactive updates from Telegram and triggers the `/check <ticker>` command.
    """
    import time
    from telegram_bridge import get_updates
    
    print("\n==================================================")
    print("🤖 Stock Market AI Bot Listener Activated")
    print("🤖 Listening for '/check <stock_symbol>'...")
    print("==================================================")
    
    is_valid, missing = Config.validate()
    if not is_valid:
        print(f"[!] Error: Missing environment variables for Telegram: {missing}")
        return
        
    token = Config.TELEGRAM_TOKEN
    
    # Purge old updates to prevent processing past commands
    print("[+] Purging backlog Telegram updates...")
    updates = get_updates(token)
    offset = max(u["update_id"] for u in updates) + 1 if updates else None
    print("[+] Done. Bot is now active and polling.")
    
    while True:
        try:
            time.sleep(2)
            updates = get_updates(token, offset)
            for u in updates:
                offset = u["update_id"] + 1
                
                if "message" in u:
                    msg = u["message"]
                    sender_chat = msg.get("chat", {})
                    sender_id = sender_chat.get("id")
                    text = msg.get("text", "").strip()
                    
                    if not text or not sender_id:
                        continue
                        
                    # Match '/check <symbol>' command
                    if text.lower().startswith("/check"):
                        parts = text.split()
                        if len(parts) < 2:
                            send_message(
                                token=token, 
                                chat_id=sender_id, 
                                text="⚠️ *Format error*: Use `/check <symbol>`\nExample: `/check AAPL` or `/check TEVA.TA`", 
                                parse_mode="Markdown"
                            )
                            continue
                            
                        symbol = parts[1].upper().strip()
                        print(f"[+] Triggered check command for: {symbol} from chat_id {sender_id}")
                        
                        # Send initial acknowledgment
                        send_message(
                            token=token, 
                            chat_id=sender_id, 
                            text=f"🔍 *Processing quantitative check for {symbol}...*", 
                            parse_mode="Markdown"
                        )
                        
                        # Execute scanning logic
                        try:
                            raw_data = DataFetcher.fetch_stock_data(symbol)
                            if not raw_data:
                                msg = f"I am not allow to check this ticker"
                                print(f"[-] {msg}")
                                send_message(
                                    token=token, 
                                    chat_id=sender_id, 
                                    text=f"⚠️ {msg}: {symbol}"
                                )
                                continue
                                
                            analysis_results = Analyzer.analyze(raw_data)
                            report = AIAgent.analyze_stock(analysis_results)
                            
                            # Save to disk as Markdown
                            save_report_to_disk(symbol, report)
                            
                            # Dispatch report
                            send_message(
                                token=token, 
                                chat_id=sender_id, 
                                text=report, 
                                parse_mode="Markdown"
                            )
                            print(f"[+] Successfully generated and dispatched {symbol} check.")
                        except Exception as inner_ex:
                            print(f"[-] Error inside check: {inner_ex}")
                            send_message(
                                token=token, 
                                chat_id=sender_id, 
                                text=f"⚠️ *Execution Error*: {inner_ex}", 
                                parse_mode="Markdown"
                            )
                            
        except KeyboardInterrupt:
            print("\n[+] Stopping Telegram listener daemon safely...")
            break
        except Exception as e:
            print(f"[!] Warning: Listener loop encountered error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Stock Market AI Agent - US & Israel Stocks Scanner")
    
    # Mutually exclusive selector for targeted execution
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--ticker", type=str, help="Analyze a single ticker (e.g. NVDA or TEVA.TA)")
    group.add_argument("-m", "--market", type=str, choices=["us", "il"], help="Analyze default market list ('us' or 'il')")
    group.add_argument("-l", "--listen", action="store_true", help="Start the interactive Telegram Bot listener daemon")
    group.add_argument("-at", "--analyze-ticker", type=str, help="Analyze a purchased ticker (e.g. OPAL.TA)")
    
    # Control flags
    parser.add_argument("-pp", "--purchase-price", type=float, help="The purchase price of the stock (required for --analyze-ticker)")
    parser.add_argument("-it", "--investment-type", type=str, help="Investment type (e.g. swing, long-term) for strategic analysis")
    parser.add_argument("-ip", "--investment-period", type=str, help="Investment period (e.g. 2 months, 1 year) for strategic analysis")
    parser.add_argument("--no-telegram", action="store_true", help="Disable publishing generated analysis output to Telegram Channel")
    
    args = parser.parse_args()
    
    # Pre-flight check for Gemini key
    if not Config.GEMINI_API_KEY:
        print("\n[!] CRITICAL: GEMINI_API_KEY is not defined in your environment.", file=sys.stderr)
        print("[!] Action Required: Create a '.env' file based on '.env.example' and enter your Google AI Studio key.", file=sys.stderr)
        sys.exit(1)
        
    if args.analyze_ticker and args.purchase_price is None:
        parser.error("--purchase-price is required when using --analyze-ticker")
        
    if args.listen:
        run_telegram_listener()
        return
        
    # Execute strategic or custom portfolio analysis if active
    if args.analyze_ticker:
        symbol = args.analyze_ticker.upper()
        purchase_price = args.purchase_price
        publish_telegram = not args.no_telegram
        
        # Check if strategic analysis parameters are present
        if args.investment_type or args.investment_period:
            if not args.investment_type or not args.investment_period:
                parser.error("Both --investment-type (-it) and --investment-period (-ip) are required for strategic analysis.")
            try:
                process_strategic_ticker(
                    symbol, 
                    purchase_price, 
                    args.investment_type, 
                    args.investment_period, 
                    publish_telegram=publish_telegram
                )
            except Exception as e:
                print(f"[-] Unexpected error scanning strategic position {symbol}: {e}")
        else:
            try:
                process_portfolio_ticker(symbol, purchase_price, publish_telegram=publish_telegram)
            except Exception as e:
                print(f"[-] Unexpected error scanning portfolio {symbol}: {e}")
        return
        
    # Compile scan list
    scan_list = []
    if args.ticker:
        scan_list = [args.ticker.upper()]
    elif args.market == "us":
        scan_list = Config.DEFAULT_US_TICKERS
        print(f"[+] Commencing sweep on default US portfolio: {scan_list}")
    elif args.market == "il":
        scan_list = Config.DEFAULT_IL_TICKERS
        print(f"[+] Commencing sweep on default Israeli (TASE) portfolio: {scan_list}")
        
    # Execute batch sweep
    successes = 0
    publish_telegram = not args.no_telegram
    for symbol in scan_list:
        try:
            if process_ticker(symbol, publish_telegram=publish_telegram):
                successes += 1
        except Exception as e:
            print(f"[-] Unexpected error scanning {symbol}: {e}")
            
    print(f"\n[+] Sweep finished. Successfully completed {successes} of {len(scan_list)} assets.")

if __name__ == "__main__":
    main()
