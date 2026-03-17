"""Create a starter url,label CSV template.

This is useful when you collect phishing URLs (e.g., PhishTank export)
and legit URLs (e.g., Tranco top sites list).

Usage:
  python scripts/make_url_dataset_template.py --out data/urls.csv
"""
import argparse
from pathlib import Path
import csv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/urls.csv")
    args = ap.parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    rows = [
        ("https://example.com", 0),
        ("https://accounts.example.com/login", 0),
        ("http://paypal.verify-secure-login.example.net/confirm", 1),
    ]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "label"])
        w.writerows(rows)
    print(f"Wrote template dataset -> {args.out}")

if __name__ == "__main__":
    main()
