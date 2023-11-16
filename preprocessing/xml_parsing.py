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
        pli_text = pli.find('postxt').text if pli.find('postxt') is not None else ''
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
    title = topic_element.find('title').text or ''
    shortdesc = topic_element.find('shortdesc').text or ''
    body_element = topic_element.find('body')

    html_content = f'<h1>{title}</h1>'
    if shortdesc:
        html_content += f'<p>{shortdesc}</p>'

    html_content += convert_body_to_html(body_element)

    return html_content

def convert_body_to_html(body_element):
    body_html = ''
    for child in body_element:
        if child.tag == 'group':
            body_html += convert_group_to_html(child)
        # Add more cases as needed for other tags within <body>
    return body_html

def convert_group_to_html(group_element):
    group_html = ''
    for child in group_element:
        if child.tag == 'pos':
            group_html += convert_pos_to_html(child)
        elif child.tag == 'pli':
            group_html += convert_pli_to_html([child])
        elif child.tag == 'safetymessage':
            group_html += convert_safetymessage_to_html(child)
        elif child.tag == 'illustration':
            group_html += convert_illustration_to_html(child)
        elif child.tag == 'group':
            group_html += convert_group_to_html(child)
        elif child.tag == 'p':
            group_html += convert_paragraph_to_html(child)
        elif child.tag == 'note':
            group_html += f'<p><strong>Note:</strong> {child.text}</p>'

        # Add more cases as needed for other tags within <group>
    return group_html


def convert_pos_to_html(pos_element):
    href = pos_element.get('editref')
    text = pos_element.text or ''
    return f'<a href="{href}">{text}</a>'


def convert_pli_to_html(pli_elements):
    list_items = [f'<li id="{pli.get("id")}">{pli.find("postxt").text}</li>' for pli in pli_elements]
    return '<ol>' + ''.join(list_items) + '</ol>'

def convert_xref_to_html(xref_element):
    href = xref_element.get('href')

    if href is None:
        return xref_element.text

    text = xref_element.text or 'Reference'
    return f'<a href="{href}">{text}</a>'

def convert_paragraph_to_html(p_element):
    paragraph_html = '<p>'
    if p_element.text:
        print(p_element.text)
        paragraph_html += p_element.text

    for sub_element in p_element:
        if sub_element.tag == 'pos':
            paragraph_html += convert_pos_to_html(sub_element)
        elif sub_element.tag == 'xref':
            paragraph_html += convert_xref_to_html(sub_element)
        elif sub_element.tag == 'i':
            paragraph_html += f'<i>{sub_element.text}</i>'

        if sub_element.tail:
            paragraph_html += sub_element.tail

    paragraph_html += '</p>'
    return paragraph_html

def convert_safetymessage_to_html(safetymessage_element):
    hazardidentification = safetymessage_element.find('hazardidentification').text
    precautions_element = safetymessage_element.find('.//precautions')

    # Process the precautions text and any nested elements
    precautions_html = process_nested_elements(precautions_element)

    return f'<div class="safetymessage"><p>{hazardidentification}</p>{precautions_html}</div>'

def process_nested_elements(element):
    """
    Processes an element's text and its nested elements, returning HTML string.
    """
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
    
    poslist = illustration_element.find('poslist')
    if poslist is not None:
        poscol = poslist.find('poscol')
        list_html = convert_pli_to_html(poscol.findall('pli'))
    else:
        list_html = ''

    # Check for illustrationtext and add it to the HTML
    illustration_text_element = illustration_element.find('illustrationtext')
    if illustration_text_element is not None:
        illustration_text_html = convert_group_to_html(illustration_text_element)
        print(illustration_text_html)
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

# Call the function with your XML file path
filepath =  './all_xml_data/3030000-0126/xml/0000136007.xml'
xml_tree = ET.parse(filepath)
xml_tree = add_pli_description_to_pos_tags(xml_tree)
xml_root = xml_tree.getroot()
html_content = convert_topic_to_html(xml_root)
save_to_html(html_content, './test.html')

