
from pathlib import Path

import numpy as np
import pandas as pd
from qiskit.circuit.library import zz_feature_map
from qiskit_machine_learning.algorithms import QSVC
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import RepeatedStratifiedKFold


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample.csv"

FEATURES = [
    "upfront_fee",
    "unverified_sender",
    "unrealistic_pay",
    "pressure_tactics",
    "missing_details",
]


def calculate_metrics(y_true, predictions):
    """Calculate evaluation metrics for model predictions."""
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "precision": float(
            precision_score(y_true, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, predictions, zero_division=0)
        ),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
    }


def evaluate_models():
    """Compare classical and quantum models using repeated cross-validation."""
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES].to_numpy(dtype=float)
    y = df["label"].to_numpy(dtype=int)

    cv = RepeatedStratifiedKFold(
        n_splits=3,
        n_repeats=3,
        random_state=42,
    )

    feature_map = zz_feature_map(
        feature_dimension=len(FEATURES),
        reps=1,
        entanglement="linear",
    )
    quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)

    fold_results = {"classical": [], "quantum": []}

    for train_indices, test_indices in cv.split(X, y):
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]

        classical = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight="balanced",
        )
        classical.fit(X_train, y_train)
        classical_predictions = classical.predict(X_test)

        quantum = QSVC(quantum_kernel=quantum_kernel)
        quantum.fit(X_train * np.pi, y_train)
        quantum_predictions = quantum.predict(X_test * np.pi)

        fold_results["classical"].append(
            calculate_metrics(y_test, classical_predictions)
        )
        fold_results["quantum"].append(
            calculate_metrics(y_test, quantum_predictions)
        )

    summary = {}

    for model_name, results in fold_results.items():
        summary[model_name] = {
            metric: {
                "mean": float(
                    np.mean([result[metric] for result in results])
                ),
                "std": float(
                    np.std([result[metric] for result in results])
                ),
            }
            for metric in ("accuracy", "precision", "recall", "f1")
        }

    return {
        "folds": len(fold_results["classical"]),
        "training_examples_per_fold": "Approximately 10–11",
        "test_examples_per_fold": "Approximately 5–6",
        "classical": summary["classical"],
        "quantum": summary["quantum"],
        "dataset_note": (
            "Evaluation uses 16 synthetic examples and repeated "
            "stratified cross-validation. Mean and standard deviation "
            "describe these splits only; they do not establish "
            "real-world scam-detection performance or quantum advantage."
        ),
    }


def main():
    results = evaluate_models()

    print("\nQuantumShield Model Comparison")
    print("=" * 40)
    print(results["dataset_note"])
    print(f"\nRepeated cross-validation folds: {results['folds']}")
    print(
        f"Training examples per fold: "
        f"{results['training_examples_per_fold']}"
    )
    print(
        f"Test examples per fold: {results['test_examples_per_fold']}"
    )

    for model_name, key in [
        ("Classical Random Forest", "classical"),
        ("Quantum Kernel SVM (Qiskit)", "quantum"),
    ]:
        print(f"\n{model_name}")

        for metric in ("accuracy", "precision", "recall", "f1"):
            values = results[key][metric]
            print(
                f"{metric.capitalize():10}: "
                f"{values['mean']:.3f} "
                f"(standard deviation: {values['std']:.3f})"
            )

    print(
        "\nThese results are exploratory and do not establish "
        "real-world detection performance or quantum advantage."
    )


if __name__ == "__main__":
    main()
