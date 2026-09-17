from pathlib import Path

from ingestion.sources.local import load_markdown_files
from ingestion.extractor import extract_markdown
from ingestion.cleaner import clean_text
from ingestion.metadata import add_metadata
from ingestion.chunker import create_chunks
from ingestion.chunk_id import generate_chunk_ids
from services.embedding_service import EmbeddingService

def process_documentation(source_dir):
    # 1. load Markdown files 
    documents = load_markdown_files(source_dir)

    all_chunks = []

    for document in documents:
        file_path = document["source"]
        content = document["content"]

        # 2. extract Markdown content to blocks (headings, paragraphs, code blocks)
        blocks = extract_markdown(content)

        # 3. clean text for each block except code blocks (code blocks are not cleaned to preserve formatting)
        for block in blocks:
            if block["type"]!="code":
                block["content"] = clean_text(block["content"])

        # 4. add metadata to each block (source, file name, section, type, language)
        blocks = add_metadata(
            blocks,
            file_path=file_path,
            source=file_path
        )

        # 5. convert blocks to chunks (grouping blocks into chunks based on section and size)
        chunks = create_chunks(blocks)

        all_chunks.extend(chunks)

    # 6. add unique IDs to each chunk based on source and file name
    all_chunks = generate_chunk_ids(all_chunks)

    # 7. generate embeddings for each chunk using the embedding service
    # embedding_service = EmbeddingService()

    # for chunk in all_chunks:
    #     chunk["embedding"]= embedding_service.generate_embedding(chunk["content"])

    return all_chunks

if __name__ == "__main__":
    chunks = process_documentation("../docs")

    print(f"Total chunks: {len(chunks)}")

    if chunks:
        print("\nFirst chunk:")
        print(chunks[0])