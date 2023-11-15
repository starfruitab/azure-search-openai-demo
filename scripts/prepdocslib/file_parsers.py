
class FileParserWrapper(object):
    def __init__(self, file_parser):
        self.file_parser = file_parser

    def parse(self, file_path):
        return self.file_parser.parse(file_path)


class XmlParser:
    def __init__(self, xml_file):
        self.xml_file = xml_file

    def parse(self):
        return self.xml_file
