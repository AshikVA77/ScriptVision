def create_features(
    similarity,
    concept_accuracy,
    answer_completeness,
    diagram_correctness,
    presentation,
    max_marks
):
    """
    Create the feature vector used by the ML marking model.

    All quality scores are expected to be between 0 and 1.
    Similarity is expected as a percentage between 0 and 100.
    """

    features = [
        similarity / 100.0,
        concept_accuracy,
        answer_completeness,
        diagram_correctness,
        presentation,
        max_marks
    ]

    return features