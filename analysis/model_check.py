"""Score the no-show model on the generated training data it uses, and write docs/model_check.json.

services/ml_service.py trains on 1,000 generated appointments when no real history exists.
Run from the repo root:  python analysis/model_check.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "services" / "ml_service.py").read_text()
a = src.index("    def create_training_data(self):")
b = src.index("    def train_model", a)
ns = {"np": np, "pd": pd}
exec("\n".join(line[4:] for line in src[a:b].splitlines()), ns)  # the generator exactly as the app runs it
df = ns["create_training_data"](None)

X, y = df.drop(columns="no_show"), df.no_show
model = RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=5, min_samples_leaf=2,
                               random_state=42, class_weight="balanced")
cv = StratifiedKFold(5, shuffle=True, random_state=42)
out = {
    "rows": int(len(df)),
    "no_show_rate": round(float(y.mean()), 3),
    "majority_accuracy": round(float(1 - y.mean()), 3),
    "accuracy": round(float(cross_val_score(model, X, y, cv=cv).mean()), 3),
    "auc": round(float(cross_val_score(model, X, y, cv=cv, scoring="roc_auc").mean()), 3),
    "recall": round(float(cross_val_score(model, X, y, cv=cv, scoring="recall").mean()), 3),
}
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "model_check.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
