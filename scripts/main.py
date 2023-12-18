from prepdocslib.textsplitter import TextSplitterCustom,TextSplitterCustom2, Page
import numpy as np


#5145 chunks
if __name__ == "__main__":
    splitter = TextSplitterCustom()
    file = open("../data/mdFINAL.md", "rb")
    #file = open("NoPtags.html", "rb")

    text = file.read().decode("utf-8")
    pages = [
        Page(page_num=0, offset=0, text=text),
    ]
    pages = splitter.split_pages(pages)


    # Open a text file to write the pages
    with open("split_chunks.txt", "w", encoding="utf-8") as output_file:
        for i, page in enumerate(pages):
            
            # Write each page's content
            output_file.write(f"CHUNK {i + 1}\n")
            output_file.write(str(page.page_num))

            output_file.write(page.text)
            output_file.write("\n\n--- End of CHUNKS ---\n\n")
    page_lengths = []


    longest_text = ""
    # Pair each page's text with its length
    page_length_pairs = [(len(page.text), page.text) for page in pages]

    # Sort the pairs by length in descending order
    page_length_pairs.sort(key=lambda pair: pair[0], reverse=True)

    # Print the lengths and texts of the top 20 longest pages
    print("Top 20 longest pages:")
    for i, (length, text) in enumerate(page_length_pairs[2:3]):
        print(f"Length of page {i + 1}: {length}")
        print("Text:", text)
        print("\n--- End of Page ---\n")

    # Additional statistics
    page_lengths = [pair[0] for pair in page_length_pairs]
    print("median", np.median(page_lengths))
    print("mean", np.mean(page_lengths))
    print("std", np.std(page_lengths))
    print("max", np.max(page_lengths))
    print("min", np.min(page_lengths))


#<!-- Start of section about Troubleshoot - Quick Guide --> <section class="section" id="section993"> <h3> Troubleshoot - Quick Guide 



#Start of section about CAU Stripper - Set --> <section class="section" id="section1044"