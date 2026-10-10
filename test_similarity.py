from AI.similarity import calculate_similarity

teacher = """
Create an HTML page demonstrating all basic HTML tags.
"""

student = """
Create a HTML page demonstrating all basic HTML tags.
"""

score = calculate_similarity(student, teacher)

print(f"Similarity: {score}%")