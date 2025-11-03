import time
import requests
from typing import Any, Dict

import config
import cache


def _require_api_key() -> str:
	if not config.TWELVE_DATA_API_KEY:
		raise RuntimeError('TWELVE_DATA_API_KEY environment variable is not set. Set it in a .env or environment.')
	return config.TWELVE_DATA_API_KEY


def _call_api(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
	key = _require_api_key()
	params = dict(params)
	params['apikey'] = key
	url = f"{config.TWELVE_DATA_BASE_URL}/{path}"
	time.sleep(config.REQUEST_DELAY)
	resp = requests.get(url, params=params, timeout=15)
	resp.raise_for_status()
	data = resp.json()
	if isinstance(data, dict) and data.get('code'):
		raise RuntimeError(f"TwelveData API error: {data}")
	return data


def get_quote(symbol: str) -> Dict[str, Any]:
	"""Return latest quote JSON for symbol. Uses cache."""
	key = f"quote:{symbol.upper()}"
	cached = cache.load_json(key, max_age=config.CACHE_QUOTE_EXPIRY)
	if cached is not None:
		return cached
	data = _call_api('quote', {'symbol': symbol.upper()})
	cache.save_json(key, data)
	return data


def get_historical(symbol: str, interval: str = None, outputsize: int = None) -> Dict[str, Any]:
	"""Return time series data from TwelveData (values list sorted newest-first).

	Returns the raw JSON response from the API.
	"""
	interval = interval or config.DEFAULT_INTERVAL
	outputsize = outputsize or config.DEFAULT_OUTPUTSIZE
	key = f"historical:{symbol.upper()}:{interval}:{outputsize}"
	cached = cache.load_json(key, max_age=config.CACHE_HISTORICAL_EXPIRY)
	if cached is not None:
		return cached
	params = {
		'symbol': symbol.upper(),
		'interval': interval,
		'outputsize': outputsize,
		'format': 'JSON',
	}
	data = _call_api('time_series', params)
	cache.save_json(key, data)
	return data

