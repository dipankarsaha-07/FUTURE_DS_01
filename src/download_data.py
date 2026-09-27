import urllib.request
import os
import pandas as pd

RAW_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "raw", "Sample - Superstore.csv"
)

URLS = [
    "https://raw.githubusercontent.com/sumit0072/Superstore-Data-Analysis/main/Sample%20-%20Superstore.csv",
    "https://raw.githubusercontent.com/datasets/superstore/main/data/sample-superstore.csv",
    "https://raw.githubusercontent.com/Tiamiyu1/Sample-SuperStore-Sales-Data-Analysis/main/Sample%20-%20Superstore.csv"
]

def download_data():
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    success = False
    for url in URLS:
        try:
            print(f"Attempting to download from {url}...")
            urllib.request.urlretrieve(url, RAW_DATA_PATH)
            print("Download successful.")
            success = True
            break
        except Exception as e:
            print(f"Failed to download from {url}: {e}")

    if not success:
        raise RuntimeError("Unable to download dataset from any source URL.")

    try:
        df = pd.read_csv(RAW_DATA_PATH, encoding="windows-1252")
    except Exception:
        df = pd.read_csv(RAW_DATA_PATH, encoding="latin-1")

    print(f"Dataset successfully loaded. Shape: {df.shape}")
    print("Columns:", list(df.columns))
    print("\nFirst 3 rows:\n", df.head(3))

if __name__ == "__main__":
    download_data()
