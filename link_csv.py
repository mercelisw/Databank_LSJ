import pandas as pd
import re

pattern = r".perseus-\w+\d" #to remove .perseus-grc1 etc.

def urn_to_ids(ref: str):  # Returns a dictionary containing the doc-id and the subdoc
    temp_ref = re.sub(pattern, '', ref)
    temp_ref = ''.join(digit for digit in temp_ref if not digit.isalpha())  #removes other non-numerics
    temp_ref = temp_ref[3:]                                                #removes initial :
    temp_ref = temp_ref.replace(':', '.')                                   #removes remaining :
    cleaned_ref = temp_ref.replace('.', ':', 2)                      #split between author/work/subdoc is : otherwise .

    reference_fields = cleaned_ref.split(':')

    while len(reference_fields) < 3:
        reference_fields.append(None)

    return {'doc': reference_fields[0] + '-' + reference_fields[1], 'subdoc': str(reference_fields[2])}


xml = pd.read_csv('lemma_lookup.csv', sep='\t', encoding='UTF-8', names=['doc', 'subdoc', 'sentence', 'word', 'lemma'],
                 dtype={'doc': str, 'subdoc': str, 'sentence': int, 'word': int, 'lemma': str})

lsj = pd.read_csv('tst/LSJ_2.csv', sep='\t', encoding='UTF-8', names=['id', 'key', 'sense_1', 'sense_2', 'sense_3',
                                                                      'sense_4', 'translation', 'ref'],
                  dtype={'id': int, 'key': str, 'sense_1': str, 'sense_2': str, 'sense_3' : int, 'sense_4': str,
                         'translation': str, 'ref': str})
lemma = []
lsj['word_id'] = ""


for row in lsj.itertuples():
    reference = row.ref
    key = row.key
    result = []

    if row.Index % 10 == 0:
        print(row.Index)

    if reference.startswith('urn'):
        bibliography = urn_to_ids(reference)

        if bibliography['subdoc'].isdigit() :
            mask = ((xml['doc'].values == bibliography['doc']) &
                    (xml['subdoc'].values == str(int(bibliography['subdoc']) - 1)) &
                    (xml['lemma'].values == key))
            doc_subdoc = xml[mask]
            for doc_row in doc_subdoc.itertuples():

                word_id = doc_row.word
                result.append(word_id)

    else:
        pass             #TODO handling of non-urn links!!

    lsj.at[row.Index, 'word_id'] = result

lsj.to_csv('tst/LSJ_2_wid_only_direct.csv', sep='\t', encoding = 'UTF-8')

