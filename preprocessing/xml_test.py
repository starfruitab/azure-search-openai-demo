import xml.etree.ElementTree as ET
from html import escape

def add_pli_description_to_pos_tags(xml_tree):
    """
    Parses the XML file and adds information before the 'pos' tags with the information based of the 'pli' tags.
    Takes the XML file path as input and returns the XML tree.
    """
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
        pos_id = pos.get('editref')[1:]  # Remove the first #
        if pos_id in pli_descriptions:
            pos.text = pli_descriptions[pos_id]

    return xml_tree

def extract_text_from_href(href):
    # Extracting the last part of the href attribute as text
    if not href:
        return "Unknown"
    return href.split('/')[-1].replace('-', ' ').title()

def process_element(element, base_img_path='./all_xml_data/graphics/png/'):
    html_content = ""
    tag = element.tag.lower()

    # Handling for different tags
    if tag in ["topic", "section", "body", "group"]:
        html_content += "<div>"
    elif tag == "title":
        html_content += "<h1>"
    elif tag == "p":
        html_content += "<p>"
    elif tag == "shortdesc":
        html_content += "<p><em>"
    elif tag == "illustration":
        img_src = element.find('graphic').attrib.get('href', '#').replace('.eps', '.png')
        full_img_path = base_img_path + img_src
        html_content += f"<img src='{full_img_path}' alt='Graphic Image'/>"
    elif tag == "table":
        html_content += "<table border='1'>"  # Add border for visibility
    elif tag == "tgroup":
        # Skip tgroup as it's not a standard HTML tag but keep processing its children
        pass
    elif tag == "thead":
        html_content += "<thead>"
    elif tag == "tbody":
        html_content += "<tbody>"
    elif tag == "row":
        html_content += "<tr>"
    elif tag == "entry":
        html_content += "<td>"
    #elif tag == "pos":
       # Extract text from the href attribute
       # href = element.get('href', '')
        #text = extract_text_from_href(href)
       # html_content += escape(text)

    elif tag == "pos":
        # Let convert_pos_to_html handle the text of pos element
        html_content += convert_pos_to_html(element)
        return html_content  # Return immediately to avoid duplicating text

    elif tag == "pli":
        list_items = convert_pli_to_html([element])
        html_content += '<ol>' + list_items + '</ol>'
    
    elif tag == "xref":
        # Skip xref tags as per requirement
        pass
    # ... Add specific handling for other tags ...

    # Element text
    if element.text and tag != "pos":  # Skip adding text for pos tag here
        html_content += escape(element.text)

    # Process child elements and their tail text
    for child in element:
        if child.tag != 'xref':  # Skip xref tags
            html_content += process_element(child, base_img_path)
        if child.tail:
            html_content += escape(child.tail)

    # Closing tags
    tag_to_close = {
        "topic": "div", "section": "div", "body": "div", "group": "div",
        "title": "h1", "p": "p", "shortdesc": "p", "illustration": "div",
        "table": "table", "thead": "thead", "tbody": "tbody", "row": "tr", "entry": "td"
    }
    if tag in tag_to_close:
        html_content += f"</{tag_to_close[tag]}>"
    return html_content


def convert_topic_to_html(topic_element):
    if topic_element is None:
        return ''
    return process_element(topic_element)


def convert_pli_to_html(pli_elements):
    list_items = [f'<li id="{pli.get("id")}">{pli.find("postxt").text}</li>' for pli in pli_elements]
    return ''.join(list_items)

def convert_pos_to_html(pos_element):
    href = pos_element.get('editref')
    text = ''.join(pos_element.itertext()).strip()

    # Use a portion of the href attribute as fallback text if the pos tag is empty
    if not text:
        text = href.split('/')[-1].replace('-', ' ').title() if href else 'Reference'

    return f'<a href="{href}">{text}</a>'



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

# Main execution code
filepath = './section_4.xml'
xml_tree = ET.parse(filepath)
xml_tree = add_pli_description_to_pos_tags(xml_tree)
xml_root = xml_tree.getroot()
html_content = convert_topic_to_html(xml_root)
save_to_html(html_content, './test.html')
