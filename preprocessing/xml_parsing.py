import xml.etree.ElementTree as ET

def add_pli_description_to_pos_tags(xml_tree):
    """
    Parses the XML file and adds information before the 'pos' tags with the information based of the 'pli' tags.
    Takes the XML file path as input and returns the XML tree.
    """
    # Parse the XML file
    root = xml_tree.getroot()

    # Create a dictionary to map 'pli' ids to their descriptions
    pli_descriptions = {}
    for pli in root.findall(".//pli"):
        pli_id = pli.get('id')
        pli_text_elements = pli.find('postxt')
        if pli_id and pli_text_elements is not None:
            pli_text = ''.join(pli_text_elements.itertext()).strip()
            pli_descriptions[pli_id] = pli_text.replace('\n', ' ')


    # Update 'pos' tags with corresponding 'pli' descriptions
    for pos in root.findall(".//pos"):
        pos_id = pos.get('editref')
        #Remove the first #
        pos_id = pos_id[1:]
        if pos_id in pli_descriptions:
            pos.text = pli_descriptions[pos_id]

    # Return the xml tree
    return xml_tree

def convert_topic_to_html(topic_element):
    if topic_element is None:
        return ''

    html_content = ''
    sections = topic_element.findall('.//section')

    for section in sections:
        # Process each section
        title = section.find('title')
        title_text = title.text if title is not None else ''

        shortdesc = section.find('shortdesc')
        shortdesc_text = shortdesc.text if shortdesc is not None else ''

        body_element = section.find('body')

        if body_element is None:
            body_element = section.find('procbody')    
        if body_element is None:
            body_element = section.find('steps-ordered')        

        # Append section's content to the overall HTML
        html_content += f'<h1>{title_text}</h1>'
        if shortdesc_text:
            html_content += f'<p>{shortdesc_text}</p>'

        html_content += convert_group_to_html(body_element)

    return html_content

def convert_group_to_html(group_element):
    if group_element is None:
        return ''
    group_html = ''
    for child in group_element:
        if child.tag == 'title':
            group_html += f'<h3>{child.text}</h3>'
        if child.tag == 'pos':
            group_html += convert_pos_to_html(child)
        elif child.tag == 'pli':
            list = convert_pli_to_html([child])
            group_html += '<ol>' + list + '</ol>'
        elif child.tag == 'safetymessage':
            group_html += convert_safetymessage_to_html(child)
        elif child.tag in ['illustration', 'pdfbody']:
            group_html += convert_illustration_to_html(child)
        elif child.tag in ['group', 'body','section','procbody','steps-ordered','procedure-section','substep']:
            group_html += convert_group_to_html(child)
        elif child.tag == 'p':
            group_html += convert_paragraph_to_html(child)
        elif child.tag in ['note', 'shortdesc']:
            group_html += f'<p><strong>Note:</strong> {child.text}</p>'
        elif child.tag == 'table':
            group_html += convert_table_to_html(child)
        elif child.tag == 'step-group':
            group_html += convert_steps_to_html(child)
        elif child.tag == 'ul':
            #add all the li elements
            group_html += '<ul>'
            for li in child.findall('li'):
                group_html += '<li>'
                group_html += convert_group_to_html(li)
                group_html += '</li>'
            group_html += '</ul>'

        # Add more cases as needed for other tags within <group>
    return group_html

def convert_table_to_html(table_element):
    table_html = '<table class="xml-table">'
    for tgroup in table_element.findall('.//tgroup'):
        table_html += '<tbody>'
        for row in tgroup.findall('.//row'):
            table_html += '<tr>'
            for entry in row.findall('.//entry'):
                table_html += '<td>'
                entry_content = ''.join(entry.itertext()).strip()
                table_html += entry_content
                table_html += '</td>'
            table_html += '</tr>'
        table_html += '</tbody>'
    table_html += '</table>'
    return table_html

def convert_pos_to_html(pos_element):
    href = pos_element.get('editref')
    text = pos_element.text or ''
    return f'<a href="{href}">{text}</a>'


def convert_pli_to_html(pli_elements):
    list_items = [f'<li id="{pli.get("id")}">{pli.find("postxt").text}</li>' for pli in pli_elements]
    return ''.join(list_items)

def convert_xref_to_html(xref_element):
    href = xref_element.get('href')

    if href is None:
        return xref_element.text

    text = xref_element.text or 'Reference'
    return f'<a href="{href}">{text}</a>'

def convert_steps_to_html(step_group_element):
    steps_html = '<ul>'
    for element in step_group_element:
        if element.tag == 'step':
            steps_html += '<li>'
            for child in element:
                if child.tag == 'p':
                    steps_html += convert_paragraph_to_html(child)
                if child.tag == 'note':
                    steps_html += f'<p><strong>Note:</strong> {child.text}</p>'
                else:
                    steps_html += convert_group_to_html(child)

            steps_html += '</li>'
        elif element.tag == 'illustration':
            steps_html += f'{convert_illustration_to_html(element)}'
        elif element.tag == 'note':
            steps_html += f'<p><strong>Note:</strong> {element.text}</p>'
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
        else:
            print(f'Unknown tag: {element.tag}')
            steps_html += convert_group_to_html(element)

    steps_html += '</ul>'
    return steps_html

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
        # Handle other tags if needed

        if sub_element.tail:
            html_content += sub_element.tail

    return f'<p>{html_content}</p>'

def convert_illustration_to_html(illustration_element):
    image_href = illustration_element.find('graphic').get('href')

    #Switch .eps to .png
    image_href = image_href.replace('.eps', '.png')
    base_path = './all_xml_data/graphics/png/'
    image_href = base_path + image_href

    img_html = f'<img src="{image_href}" alt="Illustration">'
    
    list_html = ''
    poslists = illustration_element.findall('poslist')
    if poslists:
        for poslist in poslists:
            for poscol in poslist.findall('poscol'):
                list_html += convert_pli_to_html(poscol.findall('pli'))

    list_html = '<ol>' + list_html + '</ol>'

    # Check for illustrationtext and add it to the HTML
    illustration_text_element = illustration_element.find('illustrationtext')
    if illustration_text_element is not None:
        illustration_text_html = convert_group_to_html(illustration_text_element)
    else:
        illustration_text_html = ''

    return img_html + list_html + illustration_text_html


def save_to_html(html_content, filepath):
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Water Supply Documentation</title>
        <link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body>
        <div class="container">
            {html_content}
        </div>
    </body>
    </html>
    """
    with open(filepath, 'w') as f:
        f.write(html_template)

def convert_xml_to_text(xml_root):
    try:

        # Extract text from XML
        text_content = []
        for elem in xml_root.iter():
            if elem.text:
                text_content.append(elem.text.strip())

        # Write the extracted text to a text file
        with open('text.txt', 'w', encoding='utf-8') as file:
            file.write('\n'.join(text_content))

        print(f"Text extracted to text.txt")

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")


filepath =  './section_4.xml' #'./all_xml_data/3030000-0126/xml/0005252812.xml'
xml_tree = ET.parse(filepath)
xml_tree = add_pli_description_to_pos_tags(xml_tree)
xml_root = xml_tree.getroot()
#convert_xml_to_text(xml_root)
html_content = convert_topic_to_html(xml_root)
save_to_html(html_content, './test.html')

