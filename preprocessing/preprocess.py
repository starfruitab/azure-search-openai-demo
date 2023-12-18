from xml.etree import ElementTree as ET
import os
#from xml_parsing import xml_to_html
from merge import XMLMerger
from xml_parsing import XMLToHTMLConverter
import pandas as pd

# Constants
XML_DIR = "./all_xml_data/3030000-0126/xml/"

def get_xml_dir(file):
    return "./all_xml_data/" + file + "/xml/"

UP_DIR = "./update_pages/"
OUTPUT_DIR = "./output/"
VERBOSE = False

# This is a bit of a hacky solution, but it works for now
def convert_update_pages_to_xml():
    """
    Converts all update pages to XML files
    """
    for filename, index in zip(os.listdir(UP_DIR), range(len(os.listdir(UP_DIR)))):
        filepath = filename.split(".")[0]
        filepath = filepath.replace("_", "-")
        xml_dir = get_xml_dir(filepath)

        merger = XMLMerger(xml_dir, verbose=True)

        df = merger.read_xlsx(os.path.join(UP_DIR, filename))
        links = [link + ".xml" for link in df['Number'].to_numpy()]

        if links:
            merged_tree, mapping = merger.merge_xml_files(links)

            merged_tree_string = ET.tostring(merged_tree.getroot(), encoding='utf-8', method='xml').decode()
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            with open(os.path.join(OUTPUT_DIR, f"update_pages_{index}.xml"), 'w') as f:
                f.write(merged_tree_string)

            mapping_df = pd.DataFrame.from_dict(mapping, orient='index').reset_index()
            mapping_df.columns = ['FileName', 'Link', 'Title']
            mapping_df.to_csv(os.path.join(OUTPUT_DIR, 'mapping_up.csv'), index=False)

            print(f"Successfully merged {len(links)} XML files and wrote to {OUTPUT_DIR}merged.xml")

        print("Converting UP XML to HTML...")
        
        special_comment = "<!-- NOTE: Give prio'rity to this below when duplicated named sections exist. -->"

        converter = XMLToHTMLConverter(mapping_path=os.path.join(OUTPUT_DIR, 'mapping_up.csv'), special_section_comment=special_comment)
        converter.xml_to_html(os.path.join(OUTPUT_DIR, f"update_pages_{index}.xml"), os.path.join(OUTPUT_DIR, f"update_pages_{index}.html"))

def main():
    merger = XMLMerger(XML_DIR, verbose=VERBOSE)

    print("Reading excel file...")
    df = merger.read_xlsx("./3030000_0126.xlsx")
    links = [link + ".xml" for link in df['Number'].to_numpy()]

    print("Merging XML files...")
    if links:
        merged_tree, mapping = merger.merge_xml_files(links)

        merged_tree_string = ET.tostring(merged_tree.getroot(), encoding='utf-8', method='xml').decode()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        with open(os.path.join(OUTPUT_DIR, 'merged.xml'), 'w') as f:
            f.write(merged_tree_string)

        mapping_df = pd.DataFrame.from_dict(mapping, orient='index').reset_index()
        mapping_df.columns = ['FileName', 'Link', 'Title']
        mapping_df.to_csv(os.path.join(OUTPUT_DIR, 'mapping.csv'), index=False)

        print(f"Successfully merged {len(links)} XML files and wrote to {OUTPUT_DIR}merged.xml")

    print("Converting XML to HTML...")
    converter = XMLToHTMLConverter()
    converter.xml_to_html(os.path.join(OUTPUT_DIR, "merged.xml"), os.path.join(OUTPUT_DIR, "merged.html"))

    #Update pages
    print("Converting update pages to XML...")
    convert_update_pages_to_xml()

if __name__ == "__main__":
    main()
