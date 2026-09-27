import json
from google import genai
from google.genai import types
from typing import Dict, Any
from config.config import Config

class AIAgent:
    """
    Interfaces with the next-gen official Google Gen AI SDK to synthesize technical
    and fundamental statistics into professional, data-backed market recommendations.
    """
    
    @staticmethod
    def analyze_stock(analysis_data: Dict[str, Any]) -> str:
        """
        Submits structured statistical summaries to Gemini to write an institutional-grade,
        visually premium financial briefing tailored for Telegram broadcast.
        """
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing. Please provide it in your .env file.")
            
        # Initialize official next-gen Google Gen AI Client
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        # Prepare structured data for AI reading
        ticker = analysis_data["fundamentals"]["ticker"]
        name = analysis_data["fundamentals"]["name"]
        
        # Format numbers for readability (e.g. Market Cap into Billions)
        mcap = analysis_data["fundamentals"]["market_cap"]
        formatted_mcap = "N/A"
        if isinstance(mcap, (int, float)):
            if mcap >= 1e12:
                formatted_mcap = f"${mcap / 1e12:.2f}T"
            elif mcap >= 1e9:
                formatted_mcap = f"${mcap / 1e9:.2f}B"
            elif mcap >= 1e6:
                formatted_mcap = f"${mcap / 1e6:.2f}M"
            else:
                formatted_mcap = f"${mcap:,.0f}"
        
        analysis_data["fundamentals"]["market_cap_formatted"] = formatted_mcap
        
        stock_summary_json = json.dumps(analysis_data, indent=2)
        
        # Import prompts from externalized prompt module
        from config.agent_prompt import SYSTEM_INSTRUCTION, PROMPT_TEMPLATE
        
        system_instruction = SYSTEM_INSTRUCTION
        prompt = PROMPT_TEMPLATE.format(
            stock_summary_json=stock_summary_json,
            ticker=ticker,
            name=name,
            formatted_mcap=formatted_mcap
        )
        
        # A robust list of premium models to try in sequence to bypass quotas or regional restrictions
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-3.5-flash",
            "gemini-2.5-pro"
        ]
        
        last_error = None
        for model_name in models_to_try:
            try:
                print(f"[+] Attempting synthesis using model: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1
                    )
                )
                print(f"[+] Generation successful using model {model_name}.")
                report_text = response.text.strip()
                divider = "\n━━━━━━━━━━━━━━━━━━━━\n"
                model_footer = f"{divider}🤖 **AI Analysis Model:** `{model_name}`"
                return report_text + "\n" + model_footer
            except Exception as e:
                print(f"[!] Warning: Model {model_name} failed or is rate-limited: {e}")
                last_error = e
                continue
                
        return f"⚠️ *Error generating AI report for {ticker}*: All attempted models failed. Last error: {last_error}"

    @staticmethod
    def analyze_portfolio_stock(analysis_data: Dict[str, Any]) -> str:
        """
        Submits structured portfolio statistics to Gemini to write an institutional-grade,
        visually premium portfolio briefing entirely in Hebrew.
        """
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing. Please provide it in your .env file.")
            
        # Initialize official next-gen Google Gen AI Client
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        # Prepare structured data for AI reading
        ticker = analysis_data["fundamentals"]["ticker"]
        name = analysis_data["fundamentals"]["name"]
        currency = analysis_data["fundamentals"]["currency"]
        
        metrics = analysis_data["portfolio_metrics"]
        
        # Format the stats JSON nicely for the AI context
        analysis_data_json = json.dumps(analysis_data, indent=2)
        
        # Import prompts from the new prompt module
        from config.agent_analyzed_pruchase_stock import SYSTEM_INSTRUCTION, PROMPT_TEMPLATE
        
        # Build the dynamic Fibonacci levels list formatted as a beautiful list
        fib_levels = metrics.get("fibonacci_levels", [])
        fib_formatted_lines = []
        for lvl in fib_levels:
            # Add a visual arrow pointing if the price is extremely close (within 2%) to this level
            is_current_here = ""
            curr_pr = metrics["current_price"]
            lvl_pr = lvl["price"]
            if lvl_pr > 0 and abs(curr_pr - lvl_pr) / lvl_pr <= 0.02:
                is_current_here = " ◀◀ המניה נסחרת כרגע ממש כאן!"
            
            role_emoji = "🟢" if "תמיכה" in lvl["current_role"] else "🔴"
            line = f"• {role_emoji} **רמת {lvl['name']} (`{lvl['price']}`):** {lvl['current_role'].split(' ')[0]} ({lvl['role_desc']}) | 🎯 **{lvl['total_touches']} נגיעות** _({lvl['support_touches']} מלמעלה, {lvl['resistance_touches']} מלמטה)_{is_current_here}"
            fib_formatted_lines.append(line)
            
        fibonacci_levels_formatted = "\n".join(fib_formatted_lines)
        
        sector = analysis_data["fundamentals"].get("sector", "N/A")
        
        system_instruction = SYSTEM_INSTRUCTION
        prompt = PROMPT_TEMPLATE.format(
            ticker=ticker,
            name=name,
            currency=currency,
            sector=sector,
            purchase_price=metrics["purchase_price"],
            purchase_date=metrics["purchase_date"],
            current_price=metrics["current_price"],
            daily_change=metrics["daily_change"],
            daily_change_emoji=metrics["daily_change_emoji"],
            total_return=metrics["total_return"],
            total_return_emoji=metrics["total_return_emoji"],
            consolidation=metrics["consolidation"],
            peak_price=metrics.get("peak_price", metrics["current_price"]),
            fibonacci_levels_formatted=fibonacci_levels_formatted,
            stock_summary_json=analysis_data_json
        )
        
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-3.5-flash",
            "gemini-2.5-pro"
        ]
        
        last_error = None
        for model_name in models_to_try:
            try:
                print(f"[+] Attempting synthesis using model: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1
                    )
                )
                print(f"[+] Generation successful using model {model_name}.")
                report_text = response.text.strip()
                divider = "\n━━━━━━━━━━━━━━━━━━━━\n"
                model_footer = f"{divider}🤖 **AI Analysis Model:** `{model_name}`"
                return report_text + "\n" + model_footer
            except Exception as e:
                print(f"[!] Warning: Model {model_name} failed or is rate-limited: {e}")
                last_error = e
                continue
                
        return f"⚠️ *שגיאה ביצירת דוח בינה מלאכותית עבור {ticker}*: כל המודלים נכשלו. שגיאה אחרונה: {last_error}"

    @staticmethod
    def analyze_strategic_stock(analysis_data: Dict[str, Any], investment_type: str, investment_period: str) -> str:
        """
        Submits structured strategic statistics to Gemini to write an institutional-grade,
        visually premium strategy briefing entirely in Hebrew.
        """
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing. Please provide it in your .env file.")
            
        # Initialize official next-gen Google Gen AI Client
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        # Prepare structured data for AI reading
        ticker = analysis_data["fundamentals"]["ticker"]
        name = analysis_data["fundamentals"]["name"]
        currency = analysis_data["fundamentals"]["currency"]
        
        metrics = analysis_data["portfolio_metrics"]
        
        # Format the stats JSON nicely for the AI context
        analysis_data_json = json.dumps(analysis_data, indent=2)
        
        # Import prompts from the new prompt module
        from config.agent_strategy_prompt import SYSTEM_INSTRUCTION, PROMPT_TEMPLATE
        
        # Build the dynamic Fibonacci levels list formatted as a beautiful list
        fib_levels = metrics.get("fibonacci_levels", [])
        fib_formatted_lines = []
        for lvl in fib_levels:
            is_current_here = ""
            curr_pr = metrics["current_price"]
            lvl_pr = lvl["price"]
            if lvl_pr > 0 and abs(curr_pr - lvl_pr) / lvl_pr <= 0.02:
                is_current_here = " ◀◀ המניה נסחרת כרגע ממש כאן!"
            
            role_emoji = "🟢" if "תמיכה" in lvl["current_role"] else "🔴"
            
            line = f"• {role_emoji} **רמת {lvl['name']} (`{lvl['price']}`):** {lvl['current_role'].split(' ')[0]} ({lvl['role_desc']}) | 🎯 **{lvl['total_touches']} נגיעות** _({lvl['support_touches']} מלמעלה, {lvl['resistance_touches']} מלמטה)_{is_current_here}"
            fib_formatted_lines.append(line)
            
        fibonacci_levels_formatted = "\n".join(fib_formatted_lines)
        
        sector = analysis_data["fundamentals"].get("sector", "N/A")
        
        system_instruction = SYSTEM_INSTRUCTION
        prompt = PROMPT_TEMPLATE.format(
            ticker=ticker,
            name=name,
            currency=currency,
            sector=sector,
            purchase_price=metrics["purchase_price"],
            current_price=metrics["current_price"],
            daily_change=metrics["daily_change"],
            daily_change_emoji=metrics["daily_change_emoji"],
            total_return=metrics["total_return"],
            total_return_emoji=metrics["total_return_emoji"],
            consolidation=metrics["consolidation"],
            peak_price=metrics.get("peak_price", metrics["current_price"]),
            fibonacci_levels_formatted=fibonacci_levels_formatted,
            stock_summary_json=analysis_data_json,
            investment_type=investment_type,
            investment_period=investment_period
        )
        
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-3.5-flash",
            "gemini-2.5-pro"
        ]
        
        last_error = None
        for model_name in models_to_try:
            try:
                print(f"[+] Attempting strategic synthesis using model: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1
                    )
                )
                print(f"[+] Generation successful using model {model_name}.")
                report_text = response.text.strip()
                divider = "\n━━━━━━━━━━━━━━━━━━━━\n"
                model_footer = f"{divider}🤖 **AI Analysis Model:** `{model_name}`"
                return report_text + "\n" + model_footer
            except Exception as e:
                print(f"[!] Warning: Model {model_name} failed or is rate-limited: {e}")
                last_error = e
                continue
                
        return f"⚠️ *שגיאה ביצירת דוח בינה מלאכותית אסטרטגי עבור {ticker}*: כל המודלים נכשלו. שגיאה אחרונה: {last_error}"
