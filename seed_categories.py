"""Fill the categories table with the queues the model was trained on, and the team that handles each."""
import pandas as pd
from db import get_db

queues = sorted(pd.read_csv("data/tickets.csv", dtype=str)["category"].dropna().unique())

conn = get_db()
for name in queues:
    # INSERT OR IGNORE: running this script twice does not create duplicates
    conn.execute("INSERT OR IGNORE INTO categories (name, team) VALUES (?, ?)", (name, name + " Team"))
conn.commit()
for row in conn.execute("SELECT name, team FROM categories ORDER BY name"):
    print(row["name"], "->", row["team"])
conn.close()