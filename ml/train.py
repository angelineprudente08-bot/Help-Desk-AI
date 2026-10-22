"""ML step 2: train two TF-IDF + Logistic Regression models (category and priority)."""
import json
from datetime import datetime
from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATA = "data/tickets.csv"
MODEL_FILE = "models/ticket_model.joblib"

data = pd.read_csv(DATA, dtype=str).fillna("")
text = data["title"] + "\n" + data["description"]   # the model reads title + description together

bundle = {"version": datetime.now().strftime("%Y%m%d-%H%M%S")}
metrics = {}

for target in ["category", "priority"]:
    # 80% of tickets to learn from, 20% kept hidden to test on.
    # stratify keeps the same mix of labels in both parts; random_state makes the split repeatable.
    x_train, x_test, y_train, y_test = train_test_split(
        text, data[target], test_size=0.2, random_state=42, stratify=data[target]
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, max_features=50000)),
        ("classifier", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42)),
    ])
    model.fit(x_train, y_train)               # learning happens here
    predicted = model.predict(x_test)         # guess the hidden 20%

    report = classification_report(y_test, predicted, output_dict=True, zero_division=0)
    metrics[target] = report
    bundle[target] = model

    print(f"\n===== {target.upper()} model =====")
    print(f"Trained on {len(x_train)} tickets, tested on {len(x_test)} tickets")
    print(classification_report(y_test, predicted, zero_division=0))
    print(f"{target} macro-F1: {report['macro avg']['f1-score']:.3f}")

Path("models").mkdir(exist_ok=True)
joblib.dump(bundle, MODEL_FILE)
Path("models/ticket_model.metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print("\nSaved", MODEL_FILE, "and models/ticket_model.metrics.json")