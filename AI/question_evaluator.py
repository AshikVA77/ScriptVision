from AI.similarity import calculate_similarity
from AI.evaluator import evaluate_answer
from AI.ML.features import create_features
from AI.ML.predict import predict_marks
from AI.feedback import generate_feedback


def evaluate_question_answer(
    image_paths,
    student_text,
    question
):

    # ---------------------------------------------
    # Question details
    # ---------------------------------------------

    question_text = question.question_text
    model_answer = question.model_answer
    max_marks = question.maximum_marks


    # ---------------------------------------------
    # Semantic Similarity
    # ---------------------------------------------

    similarity = calculate_similarity(
        student_text,
        model_answer
    )


    # ---------------------------------------------
    # Gemini Evaluation
    # ---------------------------------------------

    analysis = evaluate_answer(
        image_paths=image_paths,
        student_text=student_text,
        raw_text=student_text,
        question=question_text,
        model_answer=model_answer,
        similarity=similarity,
        max_marks=max_marks
    )


    # ---------------------------------------------
    # Create ML Features
    # ---------------------------------------------

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


    # ---------------------------------------------
    # Random Forest Mark Prediction
    # ---------------------------------------------

    predicted_mark = predict_marks(
        features,
        max_marks
    )


    # ---------------------------------------------
    # Percentage
    # ---------------------------------------------

    percentage = round(
        (
            predicted_mark /
            max_marks
        ) * 100,
        2
    ) if max_marks else 0


    # ---------------------------------------------
    # Grade
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
    # Marks
    # ---------------------------------------------

    marks = {
        "total_marks": predicted_mark,
        "max_marks": max_marks,
        "percentage": percentage,
        "grade": grade
    }


    # ---------------------------------------------
    # Feedback
    # ---------------------------------------------

    feedback = generate_feedback(
        analysis,
        marks
    )


    # ---------------------------------------------
    # Return Result
    # ---------------------------------------------

    return {
        "question": question,
        "question_id": question.question_id,
        "question_number": question.question_number,
        "extracted_text": student_text,
        "similarity": similarity,
        "analysis": analysis,
        "marks": marks,
        "feedback": feedback
    }