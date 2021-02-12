import pandas as pd
import os
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


xml = pd.read_csv('lemma_lookup.csv', sep='\t', encoding='UTF-8',
                  names=['doc', 'subdoc', 'sentence', 'line', 'word', 'lemma', 'form'],
                  dtype={'doc': str, 'subdoc': str, 'sentence': int, 'line': str,
                         'word': str, 'lemma': str, 'form':str})

xml['subdocstring'] = xml['subdoc']  # extra column to store non-numeric subdocs

xml['subdoc'] = pd.to_numeric(xml['subdoc'], errors='coerce', downcast='float')  # same process as lsj

xml['line'] = pd.to_numeric(xml['line'], errors='coerce', downcast='float')  # cf supra

for index in range(len(os.listdir('LSJ_output'))):
    print(index + 1)

    file = open('LSJ_output/LSJ_{}.csv'.format(index + 1), encoding='UTF-8')
    if len(file.readlines()) < 2:
        file.close()
        continue

    else:
        file.close()
        lsj = pd.read_csv('LSJ_output/LSJ_{}.csv'.format(index + 1), sep='\t', encoding='UTF-8',
                          names=['id', 'key', 'sense_1', 'sense_2', 'sense_3', 'sense_4', 'translation', 'ref'],
                          dtype={'id': int, 'key': str, 'sense_1': str, 'sense_2': str, 'sense_3': int, 'sense_4': str,
                                 'translation': str, 'ref': str})

    lsj['ref'] = lsj['ref'].apply(urn_to_ids)  # removes the unwieldy urn
    split = lsj['ref'].str.split('\t', expand=True)
    lsj = pd.concat([lsj, split], axis=1)  # new reference in dataframe

    lsj.rename(columns={'key': 'lemma', 0: 'doc', 1: 'subdoc'}, inplace=True)  # rename columns to match with xml
    lsj['lemma'] = lsj['lemma'].str.replace('\d+', '')              # removing unwanted digits in lemmata
    lsj['subdoc'] = pd.to_numeric(lsj['subdoc'], errors='coerce',
                                  downcast='float')  # merge_asof needs numbers, bonus: subdocs like 1.3 become floats
    lsj.sort_values(by=['subdoc'], inplace=True)  # sorting for the merge_asof

    # TRY TO MERGE ON SUBDOC
    xml.sort_values(by=['subdoc'], inplace=True)
    subdoc_merge = pd.merge_asof(lsj[lsj['subdoc'].notna()], xml[xml['subdoc'].notna()],
                                 on=['subdoc'], by=['lemma', 'doc'], tolerance=4)

    # merge on subdoc, with tolerance 4 for lines numbered per 5

    # TRY TO MERGE ON LINE NUMBER

    lsj.rename(columns={'subdoc': 'line'}, inplace=True)  # rename columns to match with xml

    xml.sort_values(by=['line'], inplace=True)

    line_merge = pd.merge_asof(lsj[lsj['line'].notna()], xml[xml['line'].notna()],
                               on=['line'], by=['lemma', 'doc'], tolerance=4)
    # merge on line, with tolerance 4 for lines numbered per 5

    # TRY TO MERGE SOLELY ON DOC NUMBER

    doc_merge = pd.merge(lsj[lsj['doc'].notna()], xml[xml['doc'].notna()], on=['doc', 'lemma'])

    # test = subdoc_merge[subdoc_merge['word'].notnull()]
    # test_line = line_merge[line_merge['word'].notnull()]

    # COMBINE RESULTS

    subdoc_merge.fillna(line_merge, inplace=True)  # fills remaining NaN results from lines
    # subdoc_merge.fillna(subdoc_merge_docs, inplace=True)

    failed_merge = subdoc_merge[subdoc_merge['word'].isnull()]  # no words found

    words_in_docs = doc_merge.groupby(['id', 'lemma', 'sense_1', 'sense_2', 'sense_3', 'sense_4', 'doc'],
                                      as_index=False).agg({'word': lambda x: str(list(x))})
    # Words grouped per document per sense

    only_in_docs = failed_merge.drop(columns=['word']).merge(words_in_docs, 'left',
                                                             on=['id', 'lemma', 'sense_1', 'sense_2',
                                                                 'sense_3', 'sense_4', 'doc'])
    # Combine failed_merge (words not yet found) with the words found in docs

    # CONCATENATE RESULTS

    subdoc_line_hits = subdoc_merge[subdoc_merge['word'].notnull()]
    # As the words found in docs are taken from failed_merge (which contains the isnull values)
    # we should remove them here

    combined = pd.concat([subdoc_line_hits, only_in_docs])

    # Sorting for better readability
    combined.sort_values(by=['id', 'sense_1', 'sense_2', 'sense_3', 'sense_4'], inplace=True)
    lsj.sort_values(by=['id', 'sense_1', 'sense_2', 'sense_3', 'sense_4'], inplace=True)

    # Merge to return a dataframe like the first lsj, but with the referenced words
    result = lsj.rename(columns={'line': 'subdoc'}).merge(combined, how='left',
                                                          on=['id', 'lemma', 'sense_1', 'sense_2', 'sense_3', 'sense_4',
                                                              'translation', 'ref', 'doc', 'subdoc'])
    result.drop(columns=['ref', 'subdocstring'], inplace=True)  # remove redundant columns

    result['word'] = result['word'].dropna().apply(lambda x: list(map(int, x.strip('[]\'\'').split('\', \''))))
    # converting strings to lists of ints, by stripping brackets and quotes, and splitting on "', '"

    result.to_csv('LSJ_words/LSJ_{}_words.csv'.format(index + 1), sep='\t', encoding='UTF-8')  # write to csv

    # TESTING

    # test = subdoc_merge[subdoc_merge['word'].notnull()]
    # test_line = line_merge[line_merge['word'].notnull()]
    # test_only_in_docs = only_in_docs[only_in_docs['word'].notnull()]
    # test_result = result[result['word'].notnull()]
