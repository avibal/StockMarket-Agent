import os
from dotenv import load_dotenv

# Load environmental variables from .env if present
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Default high-interest US Stocks
    DEFAULT_US_TICKERS = [
        "AAPL",   # Apple
        "MSFT",   # Microsoft
        "NVDA",   # NVIDIA
        "AMZN",   # Amazon
        "META",   # Meta Platforms
        "TSLA",   # Tesla
        "GOOGL",  # Alphabet
        "PLTR",   # Palantir Technologies
        "AMD",    # Advanced Micro Devices
        "NFLX"    # Netflix
    ]
    
    # Default Israeli Stocks (TASE) listed with .TA suffix
    DEFAULT_IL_TICKERS = [
        "TEVA.TA",  # Teva Pharmaceutical Industries
        "ICL.TA",   # ICL Group (Israel Chemicals)
        "NICE.TA",  # Nice Systems
        "ONE.TA",   # One Software Technologies
        "AZRG.TA",  # Azrieli Group
        "DSCT.TA",  # Israel Discount Bank
        "POLI.TA",  # Bank Hapoalim
        "LUMI.TA",  # Bank Leumi
        "FIBI.TA",  # First International Bank of Israel
        "ELCO.TA",  # Elco Ltd.
        "OPAL.TA",  # Opals Group
        "ATRY.TA",  # Atreyu Capital Markets Ltd (ATRY.TA)
    ]
    
    # Technical Analysis Default Settings
    LOOKBACK_DAYS = 730  # 2 years of daily history to calculate 200-day SMA accurately
    RSI_PERIOD = 14
    SMA_FAST = 50
    SMA_SLOW = 200
    
    # Email SMTP Credentials (e.g. Gmail)
    EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
    
    @classmethod
    def validate(cls):
        """Validates that core credentials are set."""
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.TELEGRAM_TOKEN:
            missing.append("TELEGRAM_TOKEN")
        if not cls.TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
        return len(missing) == 0, missing

    @classmethod
    def validate_email(cls):
        """Validates that email credentials are set."""
        missing = []
        if not cls.EMAIL_SENDER:
            missing.append("EMAIL_SENDER")
        if not cls.EMAIL_PASSWORD:
            missing.append("EMAIL_PASSWORD")
        if not cls.EMAIL_RECEIVER:
            missing.append("EMAIL_RECEIVER")
        return len(missing) == 0, missing
