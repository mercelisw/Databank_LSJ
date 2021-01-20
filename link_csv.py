import pandas as pd
import re

pattern = r".perseus-\w+\d"  # to remove .perseus-grc1 etc.


def urn_to_ids(ref: str):  # Returns a dictionary containing the doc-id and the subdoc
    temp_ref = re.sub(pattern, '', ref)
    temp_ref = ''.join(digit for digit in temp_ref if not digit.isalpha())  # removes other non-numerics
    temp_ref = temp_ref[3:]  # removes initial :
    temp_ref = temp_ref.replace(':', '.')  # removes remaining :
    cleaned_ref = temp_ref.replace('.', ':', 2)  # split between author/work/subdoc is : otherwise .

    reference_fields = cleaned_ref.split(':')

    while len(reference_fields) < 3:
        reference_fields.append(None)

    return {'doc': reference_fields[0] + '-' + reference_fields[1], 'subdoc': str(reference_fields[2])}


xml = pd.read_csv('lemma_lookup.csv', sep='\t', encoding='UTF-8',
                  names=['doc', 'subdoc', 'sentence', 'line', 'word', 'lemma'],
                  dtype={'doc': str, 'subdoc': str, 'sentence': int, 'line': str, 'word': int, 'lemma': str})

lsj = pd.read_csv('tst/LSJ_2.csv', sep='\t', encoding='UTF-8', names=['id', 'key', 'sense_1', 'sense_2', 'sense_3',
                                                                      'sense_4', 'translation', 'ref'],
                  dtype={'id': int, 'key': str, 'sense_1': str, 'sense_2': str, 'sense_3': int, 'sense_4': str,
                         'translation': str, 'ref': str})
nb_of_results = 0
lsj['word_id'] = ""
doc_not_found = 0

for row in lsj.itertuples():
    reference = row.ref
    key = row.key
    result = []

    if row.Index % 10 == 0:
        print(row.Index)

    if reference.startswith('urn'):
        bibliography = urn_to_ids(reference)

        if bibliography['subdoc'].isdigit():  # subdoc is only digits

            zero_five_line_number = int(bibliography['subdoc']) // 5 * 5
            if zero_five_line_number == 0:
                zero_five_line_number = 1
            mask = ((xml['doc'].values == bibliography['doc']) &
                    ((xml['subdoc'].values == str(bibliography['subdoc'])) |
                     (xml['subdoc'].values == str(int(bibliography['subdoc']) - 1)) |  # for off-by-ones in subdoc
                     (xml['subdoc'].values == str(int(bibliography['subdoc']) + 1)) |
                     (xml['subdoc'].values == str(zero_five_line_number))) &
                    (xml['lemma'].values == key))
            doc_subdoc = xml[mask]
            for doc_row in doc_subdoc.itertuples():
                word_id = doc_row.word
                result.append(str(word_id))
                nb_of_results += 1

        if bibliography['subdoc'].isalpha():  # try line number
            zero_five_line_number = int(bibliography['subdoc']) // 5 * 5
            if zero_five_line_number == 0:
                zero_five_line_number = 1
            mask = ((xml['doc'].values == bibliography['doc']) &
                    ((xml['line'].values == str(bibliography['subdoc'])) |
                     (xml['line'].values == str(int(bibliography['subdoc']) - 1)) |  # for off-by-ones in line
                     (xml['line'].values == str(int(bibliography['subdoc']) + 1)) |
                     (xml['line'].values == str(zero_five_line_number))) &
                    (xml['lemma'].values == key))
            doc_subdoc = xml[mask]
            for doc_row in doc_subdoc.itertuples():
                word_id = doc_row.word
                result.append(str(word_id))
                nb_of_results += 1

        if len(result) == 0 and len(bibliography['subdoc']) > 0:  # for subdocs like 1.2.3 or others
            mask = ((xml['doc'].values == bibliography['doc']) &
                    ((xml['subdoc'].values == str(bibliography['subdoc'])) |
                     (xml['subdoc'].values == (bibliography['subdoc'][:-1]))) &  # e.g. Plato ... 23b
                    (xml['lemma'].values == key))
            doc_subdoc = xml[mask]
            for doc_row in doc_subdoc.itertuples():
                word_id = doc_row.word
                result.append(str(word_id))
                nb_of_results += 1

        elif len(result) == 0:  # if nothing found try whole document
            mask = ((xml['doc'].values == bibliography['doc']) &
                    (xml['lemma'].values == key))
            doc_subdoc = xml[mask]
            for doc_row in doc_subdoc.itertuples():
                word_id = doc_row.word
                result.append(str(word_id))
                nb_of_results += 1

        else:
            mask = (xml['doc'].values == bibliography['doc'])
            doc_subdoc = xml[mask]
            if doc_subdoc.size == 0:
                result.append('Document not found')
                doc_not_found += 1

    else:
        pass  # TODO handling of non-urn links!!

    print(str(row.Index) + ': ' + ','.join(result))
    lsj.at[row.Index, 'word_id'] = result

print("Hits: " + str(nb_of_results))
print("Documents not found: " + str(doc_not_found))

lsj.to_csv('tst/LSJ_2_wid.csv', sep='\t', encoding='UTF-8')
