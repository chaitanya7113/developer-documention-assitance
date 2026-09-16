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
        if token.type == "fence":
            blocks.append({
                "type": "code",
                "language": token.info.strip() or "text",
                "content": token.content.rstrip("\n")
            })

        i += 1

    return blocks