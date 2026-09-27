import yfinance as yf
import pandas as pd
import datetime
from typing import Dict, Any, Optional
from config.config import Config

class DataFetcher:
    """
    Handles data ingestion using Yahoo Finance to query stock histories 
    and fundamental metrics for both US and Israeli (TASE) assets.
    """
    
    @staticmethod
    def fetch_stock_data(symbol: str, lookback_days: int = Config.LOOKBACK_DAYS) -> Optional[Dict[str, Any]]:
        """
        Fetches historical price candles and key fundamental metrics for a ticker.
        Supports standard US symbols (e.g. AAPL) and Tel Aviv symbols (e.g. TEVA.TA).
        """
        print(f"[+] Querying Yahoo Finance for symbol: {symbol}")
        try:
            ticker = yf.Ticker(symbol)
            
            # Fetch historical daily prices
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=lookback_days)
            
            # yfinance history handles split adjustments
            df = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if df.empty:
                print(f"[-] No price history found for {symbol} in the requested timeframe.")
                return None
                
            # Safely extract core financial metadata
            info: Dict[str, Any] = {}
            try:
                info = ticker.info
            except Exception as e:
                # Sometimes yfinance throws errors on ticker.info for obscure assets
                print(f"[!] Warning: Could not retrieve info dict for {symbol}: {e}")
                
            # Extract metrics with bulletproof fallback mappings
            fundamentals = {
                "ticker": symbol,
                "name": info.get("longName", symbol),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", info.get("forwardPE", "N/A")),
                "forward_pe": info.get("forwardPE", "N/A"),
                "eps": info.get("trailingEps", "N/A"),
                "dividend_yield": info.get("dividendYield", 0.0),
                "profit_margin": info.get("profitMargins", "N/A"),
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                "currency": info.get("currency", "USD")
            }
            
            # Fill missing current price using last closing row if info was empty
            if fundamentals["current_price"] == "N/A" and not df.empty:
                fundamentals["current_price"] = float(df['Close'].iloc[-1])
                
            return {
                "history": df,
                "fundamentals": fundamentals
            }
            
        except Exception as e:
            print(f"[-] Error fetching data for {symbol}: {e}")
            return None
