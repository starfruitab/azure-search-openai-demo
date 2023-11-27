
from xml.etree import ElementTree as ET
import pandas as pd
import os
from merge import read_xlsx, merge_xml_files
from xml_parsing import xml_to_html

#The directory containing all the XML files
XML_DIR = "./all_xml_data/3030000-0126/xml/"
#The path to the output file (the merged XML file)
OUTPUT_DIR = "./output/"
#Whether to print verbose messages
VERBOSE = False

if __name__ == "__main__":
    # Read the excel file
    print("Reading excel file...")

    df = read_xlsx("./3030000_0126.xlsx")

    links = df['Number']
    links = links.to_numpy()
    links = [link + ".xml" for link in links]

    print("Merging XML files...")
    if links is not None:
        merged_tree, mapping = merge_xml_files(links, XML_DIR, verbose=VERBOSE)

        # Convert the merged tree to string and write to file
        merged_tree_string = ET.tostring(merged_tree.getroot(), encoding='utf-8', method='xml').decode()
        
        #Create the output directory if it doesn't exist
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        with open(OUTPUT_DIR + 'merged.xml', 'w') as f:
            f.write(merged_tree_string)

        mapping_df = pd.DataFrame.from_dict(mapping, orient='index')
        mapping_df.reset_index(inplace=True)
        mapping_df.columns = ['FileName', 'Link', 'Title']
        mapping_df.to_csv(OUTPUT_DIR + 'mapping.csv', index=False)

        print(f"Successfully merged {len(links)} XML files and wrote to {OUTPUT_DIR}merged.xml")

    print("Converting XML to HTML...")

    xml_to_html(OUTPUT_DIR + "merged.xml", OUTPUT_DIR + "merged.html")