import re
import xml.etree.ElementTree as ET

XML_DIR = "./all_xml_data/3030000-0126/xml/"
MAIN_XML = "0000145342.xml"
OUTPUT_PATH = "./section_4.xml"

def merge_xml_files(file_list, xml_dir):
    # Initialize an empty root element
    merged_root = ET.Element('?xml version="1.0" encoding="UTF-8"?')
    merged_body = ET.Element('body')

    # Iterate over each file in the list and merge their contents
    for file_name in file_list:
        full_path = xml_dir + file_name
        try:
            # Parse each XML file and get its root
            tree = ET.parse(full_path)
            root = tree.getroot()

            # Find the 'body' or 'procbody' element and append its contents
            body = root.find('body') or root.find('procbody')
            if body is not None:
                for child in body:
                    merged_body.append(child)
        except Exception as e:
            print(f"Error processing {full_path}: {e}")

    # Return the new tree with the merged content
    merged_root.append(merged_body)
    return ET.ElementTree(merged_root)

def get_relevant_content(start_text: str, end_text: str, content: str):
    start_index = content.find(start_text)
    end_index = content.find(end_text, start_index)
    if start_index == -1 or end_index == -1:
        return None
    return content[start_index:end_index]

def extract_xml_from_link(content):
    pattern = r'href="([^"]+\.xml)"'
    return re.findall(pattern, content)

if __name__ == "__main__":
    with open(XML_DIR + MAIN_XML) as f:
        content = f.read()
    
    relevant_content = get_relevant_content("<!--4 Screw Cap Application Unit-->", "<!--5-->", content)
    if relevant_content:
        links = extract_xml_from_link(relevant_content)
        merged_tree = merge_xml_files(links, XML_DIR)

        # Convert the merged tree to string and write to file
        merged_tree_string = ET.tostring(merged_tree.getroot(), encoding='utf-8', method='xml').decode()
        with open(OUTPUT_PATH, "w") as f:
            f.write(merged_tree_string)
    else:
        print("Specified start and end text not found in the document.")
