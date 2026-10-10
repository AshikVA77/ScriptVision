from AI.file_handler import prepare_answer_script
from AI.preprocess import preprocess_image
from AI.ocr import extract_text
from AI.similarity import calculate_similarity
from AI.evaluator import evaluate_answer
from AI.ML.features import create_features
from AI.ML.predict import predict_marks
from AI.feedback import generate_feedback
from AI.report_generator import generate_report


def evaluate_answer_sheet(
    file_path,
    question,
    model_answer,
    max_marks,
    rubric
):

    # ---------------------------------------------
    # 1. Prepare Answer Script
    # ---------------------------------------------

    script = prepare_answer_script(
        file_path
    )

    pages = script["pages"]


    # ---------------------------------------------
    # 2. Process Each Page
    # ---------------------------------------------

    page_results = []


    for page_number, page_path in enumerate(
        pages,
        start=1
    ):

        # -----------------------------------------
        # Image Preprocessing
        # -----------------------------------------

        processed_image = preprocess_image(
            page_path
        )


        # -----------------------------------------
        # OCR + OCR Correction
        # -----------------------------------------

        ocr_result = extract_text(
            processed_image
        )

        raw_text = ocr_result["raw_text"]

        corrected_text = ocr_result[
            "corrected_text"
        ]


        # -----------------------------------------
        # Semantic Similarity
        # -----------------------------------------

        similarity = calculate_similarity(
            corrected_text,
            model_answer
        )


        # -----------------------------------------
        # Gemini Qualitative Evaluation
        # -----------------------------------------

        analysis = evaluate_answer(
            image_path=processed_image,
            student_text=corrected_text,
            raw_text=raw_text,
            question=question,
            model_answer=model_answer,
            similarity=similarity,
            max_marks=max_marks
        )


        # -----------------------------------------
        # Create ML Features
        # -----------------------------------------

        features = create_features(
            similarity=similarity,
            concept_accuracy=analysis[
                "concept_accuracy"
            ],
            answer_completeness=analysis[
                "answer_completeness"
            ],
            diagram_correctness=analysis[
                "diagram_correctness"
            ],
            presentation=analysis[
                "presentation"
            ],
            max_marks=max_marks
        )


        # -----------------------------------------
        # Random Forest Prediction
        # -----------------------------------------

        predicted_mark = predict_marks(
            features,
            max_marks
        )


        # -----------------------------------------
        # Percentage
        # -----------------------------------------

        percentage = round(
            (
                predicted_mark /
                max_marks
            ) * 100,
            2
        ) if max_marks else 0


        # -----------------------------------------
        # Grade
        # -----------------------------------------

        if percentage >= 90:
            grade = "A+"

        elif percentage >= 80:
            grade = "A"

        elif percentage >= 70:
            grade = "B"

        elif percentage >= 60:
            grade = "C"

        elif percentage >= 50:
            grade = "D"

        else:
            grade = "F"


        # -----------------------------------------
        # Marks
        # -----------------------------------------

        marks = {
            "total_marks": predicted_mark,
            "max_marks": max_marks,
            "percentage": percentage,
            "grade": grade
        }


        # -----------------------------------------
        # Feedback
        # -----------------------------------------

        feedback = generate_feedback(
            analysis,
            marks
        )


        # -----------------------------------------
        # Store Page Result
        # -----------------------------------------

        page_results.append({

            "page_number": page_number,

            "raw_ocr": raw_text,

            "corrected_ocr": corrected_text,

            "similarity": similarity,

            "analysis": analysis,

            "marks": marks,

            "feedback": feedback
        })


    # ---------------------------------------------
    # 3. Return Complete Result
    # ---------------------------------------------

    return {
        "file_type": script["file_type"],

        "total_pages": script["total_pages"],

        "pages": page_results
    }