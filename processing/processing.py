import os
import xml.etree.ElementTree as ET

def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        text_content = []
        image_references = []
        list_items = []  # New list to store list items

        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_content.append(elem.text.strip())
            if elem.tag == 'graphic' and 'href' in elem.attrib:
                image_references.append(elem.attrib['href'])
            if elem.tag == 'li':  # Check for list item tags
                li_text = ''.join(elem.itertext()).strip()  # Extract all text within the list item
                list_items.append(li_text)

        return text_content, image_references, list_items
    except ET.ParseError as e:
        return f"XML Parse Error: {e}", [], []

def convert_to_html(text_content, image_references, list_items):
    html_content = "<html><body>"

    for text in text_content:
        html_content += f"<p>{text}</p>"

    if list_items:  # Add list items if there are any
        html_content += "<ul>"
        for item in list_items:
            html_content += f"<li>{item}</li>"
        html_content += "</ul>"

    for img_ref in image_references:
        #Remove the eps from img_ref and replace with png
        img_ref = img_ref.replace('.eps', '.png')

        #current path
        image_path = ''
        image_path = os.path.join(image_path, '../all_xml_data/graphics/png/')
        image_path = os.path.join(image_path, img_ref)
        html_content += f"<p>Image: {img_ref}</p>"
        html_content += f"<img src='{image_path}' alt='{img_ref}' />"

    html_content += "</body></html>"
    return html_content

def replace_newlines(text):
    return text.replace('\n', ' ')

def extract_rag_data(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    rag_data = {
        "title": root.find('.//title').text if root.find('.//title') is not None else "",
        "prerequisites": [],
        "procedure_steps": [],
        "illustrations": []
    }

    # Extract prerequisites
    for prereq in root.findall('.//prereq/*'):
        prereq_text = ''.join(prereq.itertext()).strip()
        if prereq_text:
            rag_data["prerequisites"].append(prereq_text)

    # Extract procedure steps
    for step_group in root.findall('.//step-group'):
        group_data = {"steps": [], "notes": [], "illustrations": []}

        for step in step_group.findall('.//step'):
            step_text = replace_newlines(''.join(step.itertext()).strip())
            group_data["steps"].append(step_text)

        for note in step_group.findall('.//note'):
            note_text = note.text.strip()
            group_data["notes"].append(note_text)

        for illustration in step_group.findall('.//illustration'):
            image_ref = illustration.find('.//graphic').attrib.get('href')
            group_data["illustrations"].append(image_ref)

        rag_data["procedure_steps"].append(group_data)

    return rag_data

def process_xml_files(xml_directory, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    #only go through 10 files

    for filename in os.listdir(xml_directory)[:10]:
        if filename.endswith('.xml'):
            print(f"Processing {filename}...")

            file_path = os.path.join(xml_directory, filename)
            text_content, image_references, list_items = parse_xml(file_path)

            html_content = convert_to_html(text_content, image_references, list_items)
            rag_data = extract_rag_data(file_path)

            print("Rag Data:")
            print(rag_data)

            output_file_path = os.path.join(output_directory, filename.replace('.xml', '.html'))
            with open(output_file_path, 'w') as file:
                file.write(html_content)

# Define the directories
xml_directory = './all_xml_data/3030000-0126/xml'
output_directory = './output'  # Update this with the desired output path

# Process the XML files
process_xml_files(xml_directory, output_directory)
