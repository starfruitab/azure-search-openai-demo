import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm

class XMLToHTMLConverter:
    mapping = None
    
    def __init__(self, base_img_path='https://stsp3lqew6l65ci.blob.core.windows.net/illustrations/', mapping_path='./output/mapping.csv', base_css_path='./style.css', verbose=False):
        self.base_img_path = base_img_path
        self.base_css_path = base_css_path
        self.verbose = verbose
        self.mapping = self.load_mapping_from_csv(mapping_path)

        # Create a dictionary to store references
        self.references = {}

    def log(self, message):
        if self.verbose:
            print(message)

    def save_to_html(self, html_content, filepath, main_title='Documentation'):
        """
        Saves the HTML content to a file with the given filepath.
        Adds the base CSS file to the HTML and sets the title.
        """
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{main_title}</title>
            <link rel="stylesheet" type="text/css" href="{self.base_css_path}">
        </head>
        <body>
            <div class="container">
                {html_content}
            </div>
        </body>
        </html>
        """
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(html_template.format(html_content))
    
    def get_text(self, element, default=''):
        """Extracts text from an XML element, returning a default if not found."""
        if element is None:
            return default
        if len(element) == 0:
            return element.text or default
        return ''.join(element.itertext()).strip() if element is not None else default

    def add_pli_description_to_pos_tags(self, xml_tree):
        """
        Parses the XML file and adds information before the 'pos' tags with the information based of the 'pli' tags.
        Takes the XML file path as input and returns the XML tree.
        """
        # Parse the XML file
        root = xml_tree.getroot()

        # Create a dictionary to map 'pli' ids to their descriptions
        pli_descriptions = {pli.get('id'): self.get_text(pli.find('postxt'))
                            for pli in root.findall(".//pli") if pli.get('id')}

        # Update 'pos' tags with corresponding 'pli' descriptions
        for pos in root.findall(".//pos"):
            pos_id = pos.get('editref')
            #Remove the first #
            pos_id = pos_id[1:]
            if pos_id in pli_descriptions:
                pos.text = pli_descriptions[pos_id]

        # Update all pliref -> replace with pli
        for pliref in root.findall(".//pliref"):
            pliref_id = pliref.get('editref')
            #Remove the first #
            if pliref_id is not None:
                    
                pliref_id = pliref_id[1:]
                if pliref_id in pli_descriptions:
                    # Replace the pliref tag with pli
                    pliref.tag = 'pli'

                    #add postxt element
                    postxt = ET.SubElement(pliref, 'postxt')
                    postxt.text = pli_descriptions[pliref_id]

                    # add prev attribute
                    pliref.set('prev', 'pliref')
                    pliref.set('reference', pliref_id)

        # Return the xml tree
        return xml_tree

    def convert_section_to_html(self, section):
        """Converts an individual section to HTML."""
        title_text = self.get_text(section.find('title'))
        section_id = section.get('id', '')
        shortdesc_text = self.get_text(section.find('shortdesc'))

        html_parts = [self.create_html_comment(f'Start of section about {title_text}')]
        html_parts.append(f'<section id="{section_id}" class="section">')

        body_element = self.get_body_element(section)
        print(body_element, title_text)
        # Decide the tag for the title based on the presence of body content
        title_tag = 'h3' if body_element is not None else 'h2'
        html_parts.append(f'<{title_tag}>{title_text}</{title_tag}>')

        if shortdesc_text:
            html_parts.append(f'<p>{shortdesc_text}</p>')

        if body_element is not None:
            html_parts.append(self.convert_group_to_html(body_element))

        html_parts.append('</section>')
        return ''.join(html_parts)
    
    def get_body_element(self, section):
        """Finds the appropriate body element within a section."""
        for body_tag in ['body', 'procbody','pdfbody']:
            body_element = section.find(body_tag)
            if body_element is not None:
                return body_element
        return None
    
    def convert_xml_to_html_content(self, topic_element):
        """Converts a main topic with many sections to HTML."""
        if topic_element is None:
            return ''

        sections = topic_element.findall('.//section')
        return ''.join(self.convert_section_to_html(section) for section in tqdm(sections, desc="Processing Sections"))

    def convert_group_to_html(self, group_element, before_tag=None):
        """Converts a group element to HTML."""
        if group_element is None:
            return ''
        group_html = ''

        #get child and index
        for child, index in zip(group_element, range(len(group_element))):
            if child.tag == 'title':
                group_html += f'<h4>{self.get_text(child)}</h4>'
            elif child.tag == 'pos':
                group_html += self.convert_pos_to_html(child)
            elif child.tag == 'pli':
                list = self.convert_pli_to_html([child])
                group_html += '<ol>' + list + '</ol>'
            elif child.tag == 'safetymessage':
                group_html += self.convert_safetymessage_to_html(child)
            elif child.tag in ['illustration', 'pdfbody']:   
                group_html += self.convert_illustration_to_html(child)
            elif child.tag in ['group', 'body','section','procbody','procedure-section','substep','procedure-group','step']:
                group_html += self.convert_group_to_html(child, before_tag=child.tag)
            elif child.tag == 'steps-ordered':
                group_html += self.convert_steps_ordered_to_html(child)
            elif child.tag == 'p':
                group_html += self.convert_paragraph_to_html(child)
            elif child.tag in ['note', 'shortdesc']:
                group_html += self.convert_note_to_html(child)
            elif child.tag == 'table':
                group_html += self.convert_table_to_html(child)
            elif child.tag in ['steps-unordered']:
                group_html += self.convert_steps_to_html(child, list_type='ol')
            elif child.tag in ['ul', 'ol']:
                group_html += self.convert_normal_html_list(child, type=child.tag)
            # elif child.tag == 'prereq':
            #     group_html += convert_prereq_to_html(child)
            elif child.tag == 'illustrationtable': 
                group_html += self.convert_illustrationtable_to_html(child)     

        return group_html
    
    def convert_steps_ordered_to_html(self, steps_ordered_element):
        html_content = ''
        html_content += self.create_html_comment('The list below contains the different steps in order')
        html_content += '<ol>'

        start_pos = 0
        start_pos_illustration = 0

        for child in steps_ordered_element:
            if child.tag == 'step-group':
                html_content += self.convert_steps_to_html(child, list_type='ol',start_pos=start_pos,start_pos_illustration=start_pos_illustration)
                start_pos += len(child.findall('.//step'))
                start_pos_illustration = self.get_new_start_pos_illustration(start_pos_illustration, child.find('.//illustration'))
            elif child.tag == 'illustration':
                html_content += self.convert_illustration_to_html(child,start_pos_illustration=start_pos_illustration)
                start_pos_illustration = self.get_new_start_pos_illustration(start_pos_illustration, child)
            elif child.tag == 'note':
                html_content += self.convert_note_to_html(child)
            elif child.tag == 'safetymessage':
                html_content += self.convert_safetymessage_to_html(child)
            elif child.tag == 'p':
                html_content += self.convert_paragraph_to_html(child)
            elif child.tag == 'step':
                html_content += '<li>'
                html_content += self.convert_group_to_html(child)
                html_content += '</li>'
                start_pos += 1

        html_content += '</ol>'
        return html_content
    
    def get_new_start_pos_illustration(self, start_pos, illustration):
        # Initialize start_pos_illustration with the current start_pos
        start_pos_illustration = start_pos

        if illustration is not None:
            poslist = illustration.find('.//poslist')
            
            if poslist is not None and poslist.get('contd') != 'no':
                # Get all pli elements
                pli_elements = poslist.findall('.//poscol//pli')
                
                # Filter pli elements that don't have the prev attribute equal to 'pliref'
                pli_elements_filtered = [pli for pli in pli_elements if pli.get('prev') != 'pliref']
                
                start_pos_illustration += len(pli_elements_filtered)
            else:
                start_pos_illustration = 0

        # Return the calculated start_pos_illustration
        return start_pos_illustration



    
    def convert_normal_html_list(self, list_element, type='ol'):
        list_html = f'<{type}>'
        for li in list_element.findall('li'):
            list_html += '<li>'
            list_html += self.convert_group_to_html(li)
            list_html += '</li>'
        list_html += f'</{type}>'
        return list_html

    def convert_prereq_to_html(self, prereq_element):
        if prereq_element is None:
            return ''
        prereq_html = '<div class="prerequisite"><strong>Prerequisite:</strong><ul>'

        # Process each child element within the prereq
        for child in prereq_element:
            prereq_html += '<li>'

            if child.tag in ['machine-status', 'special-equipment', 'spc-reference', 'rk-ref']:
                for sub_child in child:
                    prereq_html += f'<span class="prereq-item">{sub_child.tag.replace("-", " ").capitalize()}:</span> ' if sub_child.text else ''
                    prereq_html += f'<span class="prereq-value">{sub_child.text}</span> ' if sub_child.text else ''
                    # Append tail text for each sub_child
                    if sub_child.tail:
                        prereq_html += sub_child.tail.strip() + ' '

            prereq_html += '</li>'

        prereq_html += '</ul></div>'
        return prereq_html

    def convert_table_to_html(self, table_element):
        """Converts a table element to HTML."""
        table_html = '<table class="xml-table">'
        for tgroup in table_element.findall('.//tgroup'):
            table_html += '<tbody>'
            for row in tgroup.findall('.//row'):
                table_html += '<tr>'
                for entry in row.findall('.//entry'):
                    table_html += '<td>'       
                    table_html += self.convert_group_to_html(entry)
                    table_html += '</td>'
                table_html += '</tr>'
            table_html += '</tbody>'
        table_html += '</table>'
        return table_html

    def convert_pos_to_html(self, pos_element):
        href = pos_element.get('editref')
        text = pos_element.text or ''
        return f'<a href="{href}">{text}</a>'

    def process_postxt_elements(self, postxt_element):
            """Process nested elements within <postxt> and return concatenated text."""
            if postxt_element is None:
                return ''
            
            text_content = ''
            for child in postxt_element:
                if child.tag == 'uicontrol':
                    # Process <uicontrol> or other specific tags as needed
                    text_content += f'<code>{child.text}</code>'
                elif child.tag == 'abbrev':
                    text_content += f'<b title="{child.get("title")}">{child.text}</b>'
                elif child.tag == 'softtxt':
                    text_content += f'<i>{child.text}</i>'
                else:
                    # Append child text if it's a different or unrecognized tag
                    text_content += child.text if child.text else ''
                
                # Append tail text of the child
                if child.tail:
                    text_content += child.tail

            #Append the text of the postxt element
            text_content += postxt_element.text if postxt_element.text else ''
            return text_content

    def convert_pli_to_html(self, pli_elements):
        list_items = []
        for pli in pli_elements:
            pli_id = pli.get("id", "")
            prev = pli.get("prev", "")

            postxt_content = self.process_postxt_elements(pli.find("postxt"))

            if prev == 'pliref':
                reference = pli.get("reference", "")
                list_items.append(f'<li id="{pli_id}" reference="{reference}">{postxt_content}</li>')
            else:
                list_items.append(f'<li id="{pli_id}">{postxt_content}</li>')
        return ''.join(list_items)

    def load_mapping_from_csv(self, file_path):
        """
        Reads the encoding mapping from a CSV file and returns it as a dictionary.
        """
        mapping_df = pd.read_csv(file_path, index_col='FileName')
        mapping = mapping_df.to_dict(orient='index')
        return mapping

    def convert_xref_to_html(self, xref_element):
        href = xref_element.get('href')

        if href is None:
            return xref_element.text or ''
        
        filename = href.split('#')[0]
        if filename in self.mapping:
            new_href = self.mapping[filename]['Link']
            href_text = self.mapping[filename]['Title']
        else:
            new_href = href  # Fallback to original href if not found in mapping
            href_text = 'Reference'

        text = xref_element.text or href_text
        return f'<a href="{new_href}">{text}</a>'

    def convert_steps_to_html(self, step_group_element, list_type='ol', start_pos=0, start_pos_illustration=0):
        steps_html = ''
        steps_html += f'<{list_type} start="{start_pos + 1}" type={"a" if list_type == "ol" else "disc"}>'

        for element in step_group_element:
            if element.tag == 'step':
                steps_html += '<li>'
                for child in element:
                    if child.tag == 'p':
                        steps_html += self.convert_paragraph_to_html(child)
                    elif child.tag == 'note':
                        steps_html += self.convert_note_to_html(child)
                    elif child.tag == 'safetymessage':
                        steps_html += self.convert_safetymessage_to_html(child)
                    elif child.tag == 'substeps':
                        steps_html += '<ul>'
                        for substep in child.findall('substep'):
                            steps_html += '<li>'
                            steps_html += self.convert_group_to_html(substep)
                            steps_html += '</li>'
                        steps_html += '</ul>'
                    elif child.tag == 'table':
                        steps_html += self.convert_table_to_html(child)
                steps_html += '</li>'
            
            elif element.tag == 'illustration':
                steps_html += f'{self.convert_illustration_to_html(element,start_pos_illustration=start_pos_illustration)}'
            elif element.tag == 'note':
                steps_html += self.convert_note_to_html(element)
            elif element.tag == 'safetymessage':
                steps_html += self.convert_safetymessage_to_html(element)
            elif element.tag == 'ul':
                steps_html += self.convert_normal_html_list(element, type='ul')
            elif element.tag == 'p':
                steps_html += self.convert_paragraph_to_html(element)  
            elif element.tag == 'illustrationtable': 
                steps_html += self.convert_illustrationtable_to_html(element)
            elif element.tag == 'step-group':
                steps_html += self.convert_steps_to_html(element, list_type='ul', start_pos=start_pos, start_pos_illustration=start_pos_illustration)
            
        steps_html += f'</{list_type}>'
        
        return steps_html

    def convert_note_to_html(self, note_element):
        if note_element is None:
            return ''
        note_html = '<p><strong>Note:</strong> '

        # Include text before the first child element (if any)
        head_text = note_element.text or ''
        note_html += head_text

        # Process each child element within the note
        for child in note_element:
            if child.tag == 'pos':
                note_html += self.convert_pos_to_html(child)
            elif child.tag == 'b':
                note_html += f'<b>{child.text}</b>' if child.text else ''
            else:
                note_html += child.text if child.text else ''
            
            # Append tail text for each child
            if child.tail:
                note_html += child.tail

        note_html += '</p>'
        return note_html

    def convert_illustrationtable_to_html(self, illustrationtable_element):
        """
        Converts illustrationtable element to HTML format.
        """
        if illustrationtable_element is None:
            return ''

        illustrationtable_html = '<div class="illustration-table">'

        # Process each illustrationcol element
        for illustrationcol in illustrationtable_element.findall('.//illustrationcol'):
            illustrationtable_html += '<div class="illustration-col">'
            
            graphic_element = illustrationcol.find('graphic')
            if graphic_element is not None:
                image_href = graphic_element.get('href').replace('.eps', '.png')
                image_href = self.base_img_path + image_href
                illustrationtable_html += f'<img src="{image_href}" alt="Illustration" class="illustration" loading="lazy" />'

            # Process illustration text if present
            illustration_text_element = illustrationcol.find('illustrationtext')
            if illustration_text_element is not None:
                illustration_text = ''.join(illustration_text_element.itertext()).strip()
                illustrationtable_html += f'<div class="illustration-text">{illustration_text}</div>'

            illustrationtable_html += '</div>'

        # Process poslist if present
        poslist_element = illustrationtable_element.find('poslist')
        if poslist_element is not None:
            list_html = ''
            for poscol in poslist_element.findall('poscol'):
                list_html += self.convert_pli_to_html(poscol.findall('pli'))
            illustrationtable_html += '<ol>' + list_html + '</ol>'

        illustrationtable_html += '</div>'
        return illustrationtable_html

    def convert_paragraph_to_html(self, p_element):
        if p_element is None:
            return ''
        paragraph_html = '<p>'
        if p_element.text:
            paragraph_html += p_element.text
        for sub_element in p_element:
            if sub_element.tag == 'pos':
                paragraph_html += self.convert_pos_to_html(sub_element)
            elif sub_element.tag == 'xref':
                paragraph_html += self.convert_xref_to_html(sub_element)
            elif sub_element.tag == 'i':
                paragraph_html += f'<i>{sub_element.text}</i>'
            elif sub_element.tag == 'b':
                paragraph_html += f'<b>{sub_element.text}</b>'
            elif sub_element.tag == 'uicontrol':
                paragraph_html += f'<code>{sub_element.text}</code>'
            elif sub_element.tag == 'abbrev':
                paragraph_html += f'<b title="{sub_element.get("title")}">{sub_element.text}</b>'
            else:
                if sub_element.text:
                    paragraph_html += sub_element.text

            if sub_element.tail:
                paragraph_html += sub_element.tail

        paragraph_html += '</p>'
        return paragraph_html

    def convert_safetymessage_to_html(self, safetymessage_element):
        hazardidentification = safetymessage_element.find('hazardidentification').text
        precautions_element = safetymessage_element.find('.//precautions')
        consequence_element = safetymessage_element.find('.//consequence')

        # Process the precautions text and any nested elements
        precautions_html = self.process_nested_elements(precautions_element)
        consequence_html = self.process_nested_elements(consequence_element)

        return f'<div class="safetymessage"><p>{hazardidentification}</p>{precautions_html}{consequence_html}</div>'

    def create_html_comment(self, text):
        return f'<!-- {text} -->'

    def process_nested_elements(self, element):
        """
        Processes an element's text and its nested elements, returning HTML string.
        """
        if element is None:
            return ''
        html_content = ''
        if element.text:
            html_content += element.text

        for sub_element in element:
            if sub_element.tag == 'xref':
                html_content += self.convert_xref_to_html(sub_element)
            elif sub_element.tag == 'pos':
                html_content += self.convert_pos_to_html(sub_element)
            elif sub_element.tag == 'b':
                html_content += f'<b>{sub_element.text}</b>'
            elif sub_element.tag == 'i':
                html_content += f'<i>{sub_element.text}</i>'
            elif sub_element.tag == 'abbrev':
                html_content += f'<b title="{sub_element.get("title")}">{sub_element.text}</b>'
            elif sub_element == 'softtxt':
                html_content += f'<i>{sub_element.text}</i>'

            #Add the tail text
            if sub_element.tail:
                html_content += sub_element.tail

        return f'<p>{html_content}</p>'

    def convert_illustration_to_html(self, illustration_element, start_pos_illustration=0):
        if illustration_element is None:
            return ''

        illustration_html = self.create_html_comment('The image below is used to illustrate the steps in the procedure (explained above in text)')
        illustration_html += '<div>'
        for child in illustration_element:
            if child.tag == 'graphic':
                image_href = child.get('href').replace('.eps', '.png')
                image_href = self.base_img_path + image_href
                
                illustration_html += f'<img src="{image_href}" alt="Illustration" class="illustration" loading="lazy" />'
            elif child.tag == 'measurement':
                measurement_text_element = child.find('measurementtext')
                if measurement_text_element is not None:
                    measurement_text = ''.join(measurement_text_element.itertext()).strip()
                    illustration_html += f'<div class="measurement">{measurement_text}</div>'
            elif child.tag == 'poslist':
                list_html = ''
                for poscol in child.findall('poscol'):
                    #Loop through all the children 
                    for children in poscol:
                        if children.tag == 'pli':
                            list_html += self.convert_pli_to_html([children])

                illustration_html += self.create_html_comment('The list below explains the different parts of the illustration.')
                illustration_html += f'<ol start="{start_pos_illustration + 1}">' + list_html + '</ol>'
            elif child.tag == 'illustrationtext':
                illustration_text_html = self.convert_group_to_html(child)
                illustration_html += illustration_text_html

        illustration_html += '</div>'
        return illustration_html


    def convert_xml_to_text(self,xml_root,filename):
        """
        Extracts text from an XML file and writes it to a text file.
        Creates a new text file with the given filename.
        """
        try:

            # Extract text from XML
            text_content = []
            for elem in xml_root.iter():
                if elem.text:
                    text_content.append(elem.text.strip())

            # Write the extracted text to a text file
            with open(filename, 'w', encoding='utf-8') as file:
                file.write('\n'.join(text_content))

        except ET.ParseError as e:
            self.log(f"Error parsing XML file: {e}")

    def xml_to_html(self,filepath='./main.xml',output_file='./main.html'):
        """
        Parses the XML file and converts it to HTML.
        Takes the XML file path as input and returns the HTML content.
        """
        try:
            xml_tree = ET.parse(filepath)

            # Add pli descriptions to pos tags (to make the links work correctly)
            xml_tree = self.add_pli_description_to_pos_tags(xml_tree)

            # Convert the XML to HTML
            html_content = self.convert_xml_to_html_content(xml_tree.getroot())

            #Remove all /n from the text
            html_content = html_content.replace('\n', ' ')

            self.save_to_html(html_content, output_file)

        except ET.ParseError as e:
            self.log(f"Error parsing XML file: {e}")