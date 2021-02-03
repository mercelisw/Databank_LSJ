import xml.etree.ElementTree as ET
import os

missing_subdocs = []
missing_lemmata = []

## IMPORTANT: afterwards, remove "

with open('lemma_lookup.csv', 'w+', encoding='UTF-8') as output:
    for xml in os.listdir('parsed_xmls'):
        read_xml = ET.parse('parsed_xmls/' + xml)
        root = read_xml.getroot()

        for sentence in root[:]:

            for word in sentence[:]:
                if 'wid' in word.attrib:
                    if int(word.attrib['wid']) % 10000 == 0:
                        print(word.attrib['wid'])

                    if 'lemma' in word.attrib and 'subdoc' in sentence.attrib:
                        if 'line' in word.attrib:
                            output.write(
                                sentence.attrib['document_id'] + '\t' + sentence.attrib['subdoc'] + '\t' +
                                sentence.attrib['id'] + '\t' + word.attrib['line'] + '\t' + word.attrib['wid'] + '\t' +
                                word.attrib['lemma']+ '\t' + word.attrib['form'] + '\n')
                        else:
                            output.write(
                                sentence.attrib['document_id'] + '\t' + sentence.attrib['subdoc'] + '\t' +
                                sentence.attrib['id'] + '\t' + '' + '\t' + word.attrib['wid'] + '\t' +
                                word.attrib['lemma'] + word.attrib['form'] + '\n')

                    elif 'lemma' in word.attrib:
                        if 'line' in word.attrib:
                            output.write(sentence.attrib['document_id'] + '\t' + '' + '\t' + sentence.attrib['id'] +
                                         '\t' + word.attrib['line'] + '\t' + word.attrib['wid'] + '\t' +
                                         word.attrib['lemma']  + word.attrib['form'] + '\n')
                            missing_subdocs.append(sentence.attrib['document_id'])
                        else:
                            output.write(sentence.attrib['document_id'] + '\t' + '' + '\t' + sentence.attrib['id'] +
                                         '\t' + '' + '\t' + word.attrib['wid'] + '\t' + word.attrib['lemma'] +
                                         word.attrib['form'] + '\n')
                            missing_subdocs.append(sentence.attrib['document_id'])

                    elif 'subdoc' in sentence.attrib:
                        if 'line' in word.attrib:
                            output.write(
                                sentence.attrib['document_id'] + '\t' + sentence.attrib['subdoc'] + '\t' +
                                sentence.attrib['id'] + '\t' + word.attrib['line'] + '\t' + word.attrib['wid'] +
                                '\t' + ''  + word.attrib['form'] + '\n')
                            missing_lemmata.append(word.attrib['wid'])

                        else:
                            output.write(
                                sentence.attrib['document_id'] + '\t' + sentence.attrib['subdoc'] + '\t' +
                                sentence.attrib['id'] + '\t' + '' + '\t' + word.attrib['wid'] + '\t' + '' +
                                word.attrib['form'] + '\n')
                            missing_lemmata.append(word.attrib['wid'])

                    else:
                        if 'line' in word.attrib:
                            output.write(sentence.attrib['document_id'] + '\t' + '' + '\t' + sentence.attrib['id'] +
                                         '\t' + word.attrib['line'] + '\t' + word.attrib['wid'] + '\t' + '' +
                                         word.attrib['form'] + '\n')
                        else:
                            output.write(sentence.attrib['document_id'] + '\t' + '' + '\t' + sentence.attrib['id'] +
                                         '\t' + '' + '\t' + word.attrib['wid'] + '\t' + '' + word.attrib['form'] + '\n')

with open('missing_subdocs.txt', 'w+', encoding='UTF-8') as output:
    for missing in set(missing_subdocs):
        output.write(missing + '\n')

with open('missing_lemmata.txt', 'w+', encoding='UTF-8') as output:
    for missing in missing_lemmata:
        output.write(missing + '\n')
