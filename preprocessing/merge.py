import re
import xml.etree.ElementTree as ET
import pandas as pd

def merge_xml_files(file_list, xml_dir, verbose=False):
    # Initialize the topic element
    topic_root = ET.Element('topic')
    file_section_mapping = {}

    # Iterate over each file in the list and merge their contents
    for index, file_name in enumerate(file_list, start=1):
        if file_name is None:
            continue

        full_path = xml_dir + file_name
        try:
            # Parse each XML file and get its root
            section_root = ET.SubElement(topic_root, 'section', attrib={'id': f'section{index}'})
            tree = ET.parse(full_path)
            root = tree.getroot()

            title = root.find('.//title')
            if title is not None:
                title_text = ''

                if title.text:
                    title_text += title.text
                for sub_element in title:
                    if sub_element.text:
                        title_text += sub_element.text

                    if sub_element.tail:
                        title_text += sub_element.tail
                
                # Remove all /n from the text
                title_text = title_text.replace('\n', ' ')

                #Overwrite the title with only the text
                for sub_element in list(title):
                    title.remove(sub_element)
                title.text = title_text
            else:
                title_text = ""  # Or any other default value


            if root is not None:
                # Add the contents of the root to the topic element
                for child in root:
                    section_root.append(child)

            file_section_mapping[file_name] = {'Link': f'#section{index}', 'Title': title_text}

            
        except Exception as e:
            if verbose:
                print(f"Error processing {full_path}: {e}")
        

    # Return the new tree with the merged content
    return ET.ElementTree(topic_root), file_section_mapping

def read_xlsx(file_path):
    df = pd.read_excel(file_path, dtype=str)
    return df

def get_relevant_content(start_text: str, end_text: str, content: str):
    start_index = content.find(start_text)
    end_index = content.find(end_text, start_index)
    if start_index == -1 or end_index == -1:
        return None
    return content[start_index:end_index]

def get_links_from_content(content: str):
    content_lines = content.split("\n")
    links = []
    for line in content_lines:
        xml_name = extract_xml_from_link(line)
        if xml_name is not None:
            links.append(xml_name)

    return links


def extract_xml_from_link(content):
    pattern = r'href="([^"]+\.xml)[^"]*"'

    match = re.search(pattern, content)

    if match:
        return match.group(1)
    else:
        return None