
from pathlib import Path

import numpy as np
import pandas as pd
from qiskit.circuit.library import zz_feature_map
from qiskit_machine_learning.algorithms import QSVC
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from sklearn.ensemble import RandomForestClassifier

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample.csv"

FEATURES = [
    "upfront_fee",
    "unverified_sender",
    "unrealistic_pay",
    "pressure_tactics",
    "missing_details",
]


def train_models():
    """Train both models using the synthetic development dataset."""
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES].to_numpy(dtype=float)
    y = df["label"].to_numpy(dtype=int)

    classical = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )
    classical.fit(X, y)

    feature_map = zz_feature_map(
        feature_dimension=len(FEATURES),
        reps=1,
        entanglement="linear",
    )
    quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)
    quantum = QSVC(quantum_kernel=quantum_kernel)
    quantum.fit(X * np.pi, y)

    return classical, quantum


def predict_opportunity(opportunity, classical, quantum):
    """Return predictions from both trained models for one opportunity."""
    values = np.array(
        [[opportunity[feature] for feature in FEATURES]],
        dtype=float,
    )

    classical_prediction = int(classical.predict(values)[0])
    quantum_prediction = int(quantum.predict(values * np.pi)[0])

    return {
        "classical_prediction": classical_prediction,
        "quantum_prediction": quantum_prediction,
        "label_meanings": {
            0: "Lower risk",
            1: "Higher risk",
        },
        "dataset_note": (
            "Models were trained on a small synthetic dataset. "
            "Predictions are experimental and are not verified scam classifications."
        ),
    }
