"""ML step 1: turn the Kaggle CSV into a clean training file."""
from pathlib import Path
import pandas as pd

INPUT = "data/raw/dataset-tickets-multi-lang-4-20k.csv"
OUTPUT = "data/tickets.csv"
PRIORITY_MAP = {"low": "Low", "medium": "Medium", "high": "High", "critical": "Critical"}
MIN_PER_CATEGORY = 5

raw = pd.read_csv(INPUT, dtype=str).fillna("")
print("Rows in the Kaggle file:", len(raw))

english = raw[raw["language"].str.strip().str.lower() == "en"]
print("English rows:", len(english))

unknown = set(english["priority"].str.strip().str.lower()) - set(PRIORITY_MAP)
if unknown:
    raise SystemExit(f"Unknown priority values {unknown}. Add them to PRIORITY_MAP first.")

# keep only the 4 columns we need, renamed to our app's names (the 'answer' column is never used)
data = pd.DataFrame({
    "title": english["subject"].str.strip(),
    "description": english["body"].str.strip(),
    "category": english["queue"].str.strip(),
    "priority": english["priority"].str.strip().str.lower().map(PRIORITY_MAP),
})
data = data[(data["description"] != "") & (data["category"] != "")]

# the same ticket text with different labels: we can't know which label is right, so drop it
key = (data["title"] + " " + data["description"]).str.lower().str.split().str.join(" ")
conflicting = data.groupby(key)[["category", "priority"]].transform("nunique").max(axis=1) > 1
print("Rows removed (same text, different labels):", int(conflicting.sum()))
data, key = data[~conflicting], key[~conflicting]

# exact duplicates would let the model "cheat" if one copy lands in training and one in testing
before = len(data)
data = data[~key.duplicated()]
print("Duplicate rows removed:", before - len(data))

# a queue with fewer than 5 tickets is too small to learn from or to test fairly
counts = data["category"].value_counts()
too_small = list(counts[counts < MIN_PER_CATEGORY].index)
data = data[~data["category"].isin(too_small)]
print("Queues removed (fewer than 5 tickets):", too_small)

Path("data").mkdir(exist_ok=True)
data.to_csv(OUTPUT, index=False)
print("Final rows:", len(data))
print("\nTickets per category:\n" + data["category"].value_counts().to_string())
print("\nTickets per priority:\n" + data["priority"].value_counts().to_string())
print("\nSaved", OUTPUT)