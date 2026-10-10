from AI.evaluator import evaluate_answer

teacher_answer = """
HTML is the standard markup language used to create web pages.
It consists of tags such as html, head, body, title, h1, p, a, img etc.
"""

student_answer = """
HTML is used to create web pages.
It contains html, head, body, title and anchor tags.
"""

result = evaluate_answer(
    image_path="Assets/Tests/sample2.jpeg",
    student_text=student_answer,
    raw_text=student_answer,
    question="Create an HTML page demonstrating basic HTML tags.",
    model_answer=teacher_answer,
    similarity=96.5,
    max_marks=10
)

print(result)