from paddleocr import PaddleOCR
from AI.ocr_corrector import correct_ocr

# Load PaddleOCR only once
ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="en_PP-OCRv5_mobile_rec",
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False
)


def extract_text(image_path):
    """
    Extract text using PaddleOCR and correct it using Gemini.

    Returns:
    {
        "raw_text": "...",
        "corrected_text": "..."
    }
    """

    result = ocr.predict(image_path)

    raw_text = ""

    for page in result:
        if "rec_texts" in page:
            for text in page["rec_texts"]:
                raw_text += text + "\n"

    corrected_text = correct_ocr(
        raw_text,
        image_path
    )

    return {
        "raw_text": raw_text,
        "corrected_text": corrected_text
    }