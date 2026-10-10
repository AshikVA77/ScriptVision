import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from AI.ocr import extract_text_from_image, extract_text_from_pdf

file_path = r"Assets/Tests/Sample.jpeg"

if file_path.lower().endswith(".pdf"):
    text = extract_text_from_pdf(file_path)
else:
    text = extract_text_from_image(file_path)

print("\n===== EXTRACTED TEXT =====\n")
print(text)