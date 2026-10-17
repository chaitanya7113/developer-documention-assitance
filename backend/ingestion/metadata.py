from pathlib import Path
from ingestion.function_detector import detect_function_names, detect_function_calls

def add_metadata(blocks, file_path,source):
    # File path ko Path object me convert karte hain, taaki .name se
    # sirf file ka naam aasani se mil sake.
    file_path = Path(file_path)

    # Heading levels aur unke titles yahan track honge.
    # Example: {1: "React", 2: "Installation"}
    sections = {}

    # Final output ke saare processed blocks is list me save honge.
    result = []

    for block in blocks:
        # Heading ko result me add nahi karna; ise current section and subsections ko track karne ke liye use karna hai.
        # identify karne ke liye use karna hai.
        if block["type"] == "heading":
            level = block["level"]  # here level will be 1,2,3 is a key and the value will be the title of that section
            title = block["content"]

            sections[level] = title # if level is 2 and title is "Introduction" then sections will be {2: "Introduction"}

            # Current heading se deeper purane sections remove karo.
            # list(sections) keys ki copy banata hai, isliye original
            # dictionary se delete karna safely possible hota hai.
            for section_level in list(sections):   # list(sections)= [1,2,3] and section_level=1,2,3
                if section_level > level:    # if section_level is 3 and level is 2, then delete the section
                    del sections[section_level]

            continue

        # Har paragraph ya code block ke liye basic metadata banao.
        metadata = {
            "source": source,
            "file": file_path.name,
            "type": block["type"],
        }

        if sections:
            # max(sections) sabse bada heading level deta hai, jo current
            # deepest section hota hai.
            current_level = max(sections)
            metadata["section"] = sections[current_level]

        
        if block["type"] == "code":
            # Code block ki programming language save karo.
            metadata["language"] = block["language"]

            language = block["language"].lower()

            supported_languages = {
                "js", "jsx", "javascript",
                "ts", "tsx", "typescript",
            }

            if language in supported_languages:
                code = block["content"]

                metadata["function_names"] = detect_function_names(code)
                metadata["function_calls"] = detect_function_calls(code)
            else:
                metadata["function_names"] = []
                metadata["function_calls"] = []


        # Content aur metadata ko ek result item ke roop me add karo.
        result.append({
            "content": block["content"],
            "metadata": metadata,
        })

    return result