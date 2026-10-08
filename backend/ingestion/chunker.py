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

    content_types = set()
    languages = set()
    has_code = False

    for block in blocks:
        contents.append(block["content"])

        block_type = block["metadata"].get("type")
        content_types.add(block_type)

        if block_type == "code":
            has_code = True

            language = block["metadata"].get("language")

            if language:
                languages.add(language)

    metadata = blocks[0]["metadata"].copy()

    metadata["content_types"] = list(content_types)
    metadata["has_code"] = has_code

    if languages:
        metadata["languages"] = list(languages)

    return {
        "content": "\n\n".join(contents),
        "metadata": metadata,
    }