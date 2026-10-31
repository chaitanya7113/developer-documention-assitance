from pathlib import Path
from ingestion.sources.local import load_markdown_files
from ingestion.extractor import extract_markdown
from ingestion.cleaner import clean_text
from ingestion.metadata import add_metadata
from ingestion.chunker import create_chunks
from ingestion.chunk_id import generate_chunk_ids



DOCUMENTATION_SOURCE = "react.dev"

SOURCE_COMMIT = "8efce7853d0fc59e615ed1c253799cf1798b8428"

SNAPSHOT_DATE = "2026-09-10"

DOCUMENTATION_VERSION = None

def process_documentation(source_dir):
    # 1. load Markdown files 
    documents = load_markdown_files(source_dir)


    all_chunks = []

    total_blocks = 0

    for document in documents:
        file_path = document["source"]
        content = document["content"]

        

        # 2. extract Markdown content to blocks (headings, paragraphs, code blocks)
        blocks  = extract_markdown(content)

        

        

        # 3. clean text for each block except code blocks (code blocks are not cleaned to preserve formatting)
        for block in blocks:  
            if block["type"]!="code":
                block["content"] = clean_text(block["content"])

        

        # 4. add metadata to each block (source, file name, section, type, language)
        blocks = add_metadata(
            blocks,
            file_path=file_path,
            source=file_path,
            documentation_source=DOCUMENTATION_SOURCE,
            source_commit=SOURCE_COMMIT,
            snapshot_date=SNAPSHOT_DATE,
            version=DOCUMENTATION_VERSION,
        )

        # 5. convert blocks to chunks (grouping blocks into chunks based on section and size)
        chunks = create_chunks(blocks)

        all_chunks.extend(chunks)

    # 6. add unique IDs to each chunk based on source and file name
    all_chunks = generate_chunk_ids(all_chunks) 
    



    return all_chunks 


def validate_code_block_integrity(source_dir="../docs"):
    documents = load_markdown_files(source_dir)

    original_code_blocks = []

    for document in documents:
        blocks = extract_markdown(document["content"])

        for block in blocks:
            if (
                block.get("type") == "code"
                and block.get("content", "").strip()
            ):
                original_code_blocks.append(block["content"])

    chunks = process_documentation(source_dir)
    chunk_contents = [
        chunk.get("content", "")
        for chunk in chunks
    ]

    missing_blocks = [
        code
        for code in original_code_blocks
        if not any(code in content for content in chunk_contents)
    ]

    print("\n--- Code Block Integrity ---")
    print("Original non-empty code blocks:", len(original_code_blocks))
    print("Total chunks:", len(chunks))
    print("Code blocks not found intact:", len(missing_blocks))

    if missing_blocks:
        print("\nFirst missing code block:")
        print(missing_blocks[0][:500])




    # Keep your existing metadata validation here.



if __name__ == "__main__":
    chunks = process_documentation("../docs")
    
    
    print(f"Total chunks: {len(chunks)}")
    
    if chunks:
            for chunk in chunks[:5]:  # Print metadata for the first 5 chunks
                print(f"Chunk metadata: {chunk['metadata']}")