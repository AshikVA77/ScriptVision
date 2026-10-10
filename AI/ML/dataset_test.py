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


# -----------------------------------
# Load ML dataset
# -----------------------------------

data = pd.read_csv(
    r"E:\Main Project\ScriptVision\AI\dataset\answer_scores.csv"
)

print(data.head())
print(data.columns)

X = data[
    [
        'similarity_score',
        'concept_accuracy',
        'answer_completeness',
        'diagram_correctness',
        'presentation',
        'maximum_marks'
    ]
]

y = data[['target_mark']]

print(X)
print(y)


# -----------------------------------
# Test OCR on Student 1
# -----------------------------------

from AI.preprocess import preprocess_image
from AI.ocr import extract_text


pdf_path = r"E:\Main Project\ScriptVision\AI\dataset\Student_1.pdf"

doc = fitz.open(pdf_path)

page = doc[0]

pix = page.get_pixmap()

image_path = os.path.join(
    os.path.dirname(__file__),
    "student1_page1.png"
)

pix.save(image_path)

doc.close()


# -----------------------------------
# Apply OpenCV preprocessing
# -----------------------------------

processed_image = preprocess_image(image_path)


# -----------------------------------
# Apply PaddleOCR
# -----------------------------------

result = extract_text(processed_image)


print("\nRAW OCR:")
print(result["raw_text"])


print("\nCORRECTED OCR:")
print(result["corrected_text"])

# -----------------------------------
# Check Student 1 teacher marks
# -----------------------------------

marks_data = pd.read_csv(
    r"E:\Main Project\ScriptVision\AI\dataset\Teacher_manual_marks_Anonymized.csv"
)

print("\nTeacher marks columns:")
print(marks_data.columns.tolist())

print("\nStudent 1 teacher marks:")
print(marks_data.iloc[0])

# -----------------------------------
# Calculate similarity for Q21
# -----------------------------------

from AI.similarity import calculate_similarity

student_answer = """
Supervised learning is a machine learning algorithm
which we give labeled data as input and expect
output as prediction we want.
"""

model_answer = """
A type of ML where the model is trained on labeled data
with known inputs and outputs.
"""

similarity_score = calculate_similarity(
    student_answer,
    model_answer
)

print("\nQ21 Similarity Score:")
print(similarity_score)

# -----------------------------------
# Evaluate Q21 using Gemini
# -----------------------------------

from AI.evaluator import evaluate_answer

question = """
Define Supervised Learning.
"""

model_answer = """
A type of ML where the model is trained on labeled data
with known inputs and outputs.
"""

analysis = evaluate_answer(
    image_path=image_path,
    student_text=student_answer,
    raw_text=student_answer,
    question=question,
    model_answer=model_answer,
    similarity=similarity_score,
    max_marks=2
)

print("\nQ21 Gemini Evaluation:")
print(analysis)