"""Loads the trained model once and suggests a category and priority for new tickets."""
from pathlib import Path
import joblib

MODEL_FILE = Path(__file__).resolve().parent / "models" / "ticket_model.joblib"
MIN_CONFIDENCE = 0.5   # below this, the suggestion is NOT applied to the ticket

# Load once when the app starts. (Only ever load model files you trained yourself.)
bundle = joblib.load(MODEL_FILE) if MODEL_FILE.is_file() else None

def predict(text):
    result = {"category": None, "priority": None,
              "category_score": None, "priority_score": None, "model_version": "no-model"}
    if bundle is None:                       # no model trained yet: everything goes to manual review
        return result
    result["model_version"] = bundle["version"]
    for target in ["category", "priority"]:
        model = bundle[target]
        probabilities = model.predict_proba([text])[0]   # one probability per label, adding up to 1
        best = probabilities.argmax()                    # position of the most likely label
        result[target] = str(model.classes_[best])
        result[target + "_score"] = float(probabilities[best])
    return result

# ---- Automatic priority ----
# Keyword rules back up the model: the model only knows Low/Medium/High and is often unsure,
# so every ticket still gets a priority. Checked in this order; the first match wins.
PRIORITY_RULES = [
    ("Critical", ["outage", "server down", "system down", "site down", "network down", " is down", " are down", "went down", "everyone", "nobody can",
                  "all users", "whole office", "entire", "data loss", "lost data", "ransomware", "virus",
                  "hacked", "breach", "security incident", "phishing"]),
    ("High", ["urgent", "asap", "immediately", "cannot", "can't", "cant ", "unable", "not working", "doesn't work",
              "won't", "failed", "failing", "error", "crash", "locked out", "charged twice",
              "billed twice", "refund", "deadline"]),
    ("Low", ["question", "how do i", "how to", "request access", "new account", "feature", "suggestion",
             "minor", "when possible", "no rush", "information", "inquiry"]),
]


def keyword_priority(text):
    lowered = " " + text.lower() + " "
    for priority, words in PRIORITY_RULES:
        if any(word in lowered for word in words):
            return priority
    return None


def auto_priority(text, prediction):
    """Always returns a priority and where it came from: 'model', 'rules' or 'default'."""
    rule = keyword_priority(text)
    if rule == "Critical":                                  # the model cannot predict Critical
        return "Critical", "rules"
    if prediction["priority"] and (prediction["priority_score"] or 0) >= MIN_CONFIDENCE:
        return prediction["priority"], "model"
    if rule:
        return rule, "rules"
    if prediction["priority"]:                              # unsure, but still the model's best guess
        return prediction["priority"], "model"
    return "Medium", "default"
