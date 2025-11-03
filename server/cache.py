import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional
import config


def _key_to_path(key: str) -> Path:
	h = hashlib.sha1(key.encode('utf-8')).hexdigest()
	return config.CACHE_DIR / f"{h}.json"


def save_json(key: str, data: Any) -> None:
	"""Save `data` to cache under `key` (JSON)."""
	p = _key_to_path(key)
	payload = {
		"ts": time.time(),
		"data": data,
	}
	with p.open('w', encoding='utf-8') as f:
		json.dump(payload, f)


def load_json(key: str, max_age: Optional[int] = None) -> Optional[Any]:
	"""Load JSON data for key if cache exists and is not older than max_age seconds.

	Returns the original Python object or None when missing/expired.
	"""
	p = _key_to_path(key)
	if not p.exists():
		return None
	try:
		with p.open('r', encoding='utf-8') as f:
			payload = json.load(f)
		ts = float(payload.get('ts', 0))
		if max_age is not None and (time.time() - ts) > max_age:
			try:
				p.unlink()
			except Exception:
				pass
			return None
		return payload.get('data')
	except Exception:
		try:
			p.unlink()
		except Exception:
			pass
		return None


def clear_cache() -> None:
	"""Remove all cache files in CACHE_DIR."""
	for p in config.CACHE_DIR.glob('*.json'):
		try:
			p.unlink()
		except Exception:
			pass

