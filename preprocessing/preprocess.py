from xml.etree import ElementTree as ET
import os
#from xml_parsing import xml_to_html
from merge import XMLMerger
from xml_parsing import XMLToHTMLConverter
from xml_to_markdown import XMLToMarkdownConverter
import pandas as pd

# Constants
XML_DIR = "./all_xml_data/3030000-0126/xml/"
OUTPUT_DIR = "./output/"
VERBOSE = False

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

if __name__ == "__main__":
    main()
