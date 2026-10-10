from AI.file_handler import prepare_answer_script
from AI.preprocess import preprocess_image
from AI.ocr import extract_text
from AI.question_extractor import extract_question_answers


def extract_student_answers(file_path):

    # ---------------------------------------------
    # 1. Prepare Answer Script
    # ---------------------------------------------

    script = prepare_answer_script(file_path)

    pages = script["pages"]

    all_answers = {}
    page_results = []

    # Remember the last question detected on previous pages
    last_question_number = None

    # ---------------------------------------------
    # 2. Process Every Page
    # ---------------------------------------------

    for page_number, page_path in enumerate(pages, start=1):

        # Preprocessing is currently bypassed
        processed_image = page_path
        processed_image_path = processed_image

        # -----------------------------------------
        # OCR
        # -----------------------------------------

        ocr_result = extract_text(processed_image_path)

        raw_text = ocr_result["raw_text"]
        corrected_text = ocr_result["corrected_text"]
        
        print(f"\n========== OCR PAGE {page_number} ==========")
        print("OCR TEXT:")
        print(corrected_text)
        print("============================================")

        # -----------------------------------------
        # Extract Questions
        # -----------------------------------------

        answers = extract_question_answers(
            corrected_text,
            continuation_question=last_question_number
        )

        print(f"QUESTIONS DETECTED ON PAGE {page_number}:")
        print(answers)
        # -----------------------------------------
        # Store Page Result
        # -----------------------------------------

        page_results.append({
            "page_number": page_number,
            "page_path": processed_image_path,
            "raw_text": raw_text,
            "corrected_text": corrected_text,
            "answers": answers
        })

        # -----------------------------------------
        # Combine Answers Across Pages
        # -----------------------------------------

        for question_number, answer in answers.items():

            if question_number not in all_answers:

                all_answers[question_number] = {
                    "answer": answer,
                    "pages": [page_number],
                    "page_paths": [processed_image_path]
                }

            else:

                all_answers[question_number]["answer"] += (
                    "\n" + answer
                )

                all_answers[question_number]["pages"].append(
                    page_number
                )

                all_answers[question_number]["page_paths"].append(
                    processed_image_path
                )

        # -----------------------------------------
        # Update Last Detected Question
        # -----------------------------------------

        if answers:
            last_question_number = list(answers.keys())[-1]

    # ---------------------------------------------
    # 3. Return Extracted Answers
    # ---------------------------------------------

    return {
        "file_type": script["file_type"],
        "total_pages": script["total_pages"],
        "answers": all_answers,
        "pages": page_results
    }