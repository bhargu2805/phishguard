"""Convert the UCI 'Phishing Websites' ARFF dataset to a URL+label CSV.

Notes:
- The classic UCI phishing dataset doesn't contain raw URLs; it contains engineered features.
- For this project (URL-based feature extraction), you need a dataset WITH urls.
- This converter is included because many students download the ARFF by default.
  It will output a feature CSV (no urls) if that's what you have.

If you want a URL dataset:
  - PhishTank (phishing URLs)
  - Tranco / Majestic top sites (legit URLs)
Then create a CSV: url,label and train.

Usage:
  python scripts/uci_arff_to_csv.py --arff data/phishing.arff --out data/uci_phishing_features.csv
"""
import argparse
from pathlib import Path

import pandas as pd
from scipy.io import arff

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arff", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data, meta = arff.loadarff(args.arff)
    df = pd.DataFrame(data)

    # Decode bytes columns
    for c in df.columns:
        if df[c].dtype == object and len(df) and isinstance(df[c].iloc[0], (bytes, bytearray)):
            df[c] = df[c].str.decode("utf-8")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with shape {df.shape}")

if __name__ == "__main__":
    main()
