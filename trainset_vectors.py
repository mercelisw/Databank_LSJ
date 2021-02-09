import pandas as pd
import unicodedata as ucd

chosen_words = ['εἰς', 'λέγω', 'ἄλλος', 'πόλις', 'οὐδείς', 'ὦ', 'λαμβάνω', 'ἔτι', 'παῖς', 'ἀγαθός']
position_in_alphabet = {'α': '1', 'β': '2', 'γ': '3', 'δ': '4', 'ε': '5', 'ζ': '7', 'η': '8', 'θ': '9',
                        'ι': '10', 'κ': '11', 'λ': '12', 'μ': '13', 'ν': '14', 'ξ': '15', 'ο': '16',
                        'π': '17', 'ρ': '20', 'σ': '21', 'τ': '22', 'υ': '23', 'φ': '24', 'χ': '25',
                        'ψ': '26', 'ω': '27'}  # watch out for combined accents and accents integrated in the character


def first_letter_without_accents(word: str):
    norm_word = ucd.normalize('NFKD', word)
    return norm_word[0]

training_vector = pd.read_csv('vectors_training.csv', sep='\t', encoding='UTF-8', header=None)

## Concatenate the 100 vectors into one df.column

concat_training_vector = training_vector.loc[:,1].astype(str) + ', ' + training_vector.loc[:,2].astype(str)

for i in range(98): #100 vectors expected
    concat_training_vector = concat_training_vector + ', ' + training_vector.loc[:, i + 2].astype(str)


training_vector_df = training_vector.loc[:, 0].to_frame()
training_vector_df['vectors'] = concat_training_vector
training_vector_df.columns = ['word', 'vectors']

all_chosen_word_lsj = []

for chosen_word in chosen_words:
    print(chosen_word)
    position = position_in_alphabet[first_letter_without_accents(chosen_word)]

    lsj = pd.read_csv('LSJ_words/LSJ_{}_words.csv'.format(position), sep='\t', encoding='UTF-8')

    chosen_word_lsj = lsj[lsj['lemma'] == chosen_word]                      #filter on word

    chosen_word_lsj['word'] = chosen_word_lsj['word'].dropna().apply(
        lambda x: list(map(int, x.strip('[]\'\'').split(', '))))            #convert strings of lists to actual lists

    cleaned_word_lsj = chosen_word_lsj[(chosen_word_lsj.word.str.len() <= 3)].explode('word')
    #drop excessively long lists and explodes the lists into rows

    all_chosen_word_lsj.append(cleaned_word_lsj)


senses_df = pd.concat(all_chosen_word_lsj)
senses_df.drop(columns=['Unnamed: 0', 'id', 'doc', 'subdoc', 'sentence', 'line'], inplace=True)


xml = pd.read_csv('lemma_lookup.csv', sep='\t', encoding='UTF-8',
                  names=['doc', 'subdoc', 'sentence', 'line', 'word', 'lemma', 'form'],
                  dtype={'doc': str, 'subdoc': str, 'sentence': int, 'line': str,
                         'word': int, 'lemma': str, 'form': str})

chosen_xml = xml[xml['lemma'].isin(chosen_words)]
chosen_xml.drop(columns=['sentence', 'line'], inplace=True)

combined_senses = pd.merge(chosen_xml, senses_df, on=['word', 'lemma', 'form'])

final_training_data = pd.merge(combined_senses, training_vector_df, on='word')

final_training_data.to_csv('training_data_vectors.csv', sep='\t', encoding='UTF-8')
