import re
import xml.etree.ElementTree as ET
import pandas as pd
XML_DIR = "./all_xml_data/3030000-0126/xml/"
MAIN_XML = "0000145342.xml"
OUTPUT_PATH = "./section_4.xml"
ENCODING_FILE_PATH = "./encoding_mapping.csv"

def merge_xml_files(file_list, xml_dir):
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
                title_text = title.text.strip() if title is not None else 'No Title'

                # Remove all /n from the text
                title_text = title_text.replace('\n', ' ')

            if root is not None:
                # Add the contents of the root to the topic element
                for child in root:
                    section_root.append(child)

            file_section_mapping[file_name] = {'Link': f'#section{index}', 'Title': title_text}

            
        except Exception as e:
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

if __name__ == "__main__":
    # Read the excel file
    df = read_xlsx("./3030000_0126.xlsx")
    links = df['Number']
    links = links.to_numpy()

    links = links[5:2232]
    links = [link + ".xml" for link in links]

    with open(XML_DIR + MAIN_XML) as f:
        content = f.read()
    content = get_relevant_content(
        start_text="<!--4 Screw Cap Application Unit-->",
        end_text="<!--5-->",
        content=content
    )
    links = get_links_from_content(content)
    print(len(links))

    if links is not None:
        merged_tree, mapping = merge_xml_files(links, XML_DIR)

        # Convert the merged tree to string and write to file
        merged_tree_string = ET.tostring(merged_tree.getroot(), encoding='utf-8', method='xml').decode()
        with open(OUTPUT_PATH, "w") as f:
            f.write(merged_tree_string)

        mapping_df = pd.DataFrame.from_dict(mapping, orient='index')
        mapping_df.reset_index(inplace=True)
        mapping_df.columns = ['FileName', 'Link', 'Title']
        mapping_df.to_csv(ENCODING_FILE_PATH, index=False)

    else:
        print("Specified start and end text not found in the document.")
