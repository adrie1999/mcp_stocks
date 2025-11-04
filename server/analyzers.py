from typing import List, Dict, Any, Optional
from pypfopt.hierarchical_portfolio import HRPOpt
import numpy as np
import pandas as pd
import data_fetcher


def _ts_to_series(ts_json: Dict[str, Any]) -> pd.Series:
	values = ts_json.get('values', [])
	if not values:
		return pd.Series(dtype=float)
	df = pd.DataFrame(values)

	if 'datetime' in df.columns:
		idx = df['datetime']
	elif 'timestamp' in df.columns:
		idx = df['timestamp']
	else:
		idx = df.index
	df.index = pd.to_datetime(idx)
	s = pd.to_numeric(df['close'], errors='coerce')
	s = s.sort_index()  
	s.name = ts_json.get('symbol') or ''
	return s


def compare_symbols(symbols: List[str], interval: Optional[str] = None, outputsize: Optional[int] = None) -> Dict[str, Any]:
	"""Fetch historical data for `symbols` and return comparison metrics.

	Returns a dict with:
	  - 'metrics': per-symbol metrics (latest, cumulative_return, volatility, sharpe, var_95)
	  - 'correlation': correlation matrix of returns
	"""
	series_map = {}
	for sym in symbols:
		ts = data_fetcher.get_historical(sym, interval=interval, outputsize=outputsize)
		if 'status' in ts and ts.get('status') == 'error':
			raise RuntimeError(f"Error fetching {sym}: {ts}")
		s = _ts_to_series(ts)
		s.name = sym.upper()
		series_map[sym.upper()] = s

	if not series_map:
		return {}

	prices = pd.concat(series_map.values(), axis=1, join='outer')
	prices.columns = [c.upper() for c in prices.columns]
	prices = prices.dropna(how='all')

	returns = prices.pct_change().dropna(how='all')

	metrics: Dict[str, Dict[str, Optional[float]]] = {}
	for col in prices.columns:
		col_prices = prices[col].dropna()
		if col_prices.empty:
			metrics[col] = {
				'latest': None,
				'cumulative_return': None,
				'volatility': None,
				'sharpe': None,
				'var_95': None,
			}
			continue
		latest = float(col_prices.iloc[-1])
		first = float(col_prices.iloc[0])
		cum_return = (latest / first) - 1.0 if first != 0 else None
		r = returns[col].dropna()
		mean = float(r.mean()) if not r.empty else 0.0
		std = float(r.std(ddof=0)) if not r.empty else 0.0

		volatility = std * np.sqrt(252) if std and interval in (None, '1day', '1D', '1d') else std
		sharpe = (mean / std) if std and std != 0 else None
		

		var_95 = float(np.percentile(r, 5)) if not r.empty else None
		
		metrics[col] = {
			'latest': latest,
			'cumulative_return': cum_return,
			'volatility': float(volatility) if volatility is not None else None,
			'sharpe': float(sharpe) if sharpe is not None else None,
			'var_95': var_95,
		}

	corr = returns.corr().fillna(0.0)


	corr_out = corr.round(4).to_dict()

	return {
		'metrics': metrics,
		'correlation': corr_out,
	}


def hierarchical_risk_parity_portfolio(symbols: List[str], interval: Optional[str] = None, outputsize: Optional[int] = None) -> Dict[str, float]:
	"""
	Compute Hierarchical Risk Parity (HRP) weights for a portfolio of stocks.
	
	Uses the pypfopt library's HRPOpt implementation which:
	1. Clusters assets based on correlation distance
	2. Builds a hierarchical tree (dendrogram)
	3. Allocates risk equally across branches, then recursively down
	
	Args:
		symbols: List of stock ticker symbols (e.g., ['AAPL', 'MSFT', 'TSLA'])
		interval: Time interval for historical data (default: None for daily)
		outputsize: Number of historical data points to fetch
	
	Returns:
		Dictionary mapping ticker symbols to their optimal HRP weights
		Example: {'AAPL': 0.35, 'MSFT': 0.40, 'TSLA': 0.25}
	"""	
	# Fetch historical data for all symbols
	series_map = {}
	for sym in symbols:
		ts = data_fetcher.get_historical(sym, interval=interval, outputsize=outputsize)
		if 'status' in ts and ts.get('status') == 'error':
			raise RuntimeError(f"Error fetching {sym}: {ts}")
		s = _ts_to_series(ts)
		s.name = sym.upper()
		series_map[sym.upper()] = s
	
	if not series_map:
		return {}
	
	prices = pd.concat(series_map.values(), axis=1, join='outer')
	prices.columns = [c.upper() for c in prices.columns]
	prices = prices.dropna(how='all')
	
	returns = prices.pct_change().dropna(how='all')
	
	if returns.empty or returns.shape[1] < 2:
		return {sym: 1.0 / len(symbols) for sym in symbols}
	
	hrp = HRPOpt(returns=returns)
	
	weights = hrp.optimize()
	
	hrp_weights = {
		ticker: float(weight) 
		for ticker, weight in weights.items()
	}
	
	return hrp_weights