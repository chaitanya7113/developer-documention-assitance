
def create_chunks(blocks, max_characters=2000):
    chunks = []

    current_blocks = []
    current_length = 0
    current_section = None
    current_language = None

    for block in blocks:
        content = block["content"]
        metadata = block["metadata"]

        section = metadata.get("section")
        block_type = metadata.get("type")
        block_language = metadata.get("language")

        # Section change
        if current_blocks and section != current_section:
            chunks.append(build_chunk(current_blocks))
            current_blocks = []
            current_length = 0
            current_language = None

        current_section = section

        # Split when code language changes
        if (
            current_blocks
            and block_type == "code"
            and block_language
            and current_language
            and block_language != current_language
        ):
            chunks.append(build_chunk(current_blocks))
            current_blocks = []
            current_length = 0
            current_language = None

        # Split when size limit is crossed
        if current_blocks and current_length + len(content) > max_characters:
            chunks.append(build_chunk(current_blocks))
            current_blocks = []
            current_length = 0
            current_language = None

        # Set language after all split checks
        if block_type == "code" and block_language:
            current_language = block_language

        current_blocks.append(block)
        current_length += len(content)

    if current_blocks:
        chunks.append(build_chunk(current_blocks))

    return chunks



def build_chunk(blocks):
    contents = []

    content_types = set()
    languages = set()
    has_code = False
    function_names = []
    function_calls=[]

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

    

    for block in blocks:
        for name in block["metadata"].get("function_names", []):
            if name not in function_names:
                function_names.append(name)

        for call in block["metadata"].get("function_calls", []):
            if call not in function_calls:
                function_calls.append(call)

        

    
    metadata["function_names"] = function_names
    metadata["function_calls"]=function_calls

    metadata["content_types"] = list(content_types)
    metadata["has_code"] = has_code

    if languages:
        metadata["languages"] = list(languages)

    return {
        "content": "\n\n".join(contents),
        "metadata": metadata,
    }