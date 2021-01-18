import xml.etree.ElementTree as ET
import os

missing_subdocs = []
missing_lemmata = []

with open('lemma_lookup.csv', 'w+', encoding='UTF-8') as output:


    for xml in os.listdir('parsed_xmls'):
        read_xml = ET.parse('parsed_xmls/' + xml)
        root = read_xml.getroot()

        for sentence in root[:]:

            for word in sentence[:]:

                if int(word.attrib['wid']) % 10000 == 0:
                    print(word.attrib['wid'])

                if 'lemma' in word.attrib and 'subdoc' in sentence.attrib:
                    output.write(sentence.attrib['document_id'] + '\t' + sentence.attrib['subdoc'] + '\t' + sentence.attrib['id'] + '\t' +
                          word.attrib['wid'] + '\t' + word.attrib['lemma'] + '\n')

                elif 'lemma' in word.attrib:
                    output.write(sentence.attrib['document_id'] + '\t' + '' + '\t' + sentence.attrib['id'] + '\t' +
                          word.attrib['wid'] + '\t' + word.attrib['lemma'] + '\n')
                    missing_subdocs.append(sentence.attrib['document_id'])

                elif 'subdoc' in sentence.attrib:
                    output.write(sentence.attrib['document_id'] + '\t' + sentence.attrib['subdoc']+ '\t' + sentence.attrib['id'] + '\t' +
                          word.attrib['wid'] + '\t' + '' + '\n')
                    missing_lemmata.append(word.attrib['wid'])

                else:
                    output.write(sentence.attrib['document_id'] + '\t' + '' + '\t' + sentence.attrib['id'] + '\t' +
                          word.attrib['wid'] + '\t' + '' + '\n')


with open('missing_subdocs.txt', 'w+', encoding='UTF-8') as output:
    for missing in set(missing_subdocs):
        output.write(missing + '\n')

with open('missing_lemmata.txt', 'w+', encoding='UTF-8') as output:
    for missing in missing_lemmata:
        output.write(missing + '\n')
