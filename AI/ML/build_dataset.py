import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

import pandas as pd
import fitz

from AI.preprocess import preprocess_image
from AI.ocr import extract_text
from AI.similarity import calculate_similarity
from AI.evaluator import evaluate_answer


# -----------------------------------
# Paths
# -----------------------------------

DATASET_PATH = r"E:\Main Project\ScriptVision\AI\dataset"

PDF_PATH = os.path.join(
    DATASET_PATH,
    "Student_1.pdf"
)

MARKS_PATH = os.path.join(
    DATASET_PATH,
    "Teacher_manual_marks_Anonymized.csv"
)


# -----------------------------------
# Q21 information
# -----------------------------------

question = "Define Supervised Learning."

model_answer = (
    "A type of ML where the model is trained on labeled data "
    "with known inputs and outputs."
)

maximum_marks = 2


# -----------------------------------
# Read Student 1 teacher mark
# -----------------------------------

marks_data = pd.read_csv(MARKS_PATH)

student_row = marks_data[
    marks_data["Student_ID"] == "Student_1"
].iloc[0]

target_mark = float(student_row["21"])

print("Student:", student_row["Student_ID"])
print("Question: Q21")
print("Teacher Mark:", target_mark)


# -----------------------------------
# Convert first PDF page to image
# -----------------------------------

doc = fitz.open(PDF_PATH)

print("Number of pages:", len(doc))

for i in range(len(doc)):
    print("Page:", i + 1)

page = doc[0]

pix = page.get_pixmap()

image_path = os.path.join(
    os.path.dirname(__file__),
    "student1_q21_test.png"
)

pix.save(image_path)

doc.close()


# -----------------------------------
# Preprocess image
# -----------------------------------

processed_image = preprocess_image(
    image_path
)


# -----------------------------------
# OCR
# -----------------------------------

ocr_result = extract_text(
    processed_image
)

raw_text = ocr_result["raw_text"]
corrected_text = ocr_result["corrected_text"]

print("\nCorrected OCR:")
print(corrected_text)


# -----------------------------------
# Calculate similarity
# -----------------------------------

similarity_score = calculate_similarity(
    corrected_text,
    model_answer
)

print("\nSimilarity Score:", similarity_score)


# -----------------------------------
# Gemini evaluation
# -----------------------------------

analysis = evaluate_answer(
    image_path=image_path,
    student_text=corrected_text,
    raw_text=raw_text,
    question=question,
    model_answer=model_answer,
    similarity=similarity_score,
    max_marks=maximum_marks
)

print("\nGemini Evaluation:")
print(analysis)


# -----------------------------------
# Create one ML training row
# -----------------------------------

row = {
    "similarity_score": similarity_score,
    "concept_accuracy": analysis["concept_accuracy"],
    "answer_completeness": analysis["answer_completeness"],
    "diagram_correctness": analysis["diagram_correctness"],
    "presentation": analysis["presentation"],
    "maximum_marks": maximum_marks,
    "target_mark": target_mark
}

print("\nML Training Row:")
print(row)

# -----------------------------------
# Save training row
# -----------------------------------

output_path = os.path.join(
    DATASET_PATH,
    "answer_scores.csv"
)

new_row = pd.DataFrame([row])

new_row.to_csv(
    output_path,
    index=False
)

print("\nTraining row saved successfully.")
print("Saved to:", output_path)