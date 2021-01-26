import pandas as pd
import numpy as np
import re

pattern = r".perseus-\w+\d"  # to remove .perseus-grc1 etc.

def urn_to_ids(ref: str):  # Returns a string: doc \t subdoc
    temp_ref = re.sub(pattern, '', ref)
    temp_ref = ''.join(digit for digit in temp_ref if not digit.isalpha())  # removes other non-numerics
    temp_ref = temp_ref[3:]  # removes initial :
    temp_ref = temp_ref.replace(':', '.')  # removes remaining :
    cleaned_ref = temp_ref.replace('.', ':', 2)  # split between author/work/subdoc is : otherwise .
    reference_fields = cleaned_ref.split(':')
    while len(reference_fields) < 3:
        reference_fields.append(None)
    return reference_fields[0] + '-' + str(reference_fields[1]) + '\t' + str(reference_fields[2])


xml = pd.read_csv('lemma_lookup.csv', sep='\t', encoding='UTF-8', names=['doc', 'subdoc', 'sentence', 'line', 'word', 'lemma'],
                 dtype={'doc': str, 'subdoc': str, 'sentence': int, 'line': str, 'word': str, 'lemma': str})
lsj = pd.read_csv('first1000.csv', sep='\t', encoding='UTF-8', names=['id', 'key', 'sense_1', 'sense_2', 'sense_3',
                                                                      'sense_4', 'translation', 'ref'],
                  dtype={'id': int, 'key': str, 'sense_1': str, 'sense_2': str, 'sense_3' : int, 'sense_4': str,
                         'translation': str, 'ref': str})


lsj['ref'] = lsj['ref'].apply(urn_to_ids)           # removes the unwieldy urn
split = lsj['ref'].str.split('\t', expand=True)
lsj = pd.concat([lsj, split], axis=1)

lsj.rename(columns={'key': 'lemma', 0: 'doc', 1: 'subdoc'}, inplace=True)   # rename columsn to match with xml

lsj['subdoc'] = pd.to_numeric(lsj['subdoc'], errors='coerce')
lsj.sort_values(by=['subdoc'], inplace=True)                                # sorting for the merge_asof

xml['subdocstring'] = xml['subdoc']                                         # extra column to store non-numeric subdocs

xml['subdoc'] = pd.to_numeric(xml['subdoc'], errors='coerce')
xml.sort_values(by=['subdoc'], inplace=True)

# Try to merge on subdoc

subdoc_merge = pd.merge_asof(lsj[lsj['subdoc'].notna()], xml[xml['subdoc'].notna()], on=['subdoc'], by=['lemma', 'doc'], tolerance = 4)  # merge on subdoc, with tolerance 4 for line per 5



lsj.rename(columns={'subdoc': 'line'}, inplace=True)   # rename columsn to match with xml
xml['line'] = pd.to_numeric(xml['line'], errors='coerce')
xml.sort_values(by=['line'], inplace=True)

subdoc_merge_lines = pd.merge_asof(lsj[lsj['line'].notna()], xml[xml['line'].notna()], on=['line'], by=['lemma', 'doc'], tolerance = 4)  # merge on subdoc, with tolerance 4 for line per 5

subdoc_merge_docs = pd.merge(lsj[lsj['doc'].notna()], xml[xml['doc'].notna()], on=['doc', 'lemma'])

#TODO Try to merge on line


test = subdoc_merge[subdoc_merge['word'].notnull()]
test_line = subdoc_merge_lines[subdoc_merge_lines['word'].notnull()]
subdoc_merge.fillna(subdoc_merge_lines, inplace=True) # fills remaining NaN results from lines
# subdoc_merge.fillna(subdoc_merge_docs, inplace=True)



failed_merge = subdoc_merge[subdoc_merge['word'].isnull()]

test_docs = subdoc_merge_docs.groupby(['id', 'lemma', 'sense_1','sense_2','sense_3','sense_4','doc'], as_index=False).agg({'word': lambda x: str(list(x))})

mergetest = failed_merge.drop(columns=['word']).merge(test_docs, 'left', on = ['id', 'lemma', 'sense_1','sense_2','sense_3','sense_4','doc'])
test_mergetest = mergetest[mergetest['word'].notnull()]



test = subdoc_merge[subdoc_merge['word'].notnull()]
#concatenate

subdoc_merge.sort_index(inplace=True)

result = pd.concat([test, mergetest])

test_result = result[result['word'].notnull()]
result.sort_values(by=['id', 'sense_1', 'sense_2', 'sense_3', 'sense_4'], inplace=True)

1==1
# print(subdoc_merge.head())
#
# print(subdoc_merge)
# print(subdoc_merge['word'].isna().sum())