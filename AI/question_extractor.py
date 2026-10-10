import re


def extract_question_answers(
    text,
    start_question=1,
    end_question=None,
    continuation_question=None
):
    answers = {}

    # Match question numbers such as:
    # 1.
    # 1)
    # 21.
    # 21)
    pattern = r'(?m)^\s*(\d{1,2})\s*[.)]\s*'

    matches = list(
        re.finditer(
            pattern,
            text
        )
    )

    # -------------------------------------------------
    # Case 1: No question number detected on this page
    # -------------------------------------------------

    if not matches:
        continuation_text = text.strip()

        if continuation_text and continuation_question is not None:
            answers[continuation_question] = continuation_text

        return answers

    # -------------------------------------------------
    # Case 2: Text before the first question number
    # This may be a continuation from the previous page.
    # -------------------------------------------------

    leading_text = text[:matches[0].start()].strip()

    if leading_text and continuation_question is not None:
        answers[continuation_question] = leading_text

    # -------------------------------------------------
    # Extract numbered answers
    # -------------------------------------------------

    for index, match in enumerate(matches):

        question_number = int(match.group(1))

        if question_number < start_question:
            continue

        if (
            end_question is not None
            and question_number > end_question
        ):
            continue

        answer_start = match.end()

        if index + 1 < len(matches):
            answer_end = matches[index + 1].start()
        else:
            answer_end = len(text)

        answer = text[answer_start:answer_end].strip()

        if not answer:
            continue

        if question_number in answers:
            answers[question_number] += "\n" + answer
        else:
            answers[question_number] = answer

    return answers