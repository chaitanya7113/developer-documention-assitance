from markdown_it import MarkdownIt

def extract_markdown(content):
    markdown = MarkdownIt()
    tokens = markdown.parse(content)

    blocks = []

    i = 0

    while i < len(tokens):
        token = tokens[i]

        # Heading
        if token.type == "heading_open":
            level = int(token.tag[1])

            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                blocks.append({
                    "type": "heading",
                    "level": level,
                    "content": tokens[i + 1].content
                })

            i += 2
            continue

        # Paragraph
        if token.type == "paragraph_open":
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                blocks.append({
                    "type": "paragraph",
                    "content": tokens[i + 1].content
                })

            i += 2
            continue

        # Code block
        # its job to get the language of the code block, if any. If no language is specified, it defaults to "text".
        if token.type == "fence":
            if not token.content.strip():                 
                i += 1
                continue

            info = token.info.strip() #its job to get the language of the code block, if any. If no language is specified, it defaults to "text".

            language = info.split()[0] if info else "text" # its job to get the language of the code block, if any. If no language is specified, it defaults to "text".

            blocks.append({
                "type": "code",
                "language": language,
                "content": token.content.rstrip("\n")
            })
        i += 1
            

    return blocks 



