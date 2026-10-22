
from pathlib import Path

import numpy as np
import pandas as pd
from qiskit.circuit.library import zz_feature_map
from qiskit_aer import AerSimulator
from qiskit_machine_learning.algorithms import QSVC
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sample.csv"

FEATURES = [
    "upfront_fee",
    "unverified_sender",
    "unrealistic_pay",
    "pressure_tactics",
    "missing_details",
]


def main():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES].to_numpy(dtype=float)
    y = df["label"].to_numpy(dtype=int)

    # Scale binary features to the range [0, pi] for angle encoding.
    X = X * np.pi

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    feature_map = zz_feature_map(
        feature_dimension=len(FEATURES),
        reps=1,
        entanglement="linear",
    )

    # Use a local Qiskit Aer simulator; no cloud account is needed.
    simulator = AerSimulator()

    quantum_kernel = FidelityQuantumKernel(
        feature_map=feature_map,
        fidelity=None,
    )

    model = QSVC(quantum_kernel=quantum_kernel)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print("QuantumShield — Quantum Kernel SVM")
    print("Dataset: synthetic development examples")
    print(f"Simulator available: {simulator.name}")
    print(f"Training rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    print(f"Test accuracy: {accuracy_score(y_test, predictions):.2f}")


if __name__ == "__main__":
    main()
