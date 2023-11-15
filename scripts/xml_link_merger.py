import re

XML_DIR = "3030000-0126/xml/"
MAIN_XML = "0000145342.xml"
OUTPUT_PATH = "data/section_4.xml"


def get_relevant_content(start_text: str, end_text: str, content: str):
    start_index = content.find(start_text)
    end_index = content.find(end_text)

    if start_index == -1 or end_index == -1 or end_index <= start_index:
        # Start or end text not found, or end text appears before start text
        return None

    relevant_content = content[start_index + len(start_text):end_index]
    return relevant_content


def merge_xml_by_links(content: str):
    content_lines = content.split("\n")
    new_content_lines = []
    for line in content_lines:
        new_content_lines.append(line)
        xml_name = extract_xml_from_link(line)
        if xml_name is not None:
            with open(XML_DIR + xml_name) as f:
                linked_xml_content = f.read().split("\n")
            new_content_lines += linked_xml_content
    return "\n".join(new_content_lines)


def extract_xml_from_link(content):
    pattern = r'href="([^"]+\.xml)[^"]*"'

    match = re.search(pattern, content)

    if match:
        return match.group(1)
    else:
        return None


if __name__ == "__main__":
    with open(XML_DIR + MAIN_XML) as f:
        content = f.read()
    content = get_relevant_content(
        start_text="<!--4 Screw Cap Application Unit-->",
        end_text="<!--5-->",
        content=content
    )
    coherent_content = merge_xml_by_links(content)
    print(coherent_content)
    with open(OUTPUT_PATH, "w") as f:
        f.write(coherent_content)
