import html2text
from bs4 import BeautifulSoup, Comment
import re
file_path = '../data/NoPtags.html'

# Read the HTML content from the file
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Convert HTML comments to Markdown comments
html_comments_to_md = re.sub(r'<!--(.*?)-->', lambda m: f"[//]: # ({m.group(1).strip()})", html_content)

# Convert HTML (with modified comments) to Markdown
markdown_content = html2text.html2text(html_comments_to_md)

# [//]: # (Write the Markdown content to a .md file)
output_file_path = 'converted_markdown.md'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(markdown_content)

# Additional code to count occurrences of '##'
# This part remains unchanged from the previous example
with open(output_file_path, 'r', encoding='utf-8') as md_file:
    md_content = md_file.read()



