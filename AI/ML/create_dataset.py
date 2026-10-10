import os
import numpy as np
import pandas as pd


# --------------------------------------------------
# Paths
# --------------------------------------------------

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "dataset"
)

MARKS_PATH = os.path.join(
    DATASET_PATH,
    "Teacher_manual_marks_Anonymized.csv"
)

OUTPUT_PATH = os.path.join(
    DATASET_PATH,
    "answer_scores.csv"
)


# --------------------------------------------------
# Random Generator
# --------------------------------------------------

rng = np.random.default_rng(42)


# --------------------------------------------------
# Number of Synthetic Variations
# --------------------------------------------------

VARIATIONS_PER_RECORD = 5


# --------------------------------------------------
# Load Teacher Marks
# --------------------------------------------------

marks_data = pd.read_csv(
    MARKS_PATH
)


# --------------------------------------------------
# Maximum Marks Options
# --------------------------------------------------

maximum_marks_options = [
    2,
    3,
    4,
    5,
    6
]


# --------------------------------------------------
# Exam Total Options
# --------------------------------------------------

exam_total_options = [
    20,
    30,
    40,
    50,
    80,
    100
]


# --------------------------------------------------
# Create Dataset
# --------------------------------------------------

rows = []


for _, student in marks_data.iterrows():

    student_id = student["Student_ID"]

    for question_number in range(21, 36):

        mark = student[str(question_number)]

        # Skip missing / NC marks
        if pd.isna(mark):
            continue

        try:
            original_mark = float(mark)

        except (ValueError, TypeError):
            continue

        if original_mark < 0 or original_mark > 2:
            continue


        # ------------------------------------------
        # Original question is 2 marks
        # ------------------------------------------

        original_max_marks = 2


        # ------------------------------------------
        # Convert teacher mark to quality ratio
        # ------------------------------------------

        quality = (
            original_mark /
            original_max_marks
        )


        # ------------------------------------------
        # Generate Multiple Variations
        # ------------------------------------------

        for variation in range(
            VARIATIONS_PER_RECORD
        ):

            # --------------------------------------
            # Randomly assign development max marks
            # --------------------------------------

            maximum_marks = int(
                rng.choice(
                    maximum_marks_options
                )
            )


            # --------------------------------------
            # Randomly assign exam total
            # --------------------------------------

            exam_total_marks = int(
                rng.choice(
                    exam_total_options
                )
            )


            # --------------------------------------
            # Generate Features
            # --------------------------------------

            similarity_score = (
                25
                + quality * 70
                + rng.normal(0, 7)
            )


            concept_accuracy = (
                quality
                + rng.normal(0, 0.08)
            )


            answer_completeness = (
                quality
                + rng.normal(0, 0.10)
            )


            presentation = (
                0.55
                + quality * 0.35
                + rng.normal(0, 0.08)
            )


            diagram_correctness = rng.uniform(
                0.0,
                0.15
            )


            # --------------------------------------
            # Clip Feature Values
            # --------------------------------------

            similarity_score = np.clip(
                similarity_score,
                0,
                100
            )


            concept_accuracy = np.clip(
                concept_accuracy,
                0,
                1
            )


            answer_completeness = np.clip(
                answer_completeness,
                0,
                1
            )


            presentation = np.clip(
                presentation,
                0,
                1
            )


            # --------------------------------------
            # Scale Teacher Mark
            # --------------------------------------

            target_mark = (
                quality *
                maximum_marks
            )


            # --------------------------------------
            # Keep Marks in 0.5 Increments
            # --------------------------------------

            target_mark = (
                round(target_mark * 2) / 2
            )


            # --------------------------------------
            # Prevent Exceeding Maximum
            # --------------------------------------

            target_mark = max(
                0,
                min(
                    target_mark,
                    maximum_marks
                )
            )


            # --------------------------------------
            # Store Row
            # --------------------------------------

            rows.append({

                "student_id":
                    student_id,

                "question_number":
                    question_number,

                "similarity_score":
                    round(
                        similarity_score,
                        2
                    ),

                "concept_accuracy":
                    round(
                        concept_accuracy,
                        2
                    ),

                "answer_completeness":
                    round(
                        answer_completeness,
                        2
                    ),

                "diagram_correctness":
                    round(
                        diagram_correctness,
                        2
                    ),

                "presentation":
                    round(
                        presentation,
                        2
                    ),

                "maximum_marks":
                    maximum_marks,

                "exam_total_marks":
                    exam_total_marks,

                "target_mark":
                    target_mark
            })


# --------------------------------------------------
# Create DataFrame
# --------------------------------------------------

data = pd.DataFrame(
    rows
)


# --------------------------------------------------
# Shuffle Dataset
# --------------------------------------------------

data = data.sample(
    frac=1,
    random_state=42
).reset_index(
    drop=True
)


# --------------------------------------------------
# Save Dataset
# --------------------------------------------------

data.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------------------------
# Display Information
# --------------------------------------------------

print(
    "Dataset created successfully."
)

print(
    "\nVariations per original record:"
)

print(
    VARIATIONS_PER_RECORD
)

print(
    "\nNumber of training samples:"
)

print(
    len(data)
)


print(
    "\nDataset preview:"
)

print(
    data.head(10)
)


print(
    "\nMaximum mark distribution:"
)

print(
    data["maximum_marks"]
    .value_counts()
    .sort_index()
)


print(
    "\nExam total mark distribution:"
)

print(
    data["exam_total_marks"]
    .value_counts()
    .sort_index()
)


print(
    "\nTarget mark distribution:"
)

print(
    data["target_mark"]
    .value_counts()
    .sort_index()
)


print(
    "\nSaved to:"
)

print(
    OUTPUT_PATH
)