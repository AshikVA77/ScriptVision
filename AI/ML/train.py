import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# --------------------------------------------------
# Paths
# --------------------------------------------------

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "dataset"
)

DATA_PATH = os.path.join(
    DATASET_PATH,
    "answer_scores.csv"
)

MODEL_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    "model"
)

MODEL_PATH = os.path.join(
    MODEL_DIRECTORY,
    "mark_model.pkl"
)


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

data = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully.")
print("Number of samples:", len(data))


# --------------------------------------------------
# Features and Target
# --------------------------------------------------

features = [
    "similarity_score",
    "concept_accuracy",
    "answer_completeness",
    "diagram_correctness",
    "presentation",
    "maximum_marks"
]

X = data[features]
y = data["target_mark"]


# --------------------------------------------------
# Train-Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# --------------------------------------------------
# Create Random Forest Model
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    min_samples_leaf=2,
    random_state=42
)


# --------------------------------------------------
# Train Model
# --------------------------------------------------

model.fit(X_train, y_train)

print("\nModel training completed.")


# --------------------------------------------------
# Test Model
# --------------------------------------------------

predictions = model.predict(X_test)


# --------------------------------------------------
# Evaluation Metrics
# --------------------------------------------------

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5

r2 = r2_score(
    y_test,
    predictions
)

print("\nModel Performance")
print("-------------------------")
print("MAE :", round(mae, 4))
print("RMSE:", round(rmse, 4))
print("R²  :", round(r2, 4))


# --------------------------------------------------
# Save Model
# --------------------------------------------------

os.makedirs(
    MODEL_DIRECTORY,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

print("\nModel saved successfully.")
print("Location:", MODEL_PATH)