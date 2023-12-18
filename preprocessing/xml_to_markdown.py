from tqdm import tqdm
import xml.etree.ElementTree as ET
import pandas as pd
from xml_parsing import XMLToHTMLConverter


class XMLToMarkdownConverter:

    def __init__(self, base_img_path='https://stsp3lqew6l65ci.blob.core.windows.net/illustrations/', mapping_path='./output/mapping.csv', base_css_path='./styles/style.css', verbose=False, verbose_skipped_tags=False):
        # Base paths
        self.html_parser = XMLToHTMLConverter(base_img_path=base_img_path, mapping_path=mapping_path, base_css_path=base_css_path, verbose=verbose, verbose_skipped_tags=verbose_skipped_tags)

        self.base_img_path = base_img_path
        self.base_css_path = base_css_path

        # Load the mapping from CSV
        self.mapping =  self.html_parser.load_mapping_from_csv(mapping_path)

        # Used for debugging
        self.verbose = verbose
        self.verbose_skipped_tags = verbose_skipped_tags
        self.skipped_tags = {}

        # Used for continuing the numbering of pli elements
        self.current_pli_list_position = 0

        # Create a dictionary to store pli references
        self.pli_reference_map = {}

        # Create a dictionary of page references
        self.page_reference_map = {}

    def log(self, message):
        """Logs a message if verbose is True."""
        if self.verbose:
            print(message)

    def log_skipped_tag(self, tag_name, function_name):
        """Logs a skipped tag."""
        if tag_name not in self.skipped_tags:
            self.skipped_tags[tag_name] = []
        self.skipped_tags[tag_name].append(function_name)

    def load_mapping_from_csv(self, file_path):
        """
        Reads the encoding mapping from a CSV file and returns it as a dictionary.
        """
        mapping_df = pd.read_csv(file_path, index_col='FileName')
        mapping = mapping_df.to_dict(orient='index')
        return mapping
    
    def convert_pos_to_html(self, pos_element):
        href = pos_element.get('editref')
        text = pos_element.text or ''
        return f'<a href="{href}">{text}</a>'

    def convert_xref_to_html(self, xref_element):
        href = xref_element.get('href')

        if href is None:
            return xref_element.text or ''
        
        filename = href.split('#')[0]
        if filename in self.mapping:
            new_href = self.mapping[filename]['Link']
            href_text = self.mapping[filename]['Title']
        else:
            #Fallback
            if href.startswith('#') and href.count('/') > 0:
                #Remove everything before /
                new_href = href.split('/')[-1]
            else:
                new_href = href

            #Check if in page reference map
            if new_href in self.page_reference_map:
                href_text = self.page_reference_map[new_href]
                new_href = '#' + new_href
            else:
                href_text = 'Reference'

        text = xref_element.text or href_text
        return f'<a href="{new_href}">{text}</a>'

    def xml_to_md(self,filepath='./main.xml',output_file='./main.md'):
        """
        Parses the XML file and converts it to HTML.
        Takes the XML file path as input and returns the HTML content.
        """
        try:
            xml_tree = ET.parse(filepath)

            # Add pli descriptions to pos tags (to make the links work correctly)
            xml_tree = self.html_parser.add_pli_description_to_pos_tags(xml_tree)

            # Set page references
            self.html_parser.set_page_references(xml_tree)

            # Convert the XML
            html_content = self.convert_xml_to_md_content(xml_tree.getroot())

            # Save the HTML content to a file
            self.save_to_md(html_content, output_file)

            #Print skipped tags
            if self.verbose_skipped_tags:
                self.print_skipped_tags()

        except ET.ParseError as e:
            self.log(f"Error parsing XML file: {e}")

    def convert_note_to_html(self, note_element):
        if note_element is None:
            return ''
        note_html = '**Note:** '

        # Include text before the first child element (if any)
        head_text = note_element.text or ''
        note_html += head_text

        # Process each child element within the note
        for child in note_element:
            if child.tag == 'pos':
                note_html += self.convert_pos_to_html(child)
            elif child.tag == 'b':
                note_html += f'**{child.text}**' if child.text else ''
            else:
                note_html += child.text if child.text else ''
            
            # Append tail text for each child
            if child.tail:
                note_html += child.tail

        note_html += '\n\n'
        return note_html

    def convert_xml_to_md_content(self, topic_element):
        """Converts a main topic with many sections to HTML."""
        if topic_element is None:
            return ''

        sections = topic_element.findall('.//section')
        return ''.join(self.convert_section_to_html(section) for section in tqdm(sections, desc="Processing Sections"))

    def create_html_comment(self, text):
        return f'<!-- {text} --> \n'

    def convert_section_to_html(self, section):
        """Converts an individual section to HTML."""

        #Reset the current_list_position
        self.current_pli_list_position = 0

        title_text = self.get_text(section.find('title'))
        section_id = section.get('id', '')
        shortdesc_text = self.get_text(section.find('shortdesc'))

        html_parts = [self.create_html_comment(f'Start of section about {title_text}')]

        body_element = self.html_parser.get_body_element(section)

        is_sub_section = body_element is not None and len(body_element) > 0

        # Decide the tag for the title based on the presence of body content
        title_tag = '###' if is_sub_section else '##'
        html_parts.append(f'{title_tag} {title_text} \n\n')

        if shortdesc_text:
            html_parts.append(f'{shortdesc_text} \n\n')

        if body_element is not None:
            html_parts.append(self.convert_group_to_md(body_element))

        html_parts.append('\n\n')
        return ''.join(html_parts)
    
    def get_text(self, xml_element):
        """Returns the text of an XML element, or an empty string if the element is None."""
        return self.html_parser.get_text(xml_element)

    def create_heading(self, xml_element, heading_level=2):
        """Creates a heading element with the given level."""
        heading_text = self.get_text(xml_element)
      
        return f'\n{"#" * heading_level} {heading_text} \n'

    def convert_paragraph_to_html(self, p_element):
        if p_element is None:
            return ''
        paragraph_html = ''
        if p_element.text:
            paragraph_html += p_element.text
        for sub_element in p_element:
            if sub_element.tag == 'pos':
                paragraph_html += self.convert_pos_to_html(sub_element)
            elif sub_element.tag == 'xref':
                paragraph_html += self.convert_xref_to_html(sub_element)
            elif sub_element.tag == 'i':
                paragraph_html += f'*{sub_element.text}*'
            elif sub_element.tag == 'b':
                paragraph_html += f'**{sub_element.text}**'
            elif sub_element.tag == 'uicontrol':
                paragraph_html += f'**{sub_element.text}**'
            elif sub_element.tag == 'abbrev':
                paragraph_html += f'**{sub_element.text}**'
            elif sub_element.tag == 'inline-graphic':
                paragraph_html += self.html_parser.convert_graphic_to_html(sub_element)
            else:
                if sub_element.text:
                    paragraph_html += sub_element.text

            if sub_element.tail:
                paragraph_html += sub_element.tail


        #Close the paragraph
        paragraph_html += '\n\n'

        return paragraph_html
    
    def convert_normal_html_list(self, list_element, type='ol'):
        list_html = ''
        for li in list_element.findall('li'):
            list_html += '- '
            list_html += self.convert_group_to_md(li)
            list_html += '\n'
        return list_html
    
    def convert_steps_to_html(self, step_group_element, list_type='ol', start_pos=0):
        steps_html = ''
        steps_html += f'<{list_type} start="{start_pos + 1}" type={"a" if list_type == "ol" else "disc"}>'

        for element in step_group_element:
            if element.tag == 'step':
                steps_html += '- '
                for child in element:
                    if child.tag == 'p':
                        steps_html += self.convert_paragraph_to_html(child)
                    elif child.tag == 'note':
                        steps_html += self.convert_note_to_html(child)
                    elif child.tag == 'safetymessage':
                        steps_html += self.html_parser.convert_safetymessage_to_html(child)
                    elif child.tag == 'substeps':
                        steps_html += ''
                        for substep in child.findall('substep'):
                            steps_html += '- '
                            steps_html += self.convert_group_to_md(substep)
                            steps_html += '\n'
                        steps_html += '\n\n'
                    elif child.tag == 'table':
                        steps_html += self.html_parser.convert_table_to_html(child)
                    elif child.tag == 'valid':
                        steps_html += f'**Valid for:** {self.get_text(child)} '
                    elif child.tag == 'notvalid':
                        steps_html += f'**Not valid for:** {self.get_text(child)} '
                    else:
                        self.log_skipped_tag(child.tag, 'convert_steps_to_html')
                steps_html += ''
            
            elif element.tag == 'illustration':
                steps_html += f'{self.html_parser.convert_illustration_to_html(element)}'
            elif element.tag == 'note':
                steps_html += self.convert_note_to_html(element)
            elif element.tag == 'safetymessage':
                steps_html += self.html_parser.convert_safetymessage_to_html(element)
            elif element.tag == 'ul':
                steps_html += self.convert_normal_html_list(element, type='ul')
            elif element.tag == 'p':
                steps_html += self.convert_paragraph_to_html(element)  
            elif element.tag == 'illustrationtable': 
                steps_html += self.html_parser.convert_illustrationtable_to_html(element)
            elif element.tag == 'step-group':
                steps_html += self.convert_steps_to_html(element, list_type='ul', start_pos=start_pos)
            elif element.tag == 'valid':
                steps_html += f'**Valid for:** {self.get_text(element)} \n'
            elif element.tag == 'notvalid':
                steps_html += f'**Not valid for:** {self.get_text(element)} \note_html'
            else:
                self.log_skipped_tag(element.tag, 'convert_steps_to_html')
            
        steps_html += f'</{list_type}>'
        
        return steps_html
    
    def get_new_start_pos_illustration(self, illustration):
        # Initialize start_pos_illustration with the current start_pos
        start_pos_illustration = self.current_pli_list_position

        if illustration is not None:
            poslist = illustration.find('.//poslist')
            
            if poslist is not None:
                # Get all pli elements
                pli_elements = poslist.findall('.//poscol//pli')
                
                # Filter pli elements that don't have the prev attribute equal to 'pliref'
                pli_elements_filtered = [pli for pli in pli_elements if pli.get('prev') != 'pliref']
                
                start_pos_illustration += len(pli_elements_filtered)

        # Return the calculated start_pos_illustration
        return start_pos_illustration
    
    def convert_steps_ordered_to_html(self, steps_ordered_element):
        html_content = ''
        html_content += self.create_html_comment('The list below contains the different steps in order')
        html_content += ''

        start_pos = 0

        for child in steps_ordered_element:
            if child.tag == 'step-group':
                html_content += self.convert_steps_to_html(child, list_type='ol',start_pos=start_pos)
                start_pos += len(child.findall('.//step'))
                self.current_pli_list_position = self.get_new_start_pos_illustration(child.find('.//illustration'))
            elif child.tag == 'illustration':
                html_content += self.html_parser.convert_illustration_to_html(child)
                self.current_pli_list_position = self.get_new_start_pos_illustration(child.find('.//illustration'))
            elif child.tag == 'note':
                html_content += self.convert_note_to_html(child)
            elif child.tag == 'safetymessage':
                html_content += self.html_parser.convert_safetymessage_to_html(child)
            elif child.tag == 'p':
                html_content += self.convert_paragraph_to_html(child)
            elif child.tag == 'step':
                html_content += '- '
                html_content += self.convert_group_to_md(child)
                html_content += '\n'
                start_pos += 1
            elif child.tag == 'valid':
                html_content += f'**Valid for:** {self.get_text(child)} \n'
            else:
                self.log_skipped_tag(child.tag, 'convert_steps_ordered_to_html')

        html_content += '</ol>'
        return html_content


    def convert_group_to_md(self, group_element):
        """Converts a group element to HTML."""
        if group_element is None:
            return ''
        group_html = ''

        #get child and index
        for child, index in zip(group_element, range(len(group_element))):
            if child.tag == 'title':
                group_html += self.create_heading(child, heading_level=4)
            elif child.tag == 'safetymessage':
                group_html += self.html_parser.convert_safetymessage_to_html(child)
            elif child.tag in ['illustration', 'pdfbody']:   
                group_html += self.html_parser.convert_illustration_to_html(child)
            elif child.tag in ['group', 'body','section','procbody','procedure-section','substep','procedure-group','step']:
                group_html += self.convert_group_to_md(child)
            elif child.tag == 'steps-ordered':
                group_html += self.convert_steps_ordered_to_html(child)
            elif child.tag == 'p':
                group_html += self.convert_paragraph_to_html(child)
            elif child.tag in ['note', 'shortdesc']:
                group_html += self.convert_note_to_html(child)
            elif child.tag == 'table':
                group_html += self.html_parser.convert_table_to_html(child)
            elif child.tag in ['steps-unordered']:
                group_html += self.html_parser.convert_steps_to_html(child, list_type='ol')
            elif child.tag in ['ul', 'ol']:
                group_html += self.convert_normal_html_list(child, type=child.tag)
            elif child.tag == 'prereq':
                group_html += self.html_parser.convert_prereq_to_html(child)
            elif child.tag == 'illustrationtable': 
                group_html += self.html_parser.convert_illustrationtable_to_html(child)   
            elif child.tag == 'valid':
                group_html += f'**Valid for:** {self.get_text(child)} \n\n'
            elif child.tag == 'notvalid':
                group_html += f'**Not valid for:** {self.get_text(child)} \n\n'
            elif child.tag == 'substeps':
                steps_html = ''
                for substep in child.findall('substep'):
                    steps_html += '- '
                    steps_html += self.convert_group_to_md(substep)
                    steps_html += '\n'
                steps_html += '\n\n'
                group_html += steps_html
            else:
                self.log_skipped_tag(child.tag, 'convert_group_to_html')

        return group_html

    def save_to_md(self, md_content, filepath):
        """
        Saves the HTML content to a file with the given filepath.
        Adds the base CSS file to the HTML and sets the title.
        """

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(md_content)
        