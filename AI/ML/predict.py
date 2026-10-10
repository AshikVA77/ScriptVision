import os
import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model",
    "mark_model.pkl"
)


FEATURE_NAMES = [
    "similarity_score",
    "concept_accuracy",
    "answer_completeness",
    "diagram_correctness",
    "presentation",
    "maximum_marks"
]


def predict_marks(features, max_marks):

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "ML model has not been trained yet."
        )

    model = joblib.load(MODEL_PATH)

    # Create DataFrame with the same feature names
    # used during model training
    features = pd.DataFrame(
        [features],
        columns=FEATURE_NAMES
    )

    prediction = model.predict(features)[0]

    # Keep prediction within valid mark range
    prediction = max(
        0,
        min(prediction, max_marks)
    )

    # Round to the nearest 0.5 mark
    prediction = round(
        prediction * 2
    ) / 2

    return round(
        float(prediction),
        2
    )