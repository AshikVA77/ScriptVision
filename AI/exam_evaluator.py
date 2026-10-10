from AI.answer_extractor import extract_student_answers
from AI.question_evaluator import evaluate_question_answer


def evaluate_exam(file_path, questions):

    # ---------------------------------------------
    # 1. Extract Student Answers
    # ---------------------------------------------

    extracted = extract_student_answers(file_path)

    student_answers = extracted["answers"]

    evaluation_results = []

    # ---------------------------------------------
    # 2. Evaluate Each Question
    # ---------------------------------------------

    for question in questions:

        try:
            question_number = int(question.question_number)

        except (ValueError, TypeError):
            continue

        # -----------------------------------------
        # Check Student Answer Exists
        # -----------------------------------------

        student_answer = student_answers.get(question_number)
        
        if student_answer:
            print("\n========== MULTI-PAGE DEBUG ==========")
            print("Question:", question_number)
            print("Pages detected:", student_answer["pages"])
            print("Image paths:", student_answer["page_paths"])
            print("Combined extracted answer:")
            print(student_answer["answer"])
            print("======================================\n")

        if not student_answer:

            evaluation_results.append({
                "question": question,
                "page_number": None,
                "extracted_text": "",
                "similarity": 0,
                "marks": {
                    "total_marks": 0,
                    "max_marks": question.maximum_marks,
                    "percentage": 0,
                    "grade": "F"
                },
                "feedback": "No answer detected."
            })

            continue

        # -----------------------------------------
        # Get All Pages Containing the Answer
        # -----------------------------------------

        page_paths = student_answer["page_paths"]

        page_numbers = student_answer["pages"]

        # Pass every relevant page image to the evaluator
        image_paths = page_paths

        # Keep the first page number for the existing database field
        page_number = page_numbers[0] if page_numbers else None

        # -----------------------------------------
        # AI + ML Evaluation
        # -----------------------------------------

        result = evaluate_question_answer(
            image_paths=image_paths,
            student_text=student_answer["answer"],
            question=question
        )

        # -----------------------------------------
        # Add Page Number
        # -----------------------------------------

        result["page_number"] = page_number

        evaluation_results.append(result)

    # ---------------------------------------------
    # 3. Calculate Total Marks
    # ---------------------------------------------

    total_ai_marks = 0

    total_max_marks = 0

    for result in evaluation_results:

        total_ai_marks += result["marks"]["total_marks"]

        total_max_marks += result["marks"]["max_marks"]

    # ---------------------------------------------
    # 4. Overall Percentage
    # ---------------------------------------------

    percentage = round(
        (total_ai_marks / total_max_marks) * 100,
        2
    ) if total_max_marks else 0

    # ---------------------------------------------
    # 5. Overall Grade
    # ---------------------------------------------

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

    # ---------------------------------------------
    # 6. Return Complete Exam Result
    # ---------------------------------------------

    return {
        "file_type": extracted["file_type"],

        "total_pages": extracted["total_pages"],

        "evaluations": evaluation_results,

        "total_ai_marks": round(
            total_ai_marks,
            2
        ),

        "total_max_marks": total_max_marks,

        "percentage": percentage,

        "grade": grade
    }