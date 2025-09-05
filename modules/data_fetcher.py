"""
Data fetcher module for retrieving real-time Indian stock data
Optimized for NSE/BSE markets with rate limiting protection
"""
import yfinance as yf
import pandas as pd
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Try to import NSEtools for additional Indian market data
try:
    from nsetools import Nse
    NSE_AVAILABLE = True
except ImportError:
    NSE_AVAILABLE = False

logger = logging.getLogger(__name__)

class IndianStockDataFetcher:
    """
    Robust stock data fetcher optimized for Indian markets (NSE/BSE)
    """
    
    def __init__(self, timeout: int = 10, max_retries: int = 3, rate_limit_delay: float = 0.5):
        """
        Initialize the Indian stock data fetcher
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            rate_limit_delay: Delay between requests to avoid rate limiting
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.session = self._create_session()
        
        # Initialize NSE connection if available
        self.nse = None
        if NSE_AVAILABLE:
            try:
                self.nse = Nse()
                logger.info("NSEtools initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize NSEtools: {e}")
                self.nse = None
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get comprehensive stock information for a single Indian stock symbol
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            
        Returns:
            Dictionary containing stock information or None if failed
        """
        # Try NSE first for Indian stocks
        if symbol.endswith('.NS') and self.nse:
            nse_data = self._get_nse_stock_info(symbol)
            if nse_data:
                logger.info(f"Successfully fetched {symbol} data from NSE")
                return nse_data
            else:
                logger.info(f"NSE failed for {symbol}, trying Yahoo Finance")
        
        # Fall back to Yahoo Finance
        return self._get_yahoo_stock_info(symbol)
    
    def _get_nse_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get stock info using NSEtools for Indian stocks"""
        if not self.nse:
            return None
            
        try:
            # Remove .NS suffix for NSE API
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            
            # Get quote from NSE
            quote = self.nse.get_quote(clean_symbol)
            
            if quote:
                # Parse NSE data
                current_price = float(quote.get('lastPrice', 0))
                previous_close = float(quote.get('previousClose', 0))
                
                change = current_price - previous_close if previous_close else 0
                change_percent = (change / previous_close * 100) if previous_close else 0
                
                return {
                    'symbol': symbol,
                    'name': quote.get('companyName', clean_symbol),
                    'current_price': current_price,
                    'previous_close': previous_close,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': quote.get('totalTradedVolume'),
                    'market_cap': None,
                    'pe_ratio': quote.get('pe'),
                    'dividend_yield': None,
                    'fifty_two_week_high': quote.get('high52'),
                    'fifty_two_week_low': quote.get('low52'),
                    'timestamp': datetime.now(),
                    'source': 'NSE'
                }
            
        except Exception as e:
            logger.error(f"Error fetching NSE data for {symbol}: {str(e)}")
            
        return None
    
    def _get_yahoo_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get stock info using Yahoo Finance API"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got rate limited
            if not info or len(info) < 3:
                logger.warning(f"Possible rate limiting or no data for {symbol}")
                time.sleep(1)  # Wait 1 second before retry
                info = ticker.info
            
            # Get current price and other key metrics
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            
            if current_price is None:
                logger.warning(f"Could not get current price for {symbol}")
                return None
            
            # Calculate change and percentage change
            if previous_close:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            else:
                change = 0
                change_percent = 0
            
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': current_price,
                'previous_close': previous_close,
                'change': change,
                'change_percent': change_percent,
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'timestamp': datetime.now(),
                'source': 'Yahoo Finance'
            }
            
            logger.info(f"Successfully fetched {symbol} data from Yahoo Finance")
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get stock information for multiple symbols with rate limiting protection
        
        Args:
            symbols: List of Indian stock symbols
            
        Returns:
            DataFrame containing stock data for all symbols
        """
        stock_data_list = []
        
        for i, symbol in enumerate(symbols):
            # Add delay between requests to avoid rate limiting
            if i > 0:
                time.sleep(self.rate_limit_delay)
                
            stock_data = self.get_stock_info(symbol.upper().strip())
            if stock_data:
                stock_data_list.append(stock_data)
            else:
                logger.warning(f"Failed to fetch data for {symbol}")
        
        if stock_data_list:
            df = pd.DataFrame(stock_data_list)
            return df
        else:
            return pd.DataFrame()
    
    def is_market_open(self) -> bool:
        """
        Check if the Indian stock market is currently open (IST market hours)
        
        Returns:
            True if market is open, False otherwise
        """
        try:
            # Use time-based check for Indian markets to avoid rate limiting
            import pytz
            
            # Get current time in IST
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            
            # Indian market hours: 9:15 AM - 3:30 PM IST, Mon-Fri
            if now.weekday() >= 5:  # Weekend
                return False
                
            market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
            
            return market_start <= now <= market_end
            
        except Exception as e:
            logger.error(f"Error checking market status: {str(e)}")
            # Fallback to simple time check
            now = datetime.now()
            if now.weekday() >= 5:  # Weekend
                return False
            # Rough IST market hours approximation
            return 9 <= now.hour < 16
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a stock symbol exists
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if symbol exists, False otherwise
        """
        try:
            stock_data = self.get_stock_info(symbol)
            return stock_data is not None
            
        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {str(e)}")
            return False
    
    def get_trending_stocks(self) -> List[str]:
        """
        Get trending Indian stocks
        
        Returns:
            List of trending Indian stock symbols
        """
        # Popular Indian stocks
        trending_stocks = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "KOTAKBANK.NS",
            "LT.NS", "HCLTECH.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS",
            "WIPRO.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TATAMOTORS.NS"
        ]
        return trending_stocks

# Utility functions for data formatting
def format_currency(value: float, currency: str = "INR") -> str:
    """Format a number as currency"""
    if value is None:
        return "N/A"
    
    if currency == "INR":
        return f"₹{value:,.2f}"
    else:
        return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format a number as percentage"""
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"

def format_large_number(value: float, currency: str = "INR") -> str:
    """Format large numbers with Indian notation (Lakh, Crore)"""
    if value is None:
        return "N/A"
    
    symbol = "₹" if currency == "INR" else "$"
    
    if value >= 1e12:
        return f"{symbol}{value/1e12:.2f}T"
    elif value >= 1e9:
        return f"{symbol}{value/1e9:.2f}B"
    elif value >= 1e7:  # 1 Crore
        return f"{symbol}{value/1e7:.2f}Cr"
    elif value >= 1e5:  # 1 Lakh
        return f"{symbol}{value/1e5:.2f}L"
    elif value >= 1e3:
        return f"{symbol}{value/1e3:.2f}K"
    else:
        return f"{symbol}{value:.2f}"
