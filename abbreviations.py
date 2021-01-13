import xml.etree.ElementTree as Et
import re

# TEI.2 -> (teiHeader) text -> front -> (pref) (post) (0) 1 -> (head) p -> list

with open("LSJ_data/grc.lsj.perseus-eng01.xml", encoding='UTF-8') as file:
    tree = Et.parse(file)
    root = tree.getroot()

authors = root[1][0][3][1][0]

# with open('abbrev_authors.csv', 'w+') as output:
#     for author in authors[:]:
#         if len(author) > 0:
#
#             name = author[0].text
#             info = author[0].tail
#
#             if '=' not in info and '=' not in name:
#
#                 m = re.search(r"\[(.*?)]", info)
#
#                 if m:
#                     abbrev = m.group(1)
#
#                 output.write(name + '\t' + abbrev + '\n')

with open('abbrev_works.csv', 'w+') as output:
    for author in authors[:]:
        if len(author) > 0:

            name = author[0].text
            tail = author[0].tail

            if '=' in name:
                name = name.split(" = ")
                if len(name) == 2:
                    output.write(name[0] + '\t' + name[1] + '\n')

            if '=' in tail:
                tail = tail.split(" = ")
                if len(tail) == 2:
                    output.write(tail[0] + '\t' +  tail[1] + '\n')