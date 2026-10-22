
import streamlit as st
import pandas as pd

from src.input_processing import (
    extract_screenshot_text,
    extract_webpage_text,
    suggest_indicators,
)

from src.risk_assessment import assess_opportunity
from src.model_service import train_models, predict_opportunity
from src.compare_models import evaluate_models


st.set_page_config(
    page_title="QuantumShield",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ QuantumShield")
st.subheader("Explainable Opportunity Risk Assessment")
st.write(
    "Evaluate warning signs in jobs, internships, events, and webinars. "
    "Compare a classical machine-learning model with an experimental "
    "Qiskit quantum-kernel model."
)
st.info(
    "Research prototype: results are preliminary and do not prove an "
    "opportunity is genuine or fraudulent, or that quantum ML is superior."
)


st.header("Analyze a screenshot or webpage")

input_method = st.radio(
    "Choose your input",
    ["Manual entry", "Upload screenshot", "Paste webpage link"],
    horizontal=True,
)

extracted_text = ""

if input_method == "Upload screenshot":
    uploaded_image = st.file_uploader(
        "Upload an opportunity screenshot",
        type=["png", "jpg", "jpeg", "webp"],
    )

    if uploaded_image is not None:
        if st.button("Extract screenshot text"):
            try:
                st.session_state["extracted_text"] = (
                    extract_screenshot_text(uploaded_image)
                )
                st.session_state["source_text"] = (
                    " ".join(st.session_state["extracted_text"].split())
                )
                st.success("Screenshot text extracted.")
            except ValueError as exc:
                st.error(str(exc))

elif input_method == "Paste webpage link":
    webpage_url = st.text_input(
        "Public webpage URL",
        placeholder="https://example.com/opportunity",
    )

    if st.button("Extract webpage text"):
        try:
            st.session_state["extracted_text"] = (
                extract_webpage_text(webpage_url)
            )
            st.session_state["source_text"] = (
                " ".join(st.session_state["extracted_text"].split())
            )
            st.success("Webpage text extracted.")
        except ValueError as exc:
            st.error(str(exc))

if input_method != "Manual entry":
    extracted_text = st.session_state.get("extracted_text", "")

    if extracted_text:
        st.text_area(
            "Review extracted text",
            value=extracted_text,
            height=180,
            key="review_extracted_text",
        )

        if st.button("Suggest warning indicators"):
            st.session_state["suggested_indicators"] = (
                suggest_indicators(extracted_text)
            )
            st.success(
                "Suggestions ready. Review them in the assessment form below."
            )


st.write(
    "Review warning signs in jobs, internships, webinars, "
    "and student competitions."
)

st.warning(
    "Experimental prototype: warnings and model predictions are not "
    "proof of fraud. Models are trained on a small synthetic dataset."
)


@st.cache_resource
def load_models():
    return train_models()


st.header("Assess an opportunity")

suggested = st.session_state.get("suggested_indicators", {})

if input_method != "Manual entry" and suggested:
    st.subheader("Review suggested warning indicators")
    st.caption(
        "These are keyword-based suggestions. Review and change them "
        "before submitting the assessment."
    )

    use_suggestions = st.checkbox(
        "Use the suggested indicators as my starting values",
        value=True,
    )
else:
    use_suggestions = False

with st.form("opportunity_form"):
    
    upfront_fee = st.selectbox(
        "Does it request an upfront payment?",
        ["No", "Yes"],
        index=(
            suggested.get("upfront_fee", 0)
            if use_suggestions else 0
        ),
    )
    unverified_sender = st.selectbox(
        "Is the sender's identity unverified?",
        ["No", "Yes"],
        index=(
            suggested.get("unverified_sender", 0)
            if use_suggestions else 0
        ),
    )
    unrealistic_pay = st.selectbox(
        "Does the advertised pay or reward seem unrealistic?",
        ["No", "Yes"],
        index=(
            suggested.get("unrealistic_pay", 0)
            if use_suggestions else 0
        ),
    )
    pressure_tactics = st.selectbox(
        "Does the message pressure you to act urgently?",
        ["No", "Yes"],
        index=(
            suggested.get("pressure_tactics", 0)
            if use_suggestions else 0
        ),
    )
    missing_details = st.selectbox(
        "Are important details missing?",
        ["No", "Yes"],
        index=(
            suggested.get("missing_details", 0)
            if use_suggestions else 0
        ),
    )


    submitted = st.form_submit_button("Assess opportunity")


if submitted:
    opportunity = {
        "upfront_fee": int(upfront_fee == "Yes"),
        "unverified_sender": int(unverified_sender == "Yes"),
        "unrealistic_pay": int(unrealistic_pay == "Yes"),
        "pressure_tactics": int(pressure_tactics == "Yes"),
        "missing_details": int(missing_details == "Yes"),
    }

    # Explainable, rule-based warning assessment
    result = assess_opportunity(opportunity)

    st.header("Warning-sign assessment")
    st.metric("Warning signs identified", result["warning_count"])
    st.subheader(result["assessment"])

    if result["warnings"]:
        for warning in result["warnings"]:
            st.warning(warning)
    else:
        st.success(
            "No warning signs were selected. This does not guarantee safety."
        )

    st.caption(result["disclaimer"])
    st.divider()
    st.header("Machine-learning experiment")

    with st.spinner("Running classical and quantum models..."):
        classical, quantum = load_models()
        predictions = predict_opportunity(
            opportunity, classical, quantum
        )

    classical_label = predictions["label_meanings"][
        predictions["classical_prediction"]
    ]
    quantum_label = predictions["label_meanings"][
        predictions["quantum_prediction"]
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Classical ML")
        st.metric("Random Forest output", classical_label)

    with col2:
        st.subheader("Quantum ML — Qiskit")
        st.metric("Quantum Kernel SVM output", quantum_label)

    st.divider()
    st.subheader("Model agreement")

    if (
        predictions["classical_prediction"]
        == predictions["quantum_prediction"]
    ):
        st.success(f"Both models agree: {classical_label}.")
    else:
        st.warning(
            "The models disagree. Review the warning signs and "
            "verify the opportunity independently."
        )

    st.dataframe(
        pd.DataFrame(
            {
                "Model": [
                    "Classical Random Forest",
                    "Quantum Kernel SVM (Qiskit)",
                ],
                "Prediction": [classical_label, quantum_label],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.info(predictions["dataset_note"])

    st.caption(
        "Agreement does not prove a prediction is correct. "
        "These are experimental labels, not calibrated probabilities."
    )



# Model evaluation dashboard
st.divider()
st.header("Model Evaluation Dashboard")

st.write(
    "Compare the classical and quantum models using repeated "
    "stratified cross-validation."
)

if st.button("Run Model Evaluation"):
    with st.spinner("Evaluating both models across nine folds..."):
        evaluation = evaluate_models()

    st.warning(evaluation["dataset_note"])

    st.metric("Evaluation folds", evaluation["folds"])

    st.caption(
        f"Training examples per fold: "
        f"{evaluation['training_examples_per_fold']} | "
        f"Test examples per fold: "
        f"{evaluation['test_examples_per_fold']}"
    )

    # Display mean scores in a comparison chart.
    st.subheader("Mean Metric Comparison")

    chart_data = pd.DataFrame(
        {
            "Metric": ["Accuracy", "Precision", "Recall", "F1 score"],
            "Classical Random Forest": [
                evaluation["classical"][metric]["mean"]
                for metric in ("accuracy", "precision", "recall", "f1")
            ],
            "Quantum Kernel SVM (Qiskit)": [
                evaluation["quantum"][metric]["mean"]
                for metric in ("accuracy", "precision", "recall", "f1")
            ],
        }
    ).set_index("Metric")

    st.bar_chart(chart_data, y_label="Mean score")

    # Display mean and standard deviation for each model.
    model_columns = st.columns(2)

    models = [
        ("Classical Random Forest", "classical"),
        ("Quantum Kernel SVM (Qiskit)", "quantum"),
    ]

    for column, (model_name, model_key) in zip(model_columns, models):
        metrics = evaluation[model_key]

        with column:
            st.subheader(model_name)

            for metric in ("accuracy", "precision", "recall", "f1"):
                values = metrics[metric]
                st.metric(
                    metric.capitalize(),
                    f"{values['mean']:.1%}",
                    help=(
                        f"Standard deviation across the evaluation folds: "
                        f"{values['std']:.1%}"
                    ),
                )
                st.caption(
                    f"Standard deviation: {values['std']:.1%}"
                )

    st.info(
        "Interpretation: the classical model had higher mean accuracy "
        "and precision in this experiment. The quantum model had higher "
        "mean recall and F1 score. These results are exploratory only; "
        "the small synthetic dataset cannot establish real-world "
        "detection performance or quantum advantage."
    )
