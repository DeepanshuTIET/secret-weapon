"""
Stock data fetcher for Indian markets

This module handles fetching stock data from NSE/BSE markets.
Had to deal with a lot of API issues, so added caching and rate limiting.
"""
import yfinance as yf
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import pickle
try:
    from fake_useragent import UserAgent
    FAKE_USERAGENT_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False
    UserAgent = None
import ssl
import urllib3

# Try to import NSEtools for additional Indian market data
try:
    from nsetools import Nse
    NSE_AVAILABLE = True
except ImportError:
    NSE_AVAILABLE = False

# This was giving SSL warnings, so just disable them
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Constants 
DEFAULT_TIMEOUT = 15
MAX_RETRIES = 3

class IndianStockDataFetcher:
    """
    Robust stock data fetcher optimized for Indian markets (NSE/BSE)
    """
    
    def __init__(self, timeout=DEFAULT_TIMEOUT, max_retries=MAX_RETRIES, rate_limit_delay=1.0, cache_expire_hours=1):
        """
        Setup the data fetcher
        
        Note: Had to increase default timeout because Yahoo API can be slow sometimes
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.cache_expire_hours = cache_expire_hours
        
        # User agent stuff - helps avoid getting blocked
        self.ua = None
        if FAKE_USERAGENT_AVAILABLE:
            try:
                self.ua = UserAgent()
            except Exception as e:
                # Sometimes this fails, not a big deal
                logger.warning(f"UserAgent init failed: {e}")
        
        self.session = self._create_session()
        
        # Simple cache - just using JSON for now, might switch to SQLite later
        self.cache_file = "stock_cache.json"
        self.cache_data = self._load_cache()
        
        # Rate limiting stuff
        self.last_request_time = 0
        
        # Batch cache - not really using this anymore but keeping for compatibility
        self.batch_cache = {}
        self.batch_cache_time = None
        
        # Try to use NSE API first, but it's flaky
        self.nse = None
        if NSE_AVAILABLE:
            try:
                self.nse = Nse()
                logger.info("NSEtools working")
            except Exception as e:
                # NSE API is unreliable anyway
                logger.warning(f"NSE init failed: {e}")
                self.nse = None
        
    def _load_cache(self):
        """Load cache from file"""
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                # Clean up old entries
                current_time = datetime.now()
                valid_cache = {}
                for key, value in cache.items():
                    try:
                        cache_time = datetime.fromisoformat(value.get('timestamp', '2000-01-01'))
                        if (current_time - cache_time).total_seconds() < self.cache_expire_hours * 3600:
                            valid_cache[key] = value
                    except:
                        # Skip invalid entries
                        continue
                return valid_cache
        except:
            # File doesn't exist or corrupted, start fresh
            return {}
    
    def _save_cache(self):
        """Save cache - probably should add some error handling here"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f, default=str)
        except Exception as e:
            # Not critical if cache save fails
            logger.warning(f"Cache save failed: {e}")
    
    def _get_from_cache(self, symbol: str) -> Optional[Dict]:
        """Get data from cache if available and fresh"""
        if symbol in self.cache_data:
            cache_entry = self.cache_data[symbol]
            cache_time = datetime.fromisoformat(cache_entry.get('timestamp', '2000-01-01'))
            if (datetime.now() - cache_time).total_seconds() < self.cache_expire_hours * 3600:
                logger.info(f"Using cached data for {symbol}")
                return cache_entry.get('data')
        return None
    
    def _store_in_cache(self, symbol: str, data: Dict):
        """Store data in cache"""
        self.cache_data[symbol] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy and SSL fixes"""
        session = requests.Session()
        
        # Set user agent rotation
        user_agent = 'Indian Stock Tracker/1.0'
        if self.ua:
            try:
                user_agent = self.ua.random
            except Exception:
                pass
        session.headers.update({'User-Agent': user_agent})
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=2,  # Increased backoff
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # SSL context fixes
        session.verify = False  # Disable SSL verification for problematic endpoints
        
        return session
    
    def _rate_limit_delay(self):
        """Add delay between requests to be nice to the API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            # Don't want to spam the logs
            if sleep_time > 0.1:  
                logger.debug(f"Sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_stock_info(self, symbol, force_refresh=False):
        """Get stock data - tries NSE first, then Yahoo as fallback"""
        # Try NSE first for Indian stocks
        if symbol.endswith('.NS') and self.nse:
            nse_data = self._get_nse_stock_info(symbol)
            if nse_data:
                logger.info(f"Got {symbol} from NSE")
                return nse_data
            else:
                logger.info(f"NSE failed for {symbol}, trying Yahoo")
        
        # Yahoo Finance fallback
        return self._get_yahoo_stock_info(symbol, force_refresh)
    
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
    
    def _get_yahoo_stock_info(self, symbol, force_refresh=False):
        """Yahoo Finance data fetcher with retries and caching"""
        try:
            # Check cache first - saves API calls (unless force refresh)
            if not force_refresh:
                cached_data = self._get_from_cache(symbol)
                if cached_data:
                    return cached_data
            
            # Be nice to the API
            self._rate_limit_delay()
            
            # Don't pass session anymore - yfinance doesn't like it
            ticker = yf.Ticker(symbol)
            
            # Retry logic - sometimes Yahoo is dicey
            info = None
            for i in range(self.max_retries):
                try:
                    info = ticker.info
                    if info and len(info) > 3:  # Make sure we got real data
                        break
                    else:
                        logger.warning(f"Try {i + 1}: Got limited data for {symbol}")
                        time.sleep(2 ** i)  # Exponential backoff
                except Exception as e:
                    logger.warning(f"Try {i + 1} failed for {symbol}: {e}")
                    if i < self.max_retries - 1:
                        time.sleep(2 ** i)
                    else:
                        raise e
            
            if not info or len(info) < 3:
                logger.error(f"No valid data received for {symbol} after {self.max_retries} attempts")
                return None
            
            # Get price - Yahoo has inconsistent field names :(
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('regularMarketPreviousClose')
            previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
            
            if current_price is None:
                logger.warning(f"No price for {symbol}")
                return None
            
            # Calculate change
            if previous_close and previous_close > 0:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            else:
                change = 0
                change_percent = 0
            
            # Build result dict
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName') or info.get('shortName') or symbol,
                'current_price': current_price,
                'previous_close': previous_close,
                'change': change,
                'change_percent': change_percent,
                'volume': info.get('volume') or info.get('regularMarketVolume'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'dividend_yield': info.get('dividendYield'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'timestamp': datetime.now(),
                'source': 'Yahoo Finance'
            }
            
            # Store in cache
            self._store_in_cache(symbol, stock_data)
            
            logger.info(f"Successfully fetched {symbol} data from Yahoo Finance")
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_multiple_stocks_batch(self, symbols, force_refresh=False):
        """
        Batch fetch multiple stocks - much faster than individual calls
        force_refresh: if True, bypasses cache to get fresh data
        """
        try:
            # Try cache first (unless force refresh)
            if not force_refresh:
                cached_data = []
                for sym in symbols:
                    cached = self._get_from_cache(sym)
                    if cached:
                        cached_data.append(cached)
                
                if len(cached_data) == len(symbols):
                    logger.info(f"All {len(cached_data)} symbols from cache")
                    return pd.DataFrame(cached_data)
            else:
                logger.info("Force refresh - bypassing cache")
            
            # Clean symbols
            clean_symbols = [s.upper().strip() for s in symbols]
            
            # Apply rate limiting before batch request
            self._rate_limit_delay()
            
            logger.info(f"Fetching batch data for {len(clean_symbols)} symbols")
            
            # Use yfinance download for batch request - much more efficient
            try:
                batch_data = yf.download(
                    clean_symbols, 
                    period="1d", 
                    interval="1m",
                    group_by="ticker",
                    auto_adjust=True,
                    prepost=True,
                    threads=True
                )
                
                stock_data_list = []
                
                for symbol in clean_symbols:
                    try:
                        if len(clean_symbols) == 1:
                            # Single stock case
                            symbol_data = batch_data
                        else:
                            # Multiple stocks case
                            symbol_data = batch_data[symbol] if symbol in batch_data.columns.levels[0] else None
                        
                        if symbol_data is not None and not symbol_data.empty:
                            # Get the latest available data
                            latest_data = symbol_data.dropna().tail(1)
                            
                            if not latest_data.empty:
                                current_price = float(latest_data['Close'].iloc[0])
                                
                                # Get additional info if needed
                                ticker = yf.Ticker(symbol)
                                info = ticker.info
                                
                                previous_close = info.get('previousClose', current_price)
                                change = current_price - previous_close if previous_close else 0
                                change_percent = (change / previous_close * 100) if previous_close else 0
                                
                                stock_data = {
                                    'symbol': symbol,
                                    'name': info.get('longName') or info.get('shortName') or symbol,
                                    'current_price': current_price,
                                    'previous_close': previous_close,
                                    'change': change,
                                    'change_percent': change_percent,
                                    'volume': info.get('volume') or latest_data.get('Volume', 0).iloc[0] if 'Volume' in latest_data.columns else 0,
                                    'market_cap': info.get('marketCap'),
                                    'pe_ratio': info.get('trailingPE'),
                                    'dividend_yield': info.get('dividendYield'),
                                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                                    'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                                    'timestamp': datetime.now(),
                                    'source': 'Yahoo Finance (Batch)'
                                }
                                
                                stock_data_list.append(stock_data)
                                self._store_in_cache(symbol, stock_data)
                            
                    except Exception as e:
                        logger.warning(f"Error processing batch data for {symbol}: {e}")
                        # Fallback to individual request
                        individual_data = self.get_stock_info(symbol, force_refresh)
                        if individual_data:
                            stock_data_list.append(individual_data)
                
                # Data cached individually above
                
                if stock_data_list:
                    logger.info(f"Successfully fetched batch data for {len(stock_data_list)} symbols")
                    return pd.DataFrame(stock_data_list)
                    
            except Exception as e:
                logger.warning(f"Batch request failed: {e}. Falling back to individual requests.")
                return self.get_multiple_stocks(symbols, force_refresh)
                
        except Exception as e:
            logger.error(f"Error in batch request: {e}")
            return self.get_multiple_stocks(symbols, force_refresh)
        
        return pd.DataFrame()
    
    def get_multiple_stocks(self, symbols, force_refresh=False):
        """
        Get stock information for multiple symbols with improved rate limiting protection
        Arguments:
            symbols: List of Indian stock symbols
        Returns:
            DataFrame containing stock data for all symbols
        """
        stock_data_list = []
        
        for i, symbol in enumerate(symbols):
            stock_data = self.get_stock_info(symbol.upper().strip(), force_refresh)
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
        Arguments:
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
