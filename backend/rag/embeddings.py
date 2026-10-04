from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_query_embedding(question):
    embedding = model.encode(question)
    return embedding