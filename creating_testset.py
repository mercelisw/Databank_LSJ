import pandas as pd
import unicodedata as ucd


chosen_words = ['εἰς', 'λέγω', 'ἄλλος', 'πόλις', 'οὐδείς', 'ὦ', 'λαμβάνω', 'ἔτι', 'παῖς', 'ἀγαθός']
position_in_alphabet = {'α': '1', 'β': '2', 'γ': '3', 'δ': '4', 'ε': '5', 'ζ': '7', 'η': '8', 'θ': '9',
                        'ι': '10', 'κ': '11', 'λ': '12', 'μ': '13', 'ν': '14', 'ξ': '15', 'ο': '16',
                        'π': '17', 'ρ': '20', 'σ': '21', 'τ': '22', 'υ': '23', 'φ': '24', 'χ': '25',
                        'ψ': '26', 'ω': '27'}# watch out for combined accents and accents integrated in the character

def first_letter_without_accents(word:str):
    norm_word = ucd.normalize('NFKD', word)
    return norm_word[0]

for chosen_word in chosen_words:
    position = position_in_alphabet[first_letter_without_accents(chosen_word)]

    lsj = pd.read_csv('LSJ_words/LSJ_{}_words.csv'.format(position), sep='\t', encoding='UTF-8')

#TODO formatting the word column, no strings but ints or lists of ints


    chosen_word_lsj = lsj[lsj['lemma'] == chosen_word]

#TODO search for all occurrences of chosen_word in XML

#TODO exclude all in chosen_word_lsj

#TODO random subset for test