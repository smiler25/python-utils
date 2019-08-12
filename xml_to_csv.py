"""
Simple XML to CSV converter.
Creates new csv file with selected tag on each line
and every inner fields and attributes in columns
"""

import argparse
import csv
import os
import xml.parsers.expat


class Parser:
    def __init__(self, fname, fname_to, tag, target_tags=None, chunk_size=1000, delimiter=','):
        self.fname = fname
        self.fname_to = fname_to
        self.delimiter = delimiter
        self.tag = tag
        if target_tags and not isinstance(target_tags, (tuple, list)):
            raise AttributeError('Tags should be a list')
        self.target_tags = target_tags
        self.in_tag = False
        self.data = []
        self.tag_data = {}
        self.current_tag = None
        self.file_header = None
        self.count = 0
        self.chunk_count = 0
        self.chunk_size = chunk_size

    def start_element(self, name, attrs):
        if not self.in_tag and name != self.tag:
            return
        self.in_tag = True
        if attrs:
            if self.target_tags:
                self.tag_data.update({k: v for k, v in attrs.items() if k in self.target_tags})
            else:
                self.tag_data.update(attrs)
        if self.target_tags and self.current_tag in self.target_tags:
            self.current_tag = name

    def end_element(self, name):
        if name == self.tag:
            self.in_tag = False
            self.data.append(self.tag_data)
            self.tag_data = {}
            self.count += 1
            self.chunk_count += 1
            if self.chunk_count == self.chunk_size:
                self.write_to_file()
            return
        self.current_tag = None

    def char_data(self, data):
        if not self.current_tag or not data:
            return
        if isinstance(data, str):
            if not data.strip():
                return
            self.tag_data[self.current_tag] = data.strip()
        if isinstance(data, dict):
            self.tag_data[self.current_tag] = data

    def parse(self):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element
        p.CharacterDataHandler = self.char_data
        with open(self.fname, 'rb') as f:
            p.ParseFile(f)
        if self.data:
            self.write_to_file()

    def write_to_file(self):
        print('writing to file, total done {}'.format(self.count))
        if not self.data:
            self.chunk_count = 0
            return
        if not self.file_header:
            self.file_header = list(sorted(self.data[0].keys()))
        header_exists = os.path.exists(self.fname_to)
        with open(self.fname_to, 'a+') as f:
            wr = csv.DictWriter(f, self.file_header, delimiter=self.delimiter)
            if not header_exists:
                wr.writeheader()
            wr.writerows(self.data)
        self.data = []


def create_parser():
    p = argparse.ArgumentParser()
    p.add_argument('-f', '--xml', required=True, help='Incoming XML file')
    p.add_argument('-c', '--csv', required=True, help='Result CSV file')
    p.add_argument('-t', '--tag', required=True, help='Target tag')
    p.add_argument('-d', '--delimiter', default=',', help='CSV delimiter')
    p.add_argument('--tags', nargs='+', help='List of tags')
    p.add_argument('--chunk', type=int, default=1000, help='Chunk size')
    return p


if __name__ == '__main__':
    args = create_parser().parse_args()
    parser = Parser(args.xml, args.csv, args.tag, args.tags, args.chunk, args.delimiter)
    parser.parse()
