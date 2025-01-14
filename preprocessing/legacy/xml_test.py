import xml.etree.ElementTree as ET
import pandas as pd

def get_text(element, default=''):
    """Extracts text from an XML element, returning a default if not found."""
    return ''.join(element.itertext()).strip() if element is not None else default

def add_pli_description_to_pos_tags(xml_tree):
    """
    Parses the XML file and adds information before the 'pos' tags with the information based of the 'pli' tags.
    Takes the XML file path as input and returns the XML tree.
    """
    # Parse the XML file
    root = xml_tree.getroot()

    # Create a dictionary to map 'pli' ids to their descriptions
    pli_descriptions = {pli.get('id'): get_text(pli.find('postxt')).replace('\n', ' ')
                        for pli in root.findall(".//pli") if pli.get('id')}

    # Update 'pos' tags with corresponding 'pli' descriptions
    for pos in root.findall(".//pos"):
        pos_id = pos.get('editref')
        #Remove the first #
        pos_id = pos_id[1:]
        if pos_id in pli_descriptions:
            pos.text = pli_descriptions[pos_id]

    # Return the xml tree
    return xml_tree

def get_element_text(element, default=''):
    """Helper function to get text from an XML element."""
    return element.text if element is not None else default

def get_body_element(section):
    """Finds the appropriate body element within a section."""
    for body_tag in ['body', 'procbody', 'steps-ordered']:
        body_element = section.find(body_tag)
        if body_element is not None:
            return body_element
    return None

def convert_section_to_html(section):
    """Converts an individual section to HTML."""
    title_text = get_element_text(section.find('title'))
    section_id = section.get('id', '')
    shortdesc_text = get_element_text(section.find('shortdesc'))

    html_content = f'<h1 id="{section_id}">{title_text}</h1>'
    if shortdesc_text:
        html_content += f'<p>{shortdesc_text}</p>'

    body_element = get_body_element(section)
    if body_element is not None:
        html_content += convert_group_to_html(body_element)

    return html_content

def convert_xml_to_html_content(topic_element):
    """Converts a main topic with many sections to HTML."""
    if topic_element is None:
        return ''

    sections = topic_element.findall('.//section')
    return ''.join(convert_section_to_html(section) for section in sections)

def convert_group_to_html(group_element):
    """Converts a group element to HTML."""
    if group_element is None:
        return ''
    group_html = ''
    for child in group_element:
        if child.tag == 'title':
            group_html += f'<h3>{child.text}</h3>'
        elif child.tag == 'pos':
            group_html += convert_pos_to_html(child)
        elif child.tag == 'pli':
            list = convert_pli_to_html([child])
            group_html += '<ol>' + list + '</ol>'
        elif child.tag == 'safetymessage':
            group_html += convert_safetymessage_to_html(child)
        elif child.tag in ['illustration', 'pdfbody']:
            group_html += convert_illustration_to_html(child)
        elif child.tag in ['group', 'body','section','procbody','steps-ordered','procedure-section','substep','procedure-group','step']:
            group_html += convert_group_to_html(child)
        elif child.tag == 'p':
            group_html += convert_paragraph_to_html(child)
        elif child.tag in ['note', 'shortdesc']:
            group_html += convert_note_to_html(child)
        elif child.tag == 'table':
            group_html += convert_table_to_html(child)
        elif child.tag in ['step-group','steps-unordered']:
            group_html += convert_steps_to_html(child)
        elif child.tag == 'ul':
            #add all the li elements
            group_html += '<ul>'
            for li in child.findall('li'):
                group_html += '<li>'
                group_html += convert_group_to_html(li)
                group_html += '</li>'
            group_html += '</ul>'
        elif child.tag == 'prereq':
            group_html += convert_prereq_to_html(child)
        elif child.tag == 'illustrationtable': 
            group_html += convert_illustrationtable_to_html(child)   

        elif child.tag == 'substeps':
            group_html += '<div class="substeps">' + convert_group_to_html(child) + '</div>'
        elif child.tag == 'valid':
            group_html += f'<p class="valid-tag">{child.text}</p>'

        elif child.tag == 'notvalid':
            group_html += f'<p class="notvalid-tag">{child.text}</p>'

        elif child.tag == 'ol':
            group_html += '<ol>'
            for li in child.findall('li'):
                group_html += '<li>'
                group_html += convert_group_to_html(li)
                group_html += '</li>'
            group_html += '</ol>'  
        else:
            print(f"Unrecognized tag: {child.tag}")
            print(ET.tostring(child, encoding='unicode'))  # Diagnostic print


    return group_html


def convert_prereq_to_html(prereq_element):
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

def convert_table_to_html(table_element):
    """Converts a table element to HTML."""
    table_html = '<table class="xml-table">'
    for tgroup in table_element.findall('.//tgroup'):
        table_html += '<tbody>'
        for row in tgroup.findall('.//row'):
            table_html += '<tr>'
            for entry in row.findall('.//entry'):
                table_html += '<td>'       
                table_html += convert_group_to_html(entry)
                table_html += '</td>'
            table_html += '</tr>'
        table_html += '</tbody>'
    table_html += '</table>'
    return table_html

def convert_pos_to_html(pos_element):
    href = pos_element.get('editref')
    text = pos_element.text or ''
    return f'<a href="{href}">{text}</a>'

def process_postxt_elements(postxt_element):
        """Process nested elements within <postxt> and return concatenated text."""
        if postxt_element is None:
            return ''
        
        text_content = ''
        for child in postxt_element:
            if child.tag == 'uicontrol':
                print(f"Found uicontrol: {child.text}")
                # Process <uicontrol> or other specific tags as needed
                text_content += f'<code>{child.text}</code>'
            else:
                # Append child text if it's a different or unrecognized tag
                text_content += child.text if child.text else ''
            
            # Append tail text of the child
            if child.tail:
                text_content += child.tail

        #Append the text of the postxt element
        text_content += postxt_element.text if postxt_element.text else ''
        return text_content

def convert_pli_to_html(pli_elements):
    list_items = []
    for pli in pli_elements:
        pli_id = pli.get("id", '')
        postxt_content = process_postxt_elements(pli.find("postxt"))
        list_items.append(f'<li id="{pli_id}">{postxt_content}</li>')

    return ''.join(list_items)


def load_mapping_from_csv(file_path):
    """
    Reads the encoding mapping from a CSV file and returns it as a dictionary.
    """
    mapping_df = pd.read_csv(file_path, index_col='FileName')
    return mapping_df.to_dict(orient='index')

def convert_xref_to_html(xref_element):
    if xref_element is None:
        return ''  # Return empty string if xref_element is None

    href = xref_element.get('href')
    if href is None:
        return xref_element.text if xref_element.text else ''  # Return text or empty string

    try:
        mapping = load_mapping_from_csv('./encoding_mapping.csv')
        filename = href.split('#')[0]
        if filename in mapping:
            new_href = mapping[filename]['Link']
            href_text = mapping[filename]['Title']
        else:
            new_href = href  # Fallback to original href if not found in mapping
            href_text = 'Reference'

        text = xref_element.text or href_text
        return f'<a href="{new_href}">{text}</a>'
    except Exception as e:
        print(f"Error in convert_xref_to_html: {e}")
        return ''  # Return empty string in case of any error
    href = xref_element.get('href')

    if href is None:
        return xref_element.text
    
    mapping = load_mapping_from_csv('./encoding_mapping.csv')
    filename = href.split('#')[0]
    if filename in mapping:
        new_href = mapping[filename]['Link']
        href_text = mapping[filename]['Title']
    else:
        new_href = href  # Fallback to original href if not found in mapping
        href_text = 'Reference'

    text = xref_element.text or href_text
    return f'<a href="{new_href}">{text}</a>'

def convert_steps_to_html(step_group_element):
    steps_html = '<ul>'
    for element in step_group_element:
        if element.tag == 'step':
            steps_html += '<li>'
            for child in element:
                if child.tag == 'p':
                    steps_html += convert_paragraph_to_html(child)
                elif child.tag == 'note':
                    steps_html += convert_note_to_html(child)
                elif child.tag == 'safetymessage':
                    steps_html += convert_safetymessage_to_html(child)
                elif child.tag == 'substeps':
                    steps_html += '<ul>'
                    for substep in child.findall('substep'):
                        steps_html += '<li>'
                        steps_html += convert_group_to_html(substep)
                        steps_html += '</li>'
                    steps_html += '</ul>'
                elif child.tag == 'table':
                    steps_html += convert_table_to_html(child)
                else:
                    print(f"Unrecognized tag: {child.tag}")
            steps_html += '</li>'
        
        elif element.tag == 'illustration':
            steps_html += f'{convert_illustration_to_html(element)}'
        elif element.tag == 'note':
            steps_html += convert_note_to_html(element)
        elif element.tag == 'safetymessage':
            steps_html += convert_safetymessage_to_html(element)
        elif element.tag == 'ul':
            steps_html += '<ul>'
            for li in element.findall('li'):
                steps_html += '<li>'
                steps_html += convert_group_to_html(li)
                steps_html += '</li>'
            steps_html += '</ul>'
        elif element.tag == 'p':
            steps_html += convert_paragraph_to_html(element)  
        elif element.tag == 'illustrationtable': 
            steps_html += convert_illustrationtable_to_html(element)        

    steps_html += '</ul>'
    
    return steps_html

def convert_note_to_html(note_element):
    if note_element is None:
        return ''
    note_html = '<p><strong>Note:</strong> '

    # Include text before the first child element (if any)
    head_text = note_element.text or ''
    note_html += head_text

    # Process each child element within the note
    for child in note_element:
        if child.tag == 'pos':
            note_html += convert_pos_to_html(child)
        elif child.tag == 'b':
            note_html += f'<b>{child.text}</b>' if child.text else ''
        else:
            note_html += child.text if child.text else ''
        
        # Append tail text for each child
        if child.tail:
            note_html += child.tail

    note_html += '</p>'
    return note_html

def convert_illustrationtable_to_html(illustrationtable_element, base_img_path='./all_xml_data/graphics/png/'):
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
            image_href = base_img_path + image_href
            illustrationtable_html += f'<img src="{image_href}" alt="Illustration"/>'

        # Process illustration text if present
        illustration_text_element = illustrationcol.find('illustrationtext')
        if illustration_text_element is not None:
            illustration_text = ''.join(illustration_text_element.itertext()).strip()
            illustrationtable_html += f'<div class="illustration-text">{illustration_text}</div>'

        illustrationtable_html += '</div>'

    # Process poslist if present
    poslist_element = illustrationtable_element.find('poslist')
    if poslist_element is not None:
        for poscol in poslist_element.findall('poscol'):
            list_html = convert_pli_to_html(poscol.findall('pli'))
            illustrationtable_html += '<ol>' + list_html + '</ol>'

    illustrationtable_html += '</div>'
    return illustrationtable_html

def convert_paragraph_to_html(p_element):
    if p_element is None:
        return ''
    paragraph_html = '<p>'
    if p_element.text:
        paragraph_html += p_element.text
    for sub_element in p_element:
        if sub_element.tag == 'pos':
            paragraph_html += convert_pos_to_html(sub_element)
        elif sub_element.tag == 'xref':
            paragraph_html += convert_xref_to_html(sub_element)
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

def convert_safetymessage_to_html(safetymessage_element):
    hazardidentification = safetymessage_element.find('hazardidentification').text
    precautions_element = safetymessage_element.find('.//precautions')
    consequence_element = safetymessage_element.find('.//consequence')

    # Process the precautions text and any nested elements
    precautions_html = process_nested_elements(precautions_element)
    consequence_html = process_nested_elements(consequence_element)

    return f'<div class="safetymessage"><p>{hazardidentification}</p>{precautions_html}{consequence_html}</div>'

def process_nested_elements(element):
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
            html_content += convert_xref_to_html(sub_element)
        elif sub_element.tag == 'pos':
            html_content += convert_pos_to_html(sub_element)
        elif sub_element.tag == 'b':
            html_content += f'<b>{sub_element.text}</b>'
        elif sub_element.tag == 'i':
            html_content += f'<i>{sub_element.text}</i>'
        elif sub_element.tag == 'abbrev':
            html_content += f'<b title="{sub_element.get("title")}">{sub_element.text}</b>'

        if sub_element.tail:
            html_content += sub_element.tail

    return f'<p>{html_content}</p>'

def convert_illustration_to_html(illustration_element, base_img_path='./all_xml_data/graphics/png/'):
    if illustration_element is None:
        return ''

    illustration_html = ''
    for child in illustration_element:
        if child.tag == 'graphic':
            image_href = child.get('href').replace('.eps', '.png')
            image_href = base_img_path + image_href
            illustration_html += f'<img src="{image_href}" alt="Illustration">'
        elif child.tag == 'measurement':
            measurement_text_element = child.find('measurementtext')
            if measurement_text_element is not None:
                measurement_text = ''.join(measurement_text_element.itertext()).strip()
                illustration_html += f'<div class="measurement">{measurement_text}</div>'
        elif child.tag == 'poslist':
            list_html = ''
            for poscol in child.findall('poscol'):
                list_html += convert_pli_to_html(poscol.findall('pli'))
            illustration_html += '<ol>' + list_html + '</ol>'
        elif child.tag == 'illustrationtext':
            illustration_text_html = convert_group_to_html(child)
            illustration_html += illustration_text_html
        # Add handling for other tags if needed
        else:
            print(f"Unrecognized tag: {child.tag}")

    return illustration_html



def save_to_html(html_content, filepath, main_title='Documentation', base_css_path='./style.css'):
    """
    Saves the HTML content to a file with the given filepath.
    Adds the base CSS file to the HTML and sets the title.
    """
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{main_title}</title>
        <link rel="stylesheet" type="text/css" href="{base_css_path}">
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


def convert_xml_to_text(xml_root,filename):
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

        print(f"Text extracted to {filename}")

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")


def xml_to_html(filepath='./section_4.xml',output_file='./test.html'):
    """
    Parses the XML file and converts it to HTML.
    Takes the XML file path as input and returns the HTML content.
    """
    try:
        xml_tree = ET.parse(filepath)

        # Add pli descriptions to pos tags (to make the links work correctly)
        xml_tree = add_pli_description_to_pos_tags(xml_tree)

        # Convert the XML to HTML
        html_content = convert_xml_to_html_content(xml_tree.getroot())
        save_to_html(html_content, output_file)

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")


if __name__ == "__main__":
    xml_to_html()

