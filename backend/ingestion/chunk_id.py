import re
from pathlib import Path


def generate_chunk_ids(chunks):
    counters = {}

    for chunk in chunks:
        source = chunk["metadata"]["source"]
        file_name = chunk["metadata"]["file"]

        base_name = Path(file_name).stem

        # Source + filename ko safe ID format mein convert karo
        base_id = f"{source}-{base_name}"
        base_id = re.sub(r"[^a-zA-Z0-9]+", "-", base_id).strip("-").lower()

        # Har file/source combination ka counter
        counters[base_id] = counters.get(base_id, 0) + 1

        chunk_number = counters[base_id]

        chunk["id"] = f"{base_id}-{chunk_number:03d}"

    return chunks