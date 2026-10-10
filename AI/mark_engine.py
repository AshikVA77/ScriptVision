# AI/marking_engine.py

def calculate_marks(analysis, rubric):
    """
    Calculate final marks based on AI analysis and teacher-defined rubric.

    Parameters
    ----------
    analysis : dict
        Example:
        {
            "concept_accuracy": 0.90,
            "answer_completeness": 0.80,
            "diagram_correctness": 1.00,
            "presentation": 0.75
        }

    rubric : dict
        Example:
        {
            "concept": 4,
            "completeness": 3,
            "diagram": 2,
            "presentation": 1
        }

    Returns
    -------
    dict
    """

    concept = analysis.get("concept_accuracy", 0) * rubric.get("concept", 0)

    completeness = analysis.get(
        "answer_completeness", 0
    ) * rubric.get("completeness", 0)

    diagram = analysis.get(
        "diagram_correctness", 0
    ) * rubric.get("diagram", 0)

    presentation = analysis.get(
        "presentation", 0
    ) * rubric.get("presentation", 0)

    total = concept + completeness + diagram + presentation

    max_marks = sum(rubric.values())

    percentage = (total / max_marks) * 100 if max_marks else 0

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

    return {
        "concept_marks": round(concept, 2),
        "completeness_marks": round(completeness, 2),
        "diagram_marks": round(diagram, 2),
        "presentation_marks": round(presentation, 2),
        "total_marks": round(total, 2),
        "max_marks": max_marks,
        "percentage": round(percentage, 2),
        "grade": grade
    }