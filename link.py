import os
import re
import xml.etree.ElementTree as ET

xml_poetry = ET.parse('AllPoetry_parsed.xml')
#
xml_prose = ET.parse('AllProse_parsed.xml')

final_csv = open('testcsv.csv', 'w+', encoding='UTF-8')

class Bibliographic():
    def __init__(self, book_id: int, word:str, author:str, work:str, subdoc = None):
        self.book_id = book_id
        self.word = word
        self.author = author
        self.work = work
        self.subdoc = subdoc

    def __str__(self):
        return (str(self.book_id) + '\t' + self.author + ',' + self.work)

    def find_occurences(self, xml:ET.ElementTree):
        xml_root = xml.getroot()
        doc_id = self.author + '-' + self.work
        result = []
        if self.subdoc is not None:
            if str(self.subdoc).isdigit():
                self.subdoc = int(self.subdoc) - 1
            for sentence in xml_root.findall(".//sentence[@document_id='{}'][@subdoc='{}']".format(doc_id, self.subdoc)):
                for word in sentence[:]:
                    if "lemma" in word.attrib:
                        if word.attrib["lemma"] == self.word:
                            return word.attrib["wid"]

        if len(result) == 0:
            for sentence in xml_root.findall(".//sentence[@document_id='{}']".format(doc_id, self)):
                for word in sentence[:]:
                    if "lemma"in word.attrib:
                        if word.attrib["lemma"] == self.word:
                            result.append(word.attrib["wid"])

        return ', '.join(result)

for file in os.listdir('tst'):
    with open('tst/' + file, 'r', encoding='UTF-8') as csv:
        with open('tst/non_urn.txt', 'w', encoding='UTF-8') as output:

            for line in csv.readlines():
                line = line.split('\t')
                urn = line[7]
                if urn.startswith('urn'):
                    pattern = r".perseus-\w+\d"
                    urn = re.sub(pattern, '', urn)
                    reference = ''.join(digit for digit in urn if not digit.isalpha())
                    reference = reference[3:-1]
                    reference = reference.replace(':', '.')
                    reference = reference.replace('.', ':', 2)

                    reference_fields = reference.split(':')
                    if len(reference_fields)> 3:
                        print(line[0])
                        print(reference)

                    while len(reference_fields) < 3:
                        reference_fields.append(None)

                    biblio = Bibliographic(line[0], line[1], reference_fields
                                           [0], reference_fields[1], str(reference_fields[2]))

                    line.append(biblio.find_occurences(xml_poetry))
                    line.append(biblio.find_occurences(xml_prose))

                    final_csv.write('\t'.join(line) + '\n')
                    print(line[0])

                else:
                    output.write(line[7])





