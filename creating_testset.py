import numpy as np
import pandas as pd
import random
import unicodedata as ucd

chosen_words = ['εἰς', 'λέγω', 'ἄλλος', 'πόλις', 'οὐδείς', 'ὦ', 'λαμβάνω', 'ἔτι', 'παῖς', 'ἀγαθός']
position_in_alphabet = {'α': '1', 'β': '2', 'γ': '3', 'δ': '4', 'ε': '5', 'ζ': '7', 'η': '8', 'θ': '9',
                        'ι': '10', 'κ': '11', 'λ': '12', 'μ': '13', 'ν': '14', 'ξ': '15', 'ο': '16',
                        'π': '17', 'ρ': '20', 'σ': '21', 'τ': '22', 'υ': '23', 'φ': '24', 'χ': '25',
                        'ψ': '26', 'ω': '27'}  # watch out for combined accents and accents integrated in the character


def first_letter_without_accents(word: str):
    norm_word = ucd.normalize('NFKD', word)
    return norm_word[0]

def include_context(word_id: int):
    index = word_id - 1

    # Need rows with sentence of word_id, doc and subdoc should be equal as well
    context = xml[(xml['sentence'] == xml['sentence'][index]) & (xml['doc'] == xml['doc'][index]) & (
                xml['subdoc'] == xml['subdoc'][index])]

    return ' '.join(context['form'].values) # return a string with the corresponding form values


xml = pd.read_csv('lemma_lookup.csv', sep='\t', encoding='UTF-8',
                  names=['doc', 'subdoc', 'sentence', 'line', 'word', 'lemma', 'form'],
                  dtype={'doc': str, 'subdoc': str, 'sentence': int, 'line': str,
                         'word': int, 'lemma': str, 'form': str})
test_data = []

for chosen_word in chosen_words:
    print(chosen_word)
    position = position_in_alphabet[first_letter_without_accents(chosen_word)]

    lsj = pd.read_csv('LSJ_words/LSJ_{}_words.csv'.format(position), sep='\t', encoding='UTF-8')

    chosen_word_lsj = lsj[lsj['lemma'] == chosen_word]

    chosen_word_lsj['word'] = chosen_word_lsj['word'].dropna().apply(
        lambda x: list(map(int, x.strip('[]\'\'').split(', '))))  # convert string of list to actual list

    raw_training_data = chosen_word_lsj['word'].dropna().values  # list of occurrences
    result = []
    for data in raw_training_data:
        if len(data) <= 3:  # filter out excessively long lists
            result.append(data)
    training_data_ids = set(np.hstack(result))

    # Search for all occurrences of chosen_word in XML

    chosen_xml = xml[xml['lemma'] == chosen_word]

    # Exclude all in chosen_word_lsj

    all_xml_data = chosen_xml['word'].values
    possible_test_data = [word for word in all_xml_data if word not in training_data_ids]
    training_data = [word for word in all_xml_data if word in training_data_ids]

    # Random subset for test

    random.seed(42)  # set seed to ensure that the test set is random, but every time the same
    test_data.append(random.sample(possible_test_data, 20))

flat_test_data = [word for per_word_data in test_data for word in per_word_data] # flatten the list of test data


all_context = []                                        #Adding context
for index, word in enumerate(sorted(flat_test_data)):
    print(index)
    all_context.append(include_context(word))

test_data_xml = xml[xml['word'].isin(flat_test_data)]
test_data_xml['context'] = all_context

test_data_xml.to_csv('test_data.csv', sep='\t', encoding='UTF-8')
