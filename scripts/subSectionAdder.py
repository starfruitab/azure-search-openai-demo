from bs4 import BeautifulSoup, Comment

def process_html(input_file_path, output_file_path):
    with open(input_file_path, "rb") as file:
        soup = BeautifulSoup(file, 'html.parser')

    last_h3 = None

    for tag in soup.find_all(['h3', 'h4']):
        if tag.name == 'h3':
            last_h3 = tag
        elif tag.name == 'h4' and last_h3 is not None:
            parent_section = last_h3.text.strip()
            comment_text = f"This section is part of the parent section: {parent_section}"
            comment = Comment(comment_text)
            tag.insert_after(comment)

    # Write the modified HTML to a new file
    with open(output_file_path, "wb") as file:
        file.write(soup.encode(formatter="html"))

# Paths to your HTML files
input_file_path = "../dataTEMP/MM-3030000-0126.html"
output_file_path = "../data/processed_MM-3030000-0126.html"
process_html(input_file_path, output_file_path)

input_file_path = "../dataTEMP/UP-3210710-0101.html"
output_file_path = "../data/processed_UP-3210710-0101.html"

process_html(input_file_path, output_file_path)

input_file_path = "../dataTEMP/UP-3521503-0101.html"
output_file_path = "../data/processed_UP-3521503-0101.html"

process_html(input_file_path, output_file_path)
