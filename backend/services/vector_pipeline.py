from ingestion.pipeline import process_documentation
from services.embedding_service import EmbeddingService
from services.qdrant_service import upsert_chunks


def process_and_store(source_dir):
    # Phase 2: documents → chunks
    chunks = process_documentation(source_dir)

    # Phase 3: chunks → embeddings
    embedding_service = EmbeddingService()

    for chunk in chunks:
        chunk["embedding"] = embedding_service.generate_embedding(
            chunk["content"]
        )

    # Phase 3: embeddings → Qdrant
    upsert_chunks(chunks)

    return chunks


if __name__ == "__main__":
    chunks = process_and_store("../docs")

    print(f"Total chunks processed: {len(chunks)}")