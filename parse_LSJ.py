import os
import xml.etree.ElementTree as ET

          # TEI.2 -> (teiHeader) text -> (front) body -> div0 -> (head) entryFree

for i, letter in enumerate(os.listdir('LSJ_data')):

    title = 'LSJ_{}.csv'.format(i+1)

    with open(title, "w+", encoding='UTF-8') as file:


        my_tree = ET.parse("LSJ_data/" + letter)

        my_root = my_tree.getroot()

        if i == 0:

            words = my_root[1][1][0][1:]        # TEI.2 -> (teiHeader) text -> (front) body -> div0 -> (head) entryFree

        else:

            words = my_root[1][0][0][1:]        # TEI.2 -> (teiHeader) text -> body -> div0 -> (head) entryFree

        for j, word in enumerate(words):
            if word.tag != 'entryFree':
                continue
            else:
                if j%1000 == 0:
                    print("book {}/{}, word {}/{}".format(i+1, len((os.listdir("LSJ_data"))), j, len(words)))

                previous_sense_levels = ['A', 'I', '1', 'a']

                key = word.attrib['key']
                senses = word.findall("sense")
                for sense in senses:
                    default = ['A', 'I', '1', 'a']

                    name = sense.attrib['n']
                    level = sense.attrib['level']

                    sense_levels = previous_sense_levels[:int(level) - 1] + [name] + default[int(level):]

                    previous_sense_levels = sense_levels
                    translation = ""
                    reference = ""
                    translation_counter = 0
                    for element in sense[:]:

                        if element.tag == 'tr' and translation_counter == 0:

                            translation = element.text
                            if reference != "":
                                file.write(
                                    key + '\t' + "\t".join(sense_levels) + "\t" + translation + "\t" + reference + "\n")
                            translation_counter += 1

                        if element.tag == 'bibl':           # bibliography without citations

                            reference = ""

                            for bibl in element:
                                if bibl.text is not None:
                                    reference += bibl.text

                            file.write(key + '\t' + "\t".join(sense_levels) + "\t" + translation + "\t" + reference + "\n")

                        if element.tag == 'cit':            # bibliography for citations
                            book = element.find('bibl')
                            reference = ""

                            if book is not None:

                                for bibl in book:
                                    reference += bibl.text

                                file.write(
                                    key + '\t' + "\t".join(sense_levels) + "\t" + translation + "\t" + reference + "\n")