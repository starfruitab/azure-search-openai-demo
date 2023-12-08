from typing import Generator, List
from bs4 import BeautifulSoup
import re

from .contentparsers import Page


class SplitPage:
    """
    A section of a page that has been split into a smaller chunk.
    """

    def __init__(self, page_num: int, text: str):
        self.page_num = page_num
        self.text = text


class TextSplitter:
    """
    Class that splits pages into smaller chunks. This is required because embedding models may not be able to analyze an entire page at once
    """

    def __init__(self, verbose: bool = False):
        self.sentence_endings = [".", "!", "?"]
        self.word_breaks = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]
        self.max_section_length = 1000
        self.sentence_search_limit = 100
        self.section_overlap = 100
        self.verbose = verbose

    def split_pages(self, pages: List[Page]) -> Generator[SplitPage, None, None]:
        def find_page(offset):
            num_pages = len(pages)
            for i in range(num_pages - 1):
                if offset >= pages[i].offset and offset < pages[i + 1].offset:
                    return pages[i].page_num
            return pages[num_pages - 1].page_num

        all_text = "".join(page.text for page in pages)
        length = len(all_text)
        start = 0
        end = length
        while start + self.section_overlap < length:
            last_word = -1
            end = start + self.max_section_length

            if end > length:
                end = length
            else:
                # Try to find the end of the sentence
                while (
                    end < length
                    and (end - start - self.max_section_length) < self.sentence_search_limit
                    and all_text[end] not in self.sentence_endings
                ):
                    if all_text[end] in self.word_breaks:
                        last_word = end
                    end += 1
                if end < length and all_text[end] not in self.sentence_endings and last_word > 0:
                    end = last_word  # Fall back to at least keeping a whole word
            if end < length:
                end += 1

            # Try to find the start of the sentence or at least a whole word boundary
            last_word = -1
            while (
                start > 0
                and start > end - self.max_section_length - 2 * self.sentence_search_limit
                and all_text[start] not in self.sentence_endings
            ):
                if all_text[start] in self.word_breaks:
                    last_word = start
                start -= 1
            if all_text[start] not in self.sentence_endings and last_word > 0:
                start = last_word
            if start > 0:
                start += 1

            section_text = all_text[start:end]
            yield SplitPage(page_num=find_page(start), text=section_text)

            last_table_start = section_text.rfind("<table")
            if last_table_start > 2 * self.sentence_search_limit and last_table_start > section_text.rfind("</table"):
                # If the section ends with an unclosed table, we need to start the next section with the table.
                # If table starts inside sentence_search_limit, we ignore it, as that will cause an infinite loop for tables longer than MAX_SECTION_LENGTH
                # If last table starts inside section_overlap, keep overlapping
                if self.verbose:
                    print(
                        f"Section ends with unclosed table, starting next section with the table at page {find_page(start)} offset {start} table start {last_table_start}"
                    )
                start = min(end - self.section_overlap, start + last_table_start)
            else:
                start = end - self.section_overlap

        if start + self.section_overlap < end:
            yield SplitPage(page_num=find_page(start), text=all_text[start:end])


class TextSplitterCustom:
    """
    Class that splits pages into smaller chunks. This is required because embedding models may not be able to analyze an entire page at once
    """
    def __init__(self, verbose: bool = False):
        self.sentence_endings = [".", "!", "?"]
        self.word_breaks = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]
        self.start_tags = ["ol", "p", "table", "ul"]  # Include 'ol' and 'ul' in start tags
        self.pref_section_length = 1000
        self.max_section_length = 27000  # Set max length to 30,000 characters
        self.force_section_length = 3000
        self.sentence_search_limit = 100
        self.section_overlap = 300
        self.verbose = verbose

    @staticmethod
    def extract_html_tags(html_string):
        pattern = r'<(\/?\w+)(?:\s[^>]*?)?>'
        match = re.search(pattern, html_string)
        match = match.group(1) if match else None
        return match

    def reset_chunk(self, chunk):
        total_length = 0
        for i, element in enumerate(chunk[::-1]):
            total_length += len(element)
            if total_length > self.section_overlap:
                return chunk[len(chunk)-1-i:], total_length

    def split_text(self, all_text) -> List[str]:
        tag_split = re.split(r'(<[^>]+>)', all_text)
        elements = []
        is_tag = []
        for tag in tag_split:
            if tag.startswith('<'):
                elements.append(tag)
                is_tag.append(True)
            else:
                elements.extend(tag.split())
                is_tag.extend([False] * len(tag.split()))
        chunk = []
        total_length = 0
        needed_tags = []

        for idx, element in enumerate(elements):
            popped = False
            chunk.append(element)
            total_length += len(element)
            if is_tag[idx]:
                html_tag = self.extract_html_tags(element)
                if html_tag:
                    if html_tag in self.start_tags:
                        needed_tags.append("/" + html_tag)
                    elif len(needed_tags) > 0 and html_tag == needed_tags[-1]:
                        popped = True
                        needed_tags.pop()

            if (total_length > self.pref_section_length and (
                    (len(needed_tags) == 0)
                    or (total_length > self.max_section_length and popped)
                    or (total_length > self.force_section_length))):
                yield " ".join(chunk)
                chunk, total_length = self.reset_chunk(chunk)
        if chunk:
            yield " ".join(chunk)
    

    def split_section(self, section_text: str) -> Generator[str, None, None]:
        """
        Generator that splits a section into chunks, each not exceeding the max_section_length.
        """
        start = 0
        while start < len(section_text):
            end = min(start + self.max_section_length, len(section_text))
            yield section_text[start:end]
            start = end

    def split_pages(self, pages: List[Page]) -> Generator[SplitPage, None, None]:
        all_text = "".join(page.text for page in pages)
        soup = BeautifulSoup(all_text, 'html.parser')

        section_idx = 0
        sections = soup.find_all('section')
        for section in sections:
            section_text = str(section)
            if len(section_text) <= self.max_section_length:
                # If the section is within the limit, yield it as is
                yield SplitPage(section_idx, section_text)
            else:
                # If the section exceeds the limit, split it into smaller chunks
                for chunk in self.split_section(section_text):
                    yield SplitPage(section_idx, chunk)
            section_idx += 1


