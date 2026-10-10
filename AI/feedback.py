def generate_feedback(analysis, marks):
    return {
        "marks": marks["total_marks"],
        "max_marks": marks["max_marks"],
        "percentage": marks["percentage"],
        "grade": marks["grade"],

        "strengths": analysis["strengths"],
        "missing_points": analysis["missing_points"],
        "feedback": analysis["feedback"]
    }