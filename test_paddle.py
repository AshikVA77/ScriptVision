from paddleocr import PaddleOCR
from AI.benchmark import preprocess_methods
from AI.ocr_corrector import correct_ocr

import cv2
import tempfile
import os

ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

# Choose the best preprocessing (Gray)
methods = preprocess_methods(r"Assets/Tests/sample3.jpeg")
image = methods["gray"]

# Save processed image temporarily
temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
temp.close()

cv2.imwrite(temp.name, image)

# Run OCR
result = ocr.predict(temp.name)

# Build raw text
raw_text = ""

for page in result:
    if "rec_texts" in page:
        for text in page["rec_texts"]:
            raw_text += text + "\n"

print("\n========== RAW OCR ==========\n")
print(raw_text)

print("\n========== GEMINI OCR ==========\n")

corrected = correct_ocr(raw_text)

print(corrected)

# Delete temp image
os.remove(temp.name)