import os
from pathlib import Path
from dotenv import load_dotenv


# API Configuration
load_dotenv()
TWELVE_DATA_API_KEY = os.environ.get('TWELVE_DATA_API_KEY')
TWELVE_DATA_BASE_URL = 'https://api.twelvedata.com'

# Cache Configuration
CACHE_DIR = Path.home() / '.stock_mcp_cache'
CACHE_DIR.mkdir(exist_ok=True)

# Cache expiration times (in seconds)
CACHE_QUOTE_EXPIRY = 900  
CACHE_FUNDAMENTALS_EXPIRY = 86400  
CACHE_HISTORICAL_EXPIRY = 3600  

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 8  
REQUEST_DELAY = 0.5  
# Data settings
DEFAULT_INTERVAL = '1day'
DEFAULT_OUTPUTSIZE = 30  

# Supported exchanges
SUPPORTED_EXCHANGES = ['NYSE', 'NASDAQ', 'AMEX']