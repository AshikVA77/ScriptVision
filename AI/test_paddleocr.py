from paddleocr import PaddleOCR

print("Creating PaddleOCR...")

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="en_PP-OCRv5_mobile_rec",
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False
)

print("PaddleOCR created successfully.")

image_path = r"Assets\Tests\Sample.jpeg"

print("Starting OCR...")

result = ocr.predict(image_path)

print("OCR completed successfully.")
print(result)