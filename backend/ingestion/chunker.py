def create_chunks(blocks, max_characters=2000):
    chunks = []

    current_blocks = []
    current_length = 0
    current_section = None

    for block in blocks:
        content = block["content"]
        section = block["metadata"].get("section")

        # Section change hone par current chunk complete karo
        if current_blocks and section != current_section:
            chunks.append(build_chunk(current_blocks))

            current_blocks = []
            current_length = 0

        current_section = section

        # Size limit cross hone par current chunk complete karo
        if current_blocks and current_length + len(content) > max_characters:
            chunks.append(build_chunk(current_blocks))

            current_blocks = []
            current_length = 0

        current_blocks.append(block)
        current_length += len(content)

    # Last chunk
    if current_blocks:
        chunks.append(build_chunk(current_blocks))

    return chunks


def build_chunk(blocks):
    contents = []

    for block in blocks:
        contents.append(block["content"])

    metadata = blocks[0]["metadata"].copy()

    return {
        "content": "\n\n".join(contents),
        "metadata": metadata,
    }