import html2text
from bs4 import BeautifulSoup, Comment

file_path = '../data/NoPtags.html'

# Read the HTML content from the file
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Use BeautifulSoup to extract comments
soup = BeautifulSoup(html_content, 'html.parser')
comments = soup.find_all(string=lambda text: isinstance(text, Comment))

# Convert HTML to Markdown
markdown_content = html2text.html2text(html_content)

# Insert comments into the Markdown content
for comment in comments:
    markdown_comment = f"\n\n<!-- {comment} -->\n\n"
    markdown_content = markdown_content + markdown_comment

# Write the Markdown content to a .md file
output_file_path = 'converted_markdown.md'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(markdown_content)


