from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_embedding(self, text):
        return self.model.encode(text).tolist()

    def generate_embeddings(self, texts):
        return self.model.encode(texts).tolist()

    def get_dimension(self):
        return self.model.get_sentence_embedding_dimension()