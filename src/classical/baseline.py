
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sample.csv"

FEATURES = [
    "upfront_fee",
    "unverified_sender",
    "unrealistic_pay",
    "pressure_tactics",
    "missing_details",
]


def load_data():
    """Load and validate the synthetic development dataset."""
    df = pd.read_csv(DATA_PATH)

    required_columns = FEATURES + ["label"]
    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")

    if df[required_columns].isna().any().any():
        raise ValueError("Dataset contains missing values.")

    if not set(df["label"].unique()).issubset({0, 1}):
        raise ValueError("Labels must be 0 or 1.")

    return df


def main():
    df = load_data()
    X = df[FEATURES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("QuantumShield — Classical ML Baseline")
    print("Dataset: synthetic development examples")
    print(f"Training rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    print(f"Test accuracy: {accuracy_score(y_test, predictions):.2f}")
    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=["Lower risk (synthetic)", "Higher risk (synthetic)"],
            zero_division=0,
        )
    )

    print("Feature importance (exploratory only):")
    for name, importance in sorted(
        zip(FEATURES, model.feature_importances_),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"  {name}: {importance:.3f}")


if __name__ == "__main__":
    main()
