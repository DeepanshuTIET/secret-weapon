"""
Configuration settings for Indian Stock Tracker
"""
from pathlib import Path

# Application settings
APP_NAME = "Indian Stock Tracker"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Real-time stock tracking application for Indian markets (NSE/BSE)"

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DIST_DIR = BASE_DIR / "dist"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
DIST_DIR.mkdir(exist_ok=True)

# Popular Indian stock symbols (NSE)
DEFAULT_STOCKS = [
    "RELIANCE.NS",     # Reliance Industries Ltd
    "TCS.NS",          # Tata Consultancy Services
    "INFY.NS",         # Infosys Ltd
    "HDFCBANK.NS",     # HDFC Bank Ltd
    "ICICIBANK.NS",    # ICICI Bank Ltd
    "HINDUNILVR.NS",   # Hindustan Unilever Ltd
    "BHARTIARTL.NS",   # Bharti Airtel Ltd
    "ITC.NS",          # ITC Ltd
    "SBIN.NS",         # State Bank of India
    "KOTAKBANK.NS",    # Kotak Mahindra Bank
    "LT.NS",           # Larsen & Toubro Ltd
    "HCLTECH.NS",      # HCL Technologies Ltd
    "ASIANPAINT.NS",   # Asian Paints Ltd
    "MARUTI.NS",       # Maruti Suzuki India Ltd
    "TITAN.NS"         # Titan Company Ltd
]

# Data refresh intervals (in seconds)
REFRESH_INTERVALS = {
    "30 seconds": 30,
    "1 minute": 60,
    "5 minutes": 300,
    "15 minutes": 900,
    "30 minutes": 1800,
    "1 hour": 3600
}

# Excel export settings
EXCEL_CONFIG = {
    "filename_template": "indian_stocks_{timestamp}.xlsx",
    "sheet_name": "Indian Stock Data",
    "auto_save_interval": 300,  # 5 minutes
    "max_history_files": 10
}

# GUI settings
GUI_CONFIG = {
    "window_title": f"{APP_NAME} v{APP_VERSION}",
    "window_size": "1100x750",
    "min_size": (900, 600),
    "theme": {
        "bg_color": "#f8f9fa",
        "primary_color": "#0d6efd",
        "success_color": "#198754",
        "warning_color": "#ffc107", 
        "danger_color": "#dc3545",
        "text_color": "#212529"
    }
}

# API settings
API_CONFIG = {
    "timeout": 10,
    "retry_attempts": 3,
    "retry_delay": 1,
    "rate_limit_delay": 0.5  # 500ms between requests
}

# Indian market settings
MARKET_CONFIG = {
    "timezone": "Asia/Kolkata",
    "trading_days": [0, 1, 2, 3, 4],  # Monday to Friday
    "market_open": {"hour": 9, "minute": 15},
    "market_close": {"hour": 15, "minute": 30}
}
