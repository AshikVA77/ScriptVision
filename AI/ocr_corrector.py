from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


def correct_ocr(text, image_path):

    image = Image.open(image_path)

    prompt = f"""
You are an OCR post-processing engine for handwritten student answer sheets.

You are given:
1. The original handwritten answer image.
2. OCR text extracted from that image.

Your ONLY task is to correct OCR recognition errors.

IMPORTANT:
Use the handwritten image as the primary evidence when deciding whether
an OCR word or character is incorrect.

Strict Rules:
1. Correct only OCR recognition errors.
2. Never rewrite or paraphrase the student's answer.
3. Never improve the student's grammar or writing style.
4. Never add information that is not visible in the image.
5. Never remove information that is clearly visible.
6. Correct obvious character and word recognition errors.
7. Correct technical terms only when the handwriting clearly supports them.
8. Never invent SQL keywords, programming keywords, variable names,
   numbers, symbols, formulas, or identifiers.
9. If handwriting is unclear, keep the OCR text unchanged.
10. Preserve the student's original meaning.
11. Preserve the original order and line structure as much as possible.
12. Do not use the model answer to guess missing words.
13. Do not complete unfinished sentences.
14. Return ONLY the corrected OCR text.
15. Do not add explanations, notes, or markdown.

OCR TEXT:
----------------
{text}
----------------
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            image,
            prompt
        ],
        config=types.GenerateContentConfig(
            temperature=0.1
        )
    )

    return response.text.strip()