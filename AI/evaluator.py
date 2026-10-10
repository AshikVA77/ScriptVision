from google import genai
from google.genai import types
from google.genai.errors import ServerError
from PIL import Image
from dotenv import load_dotenv
import json
import os
import time


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


def evaluate_answer(
    image_paths,
    student_text,
    raw_text,
    question,
    model_answer,
    similarity,
    max_marks
):

    images = [
        Image.open(image_path)
        for image_path in image_paths
        ]

    prompt = f"""
You are an experienced university examiner.

Evaluate the student's handwritten answer.

QUESTION:
{question}

TEACHER MODEL ANSWER:
{model_answer}

MAXIMUM MARKS:
{max_marks}

OCR EXTRACTED ANSWER:
{student_text}

RAW OCR (Reference Only):
{raw_text}

SEMANTIC SIMILARITY:
{similarity}%

IMPORTANT:

1. The attached image is the ORIGINAL handwritten answer sheet.
2. Use BOTH the OCR text and the original image.
3. If OCR missed words but they are clearly visible in the image, prefer the image.
4. Consider diagrams, graphs, tables, code and handwritten figures if relevant.
5. Similarity is ONLY supporting information.
6. Never calculate marks.
7. Never mention marks.
8. Return ONLY valid JSON.
9. Give each score between 0.0 and 1.0.

Return JSON in exactly this format:

{{
    "concept_accuracy": 0.0,
    "answer_completeness": 0.0,
    "diagram_correctness": 0.0,
    "presentation": 0.0,

    "strengths": [
        "...",
        "..."
    ],

    "missing_points": [
        "...",
        "..."
    ],

    "feedback": "..."
}}
"""

 
    # -----------------------------------
    # Primary Gemini evaluation with retry
    # -----------------------------------

    max_retries = 3

    for attempt in range(1, max_retries + 1):

        try:
            print(
                f"\nPrimary Gemini evaluation attempt "
                f"{attempt}/{max_retries}..."
            )

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[
                    images,
                    prompt
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )

            return json.loads(response.text)

        except ServerError as error:

            print(f"Primary Gemini server error: {error}")

            if attempt < max_retries:
                wait_time = 2 ** attempt

                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

            else:
                print("Primary Gemini retries exhausted.")

    # -----------------------------------
    # Backup Gemini model
    # -----------------------------------

    try:
        print("\nTrying backup model: gemini-3.5-flash...")

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                images,
                prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        result = json.loads(response.text)

        print("Backup Gemini evaluation successful.")

        return result

    except Exception as error:
        print(f"Backup Gemini evaluation failed: {error}")
        raise
