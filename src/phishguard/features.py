import re
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import urlparse

IP_REGEX = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
HEX_IP_REGEX = re.compile(r"0x[0-9a-fA-F]{2,}")
SUSPICIOUS_WORDS = (
    "login", "secure", "account", "update", "verify", "bank", "free", "bonus",
    "confirm", "signin", "sign-in", "password", "ebayisapi", "webscr", "paypal"
)

def _safe_urlparse(url: str):
    # If user passes "example.com" without scheme, urlparse treats it as path.
    # Add scheme to normalize.
    if "://" not in url:
        url = "http://" + url
    return urlparse(url)

def _has_ip(host: str) -> int:
    host = host.strip("[]")
    if IP_REGEX.match(host):
        parts = host.split(".")
        try:
            return 1 if all(0 <= int(p) <= 255 for p in parts) else 0
        except ValueError:
            return 0
    # crude hex/ip patterns
    if HEX_IP_REGEX.search(host):
        return 1
    return 0

def _count(pattern: str, s: str) -> int:
    return len(re.findall(pattern, s))

def extract_url_features(url: str) -> Dict[str, float]:
    """Extract practical URL-based features.
    This is intentionally lightweight (no network calls).
    """
    parsed = _safe_urlparse(url.strip())
    host = parsed.netloc.lower()
    path = parsed.path or ""
    query = parsed.query or ""
    full = (parsed.geturl() or url).lower()

    # If netloc still empty (e.g., 'example.com' parsed as path), attempt fallback.
    if not host:
        # urlparse("http://example.com") would have netloc, but keep safe
        tmp = _safe_urlparse("http://" + url.strip())
        host = tmp.netloc.lower()
        path = tmp.path or ""
        query = tmp.query or ""
        full = (tmp.geturl() or url).lower()

    # Domain pieces
    host_parts = [p for p in host.split(".") if p]
    tld_len = float(len(host_parts[-1])) if host_parts else 0.0
    subdomain_len = float(sum(len(p) for p in host_parts[:-2])) if len(host_parts) > 2 else 0.0
    domain_len = float(len(host))

    # Ratios
    digits = sum(ch.isdigit() for ch in full)
    letters = sum(ch.isalpha() for ch in full)
    total = max(len(full), 1)
    digit_ratio = digits / total
    letter_ratio = letters / total

    suspicious = 0
    for w in SUSPICIOUS_WORDS:
        if w in full:
            suspicious += 1

    features = {
        "url_length": float(len(full)),
        "hostname_length": domain_len,
        "path_length": float(len(path)),
        "query_length": float(len(query)),
        "has_ip": float(_has_ip(host)),
        "count_dots": float(full.count(".")),
        "count_hyphen": float(full.count("-")),
        "count_at": float(full.count("@")),
        "count_question": float(full.count("?")),
        "count_and": float(full.count("&")),
        "count_equal": float(full.count("=")),
        "count_underscore": float(full.count("_")),
        "count_slash": float(full.count("/")),
        "count_colon": float(full.count(":")),
        "count_comma": float(full.count(",")),
        "count_semicolon": float(full.count(";")),
        "count_percent": float(full.count("%")),
        "count_tilde": float(full.count("~")),
        "count_www": float(full.count("www")),
        "count_http": float(full.count("http")),
        "https_token": float(1 if "https" in full else 0),
        "tld_length": tld_len,
        "subdomain_length": subdomain_len,
        "digit_ratio": float(digit_ratio),
        "letter_ratio": float(letter_ratio),
        "suspicious_word_count": float(suspicious),
    }
    return features

def feature_names() -> List[str]:
    # Keep a stable ordering for model training/inference
    return list(extract_url_features("http://example.com").keys())
