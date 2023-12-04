from prepdocslib.textsplitter import TextSplitterCustom, Page
import numpy as np

if __name__ == "__main__":
    splitter = TextSplitterCustom()
    file = open("data2/chapter_4.html", "rb")
    text = file.read().decode("utf-8")
    pages = [
        Page(page_num=0, offset=0, text=text),
    ]
    pages = splitter.split_pages(pages)
    page_lengths = []
    longest_text = ""
    for page in pages:
        page_lengths.append(len(page.text))
        if len(page.text) > len(longest_text):
            longest_text = page.text
    print("median", np.median(page_lengths))
    print("mean", np.mean(page_lengths))
    print("std", np.std(page_lengths))
    print("max", np.max(page_lengths))
    print("min", np.min(page_lengths))
    print("longest", longest_text)
