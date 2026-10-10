from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(student, teacher):
    emb1 = model.encode(student, convert_to_tensor=True)
    emb2 = model.encode(teacher, convert_to_tensor=True)

    score = cos_sim(emb1, emb2).item()

    return round(score * 100, 2)