from bs4 import BeautifulSoup

if __name__ == "__main__":
    # Read the original HTML file
    with open("../data/merged.html", "r", encoding="utf-8") as file:
        html_content = file.read()

   # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Unwrap all <p> tags (remove the tag but keep its content)
    for p_tag in soup.find_all('p'):
        p_tag.unwrap()

    # Get the modified HTML as a string
    modified_html = str(soup)


    # Save the modified HTML to a new file
    with open("NoPtags.html", "w", encoding="utf-8") as new_file:
        new_file.write(modified_html)
