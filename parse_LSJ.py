import os
import xml.etree.ElementTree as ET
import pandas as pd

# TEI.2 -> (teiHeader) text -> (front) body -> div0 -> (head) entryFree
# Left out Cyr. Cyrilli Glossarium




def create_abbrev_dict(file):
    with open(file, "r+") as input:
        lines = input.readlines()
        authors = {}
        for line in lines:
            line = line[:-1]
            line = line.split('\t')
            authors[line[1]] = line[0]
        return authors

authors = create_abbrev_dict("abbrev_authors.csv")
works = create_abbrev_dict("abbrev_works.csv")
works = {v: k for k, v in works.items()}

def create_bibliographic_link(author: str, work: str, loc:int):

    work_id = ""


    tlg = pd.read_csv('tlg_numbers.csv', sep='\t')

    if author is not None:
        try:
            full_author = authors[author]
            if len(tlg[tlg["AUTHOR"] ==  full_author]) > 0:
                full_author = full_author.upper()
                author_index = tlg[(tlg['AUTHOR'] == full_author)].index[0]
                author_id = str(tlg.loc[author_index, 'TLG_AUTHOR'])
                author_id = author_id.rjust(4, "0")
            elif len(tlg[tlg['TITLE'] == full_author]) > 0:                                  # For errors like Odyssea which is in authors

                author_index = tlg[(tlg['TITLE'] == full_author)].index[0]
                author_id = str(tlg.loc[author_index, 'TLG_AUTHOR'])
                author_id = author_id.rjust(4, "0")
                work_id = str(tlg.loc[author_index, 'TLG_WORK'])
            else:

                file = open('unknown_authors.txt', 'a')
                file.write(full_author + '\n')
                file.close()
                author_id = "0000"

        except KeyError:
            author_id = "0000"

    else:
        author_id = "0000"

    if work is not None:
        try:
            full_work = works[work]
            if len(tlg[tlg["AUTHOR"] == full_author]) > 0 and len(tlg[tlg['TITLE'] == full_work]) > 0:
                # if tlg[(tlg['AUTHOR'] == full_author) & (tlg['TITLE'] == full_work)].size > 0:
                work_index = tlg[(tlg['AUTHOR'] == full_author) & (tlg['TITLE'] == full_work)].index[0]

                work_id = str(tlg.loc[work_index, 'TLG_WORK'])
            else:
                work_id = "001"
        except KeyError:
            work_id = "001"
    if work_id == "":
        work_id = "001"

    if loc is not None:        loc_id = str(loc)
    else:
        loc_id = ""

    return "urn:cts:greekLit:tlg{}.tlg{}.perseus-grc1:{}".format(author_id, work_id, loc_id)







def main():
    authors = create_abbrev_dict("abbrev_authors.csv")
    works = create_abbrev_dict("abbrev_works.csv")

    for i, letter in enumerate(os.listdir('LSJ_data')):

        title = 'LSJ_{}.csv'.format(i + 1)

        with open('LSJ_output/' + title, "w+", encoding='UTF-8') as file:

            my_tree = ET.parse("LSJ_data/" + letter)

            my_root = my_tree.getroot()

            if i == 0:

                words = my_root[1][1][0][1:]  # TEI.2 -> (teiHeader) text -> (front) body -> div0 -> (head) entryFree

            else:

                words = my_root[1][0][0][1:]  # TEI.2 -> (teiHeader) text -> body -> div0 -> (head) entryFree

            for j, word in enumerate(words):
                if word.tag != 'entryFree':
                    continue
                else:
                    if j % 1000 == 0:
                        print("book {}/{}, word {}/{}".format(i + 1, len((os.listdir("LSJ_data"))), j, len(words)))

                    previous_sense_levels = ['A', 'I', '1', 'a']

                    id = word.attrib['id']
                    key = word.attrib['key']
                    senses = word.findall("sense")
                    for sense in senses:
                        default = ['A', 'I', '1', 'a']

                        name = sense.attrib['n']
                        level = sense.attrib['level']

                        sense_levels = previous_sense_levels[:int(level) - 1] + [name] + default[int(level):]

                        previous_sense_levels = sense_levels
                        translation = ""
                        bib_key = ""
                        translation_counter = 0
                        for element in sense[:]:  # skips the 'etymological' info

                            if element.tag == 'tr' and translation_counter == 0:

                                translation = element.text
                                if bib_key != "":
                                    file.write(
                                        id[1:] + '\t' + key + '\t' + "\t".join(sense_levels) + "\t" + translation + "\t" + bib_key + "\n")
                                translation_counter += 1

                            if element.tag == 'bibl':  # bibliography without citations

                                bib_key = ""

                                if element.text is not None:
                                    if 'n' in element.attrib:
                                        bib_key += element.attrib['n']
                                    else:
                                        link = [None] * 3
                                        for child in element[:]:
                                            if child.text is not None:
                                                if child.text in authors:
                                                    link[0] = child.text
                                                elif child.text in works:
                                                    link[1] = child.text
                                                elif child.text.isnumeric():
                                                    link[2] = child.text



                                        bib_key = create_bibliographic_link(link[0], link[1], link[2])



                                if translation_counter > 0:
                                    file.write(
                                        id[1:] + '\t' + key + '\t' + "\t".join(sense_levels) + "\t" + translation + "\t" + bib_key + "\n")

                            if element.tag == 'cit':  # bibliography for citations
                                book = element.find('bibl')
                                bib_key = ""

                                if book is not None:

                                    if 'n' in book.attrib:
                                        bib_key += book.attrib['n']

                                    else:
                                        link = [None] * 3
                                        for child in book[:]:
                                            if child.text is not None:
                                                if child.text in authors:
                                                    link[0] = child.text
                                                elif child.text in works:
                                                    link[1] = child.text
                                                elif child.text.isnumeric():
                                                    link[2] = child.text

                                        bib_key = create_bibliographic_link(link[0], link[1], link[2])


                                    if translation_counter > 0:
                                        file.write(
                                            id[1:] + '\t' + key + '\t' + "\t".join(sense_levels) + "\t" + translation + "\t" + bib_key + "\n")




main()
