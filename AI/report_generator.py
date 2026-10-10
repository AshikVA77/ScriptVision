def generate_report(
    raw_text,
    corrected_text,
    similarity,
    analysis,
    marks,
    feedback
):

    return {
        "raw_ocr": raw_text,
        "corrected_ocr": corrected_text,
        "similarity": similarity,

        "analysis": analysis,

        "marks": marks,

        "feedback": feedback
    }