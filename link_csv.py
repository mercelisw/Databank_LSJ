import pandas as pd
import re

pattern = r".perseus-\w+\d" #to remove .perseus-grc1 etc.

def urn_to_ids(ref: str):  # Returns a dictionary containing the doc-id and the subdoc
    temp_ref = re.sub(pattern, '', ref)
    temp_ref = ''.join(digit for digit in temp_ref if not digit.isalpha())  #removes other non-numerics
    temp_ref = temp_ref[3:-1]                                                #removes initial : and final character
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


for index, link in lsj.iterrows():
    reference = link['ref']
    key = link['key']
    result = []

    if index%10 == 0:
        print(index)

    if reference.startswith('urn'):
        bibliography = urn_to_ids(reference)

        if bibliography['subdoc'] != "":
            mask = ((xml['doc'].values == bibliography['doc']) & (xml['subdoc'].values == bibliography['subdoc']) \
                   & (xml['lemma'].values == key))
            doc_subdoc = xml[mask]
            for i, hit in doc_subdoc.iterrows():

                word_id = hit['word']
                result.append(word_id)

    else:
        pass             #TODO handling of non-urn links!!

    lsj.at[index, 'word_id'] = result

lsj.to_csv('tst/LSJ_2_wid.csv', sep='\t', encoding = 'UTF-8')

