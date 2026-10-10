from AI.pipeline import evaluate_answer_sheet
import json

question = "Create an HTML page demonstrating all basic HTML tags."

model_answer = """
HTML is the standard markup language used to create web pages.

It contains tags like:
<html>
<head>
<title>
<body>
<h1>
<p>
<a>
<img>

These tags are used to structure and format a web page.
"""

rubric = {
    "concept": 4,
    "completeness": 3,
    "diagram": 2,
    "presentation": 1
}

report = evaluate_answer_sheet(
    image_path="Assets/Tests/Sample2.jpeg",   # Change if your image name is different
    question=question,
    model_answer=model_answer,
    max_marks=10,
    rubric=rubric
)

print(json.dumps(report, indent=4))