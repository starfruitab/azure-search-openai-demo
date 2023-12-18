import os
import re
import pandas as pd
import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict, Optional

class XMLMerger:
    def __init__(self, xml_dir: str, verbose: bool = False):
        self.xml_dir = xml_dir
        self.verbose = verbose

    def log(self, message: str):
        if self.verbose:
            print(message)

    def merge_xml_files(self, file_list: List[str]) -> Tuple[ET.ElementTree, Dict[str, Dict[str, str]]]:
        topic_root = ET.Element('topic')
        file_section_mapping = {}

        for index, file_name in enumerate(file_list, start=1):
            if not file_name:
                continue

            full_path = os.path.join(self.xml_dir, file_name)
            try:
                tree = ET.parse(full_path)
                root = tree.getroot()

                topic_id = self.get_topic_id(root)               
                section_root = ET.SubElement(topic_root, 'section', attrib={'id': f'section{index}', 'topic': topic_id})
                
                title_text = self._extract_title_text(root)
                file_section_mapping[file_name] = {'Link': f'#section{index}', 'Title': title_text}

                for child in root:
                    section_root.append(child)

            except ET.ParseError as e:
                self.log(f"XML Parse Error in {full_path}: {e}")
            except Exception as e:
                self.log(f"Error processing {full_path}: {e}")

        return ET.ElementTree(topic_root), file_section_mapping

    def get_topic_id(self, root: ET.Element) -> str:
        topic_id = root.get('id') if root is not None else None
        if topic_id:
            return topic_id
        return ""

    def _extract_title_text(self, root: ET.Element) -> str:
        title = root.find('.//title')
        if title is not None:
            title_text = ''.join(title.itertext()).replace('\n', ' ').strip()
            title.clear()
            title.text = title_text
            return title_text
        return ""

    @staticmethod
    def read_xlsx(file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path, dtype=str)

    @staticmethod
    def extract_xml_from_link(content: str) -> Optional[str]:
        pattern = r'href="([^"]+\.xml)[^"]*"'
        match = re.search(pattern, content)
        return match.group(1) if match else None