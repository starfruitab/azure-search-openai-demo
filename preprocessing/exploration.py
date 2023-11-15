import os
import xml.etree.ElementTree as ET
import pandas as pd

def extract_tags_from_file(file_path):
    try:
        # Parse the XML content from the file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract tags from this file
        tags = set()

        def find_tags(element):
            tags.add(element.tag)
            for child in element:
                find_tags(child)

        find_tags(root)
        return tags
    except ET.ParseError as e:
        print(f"Error parsing XML in file {file_path}: {e}")
        return set()
    except Exception as e:
        print(f"An error occurred with file {file_path}: {e}")
        return set()

def extract_tags_from_folder(folder_path):
    all_tags = set()
    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith('.xml') and filename.lower() != 'manifest.xml':
            file_tags = extract_tags_from_file(file_path)
            all_tags.update(file_tags)
    return all_tags

if __name__ == "__main__":

    # Define the directories
    xml_directory = './all_xml_data/3030000-0126/xml'
    output_directory = './output'

    # Extract tags from the XML files
    tags = extract_tags_from_folder(xml_directory)
    for tag in tags:
        print(tag)
