import pandas as pd

combined_senses = pd.read_excel('senses_test_data.xlsx')
combined_senses.drop(columns=['Column1', 'sentence', 'line', 'context'], inplace=True)

test_vector = pd.read_csv('vectors_test.csv', sep='\t', encoding='UTF-8', header=None)

## Concatenate the 100 vectors into one df.column

concat_test_vector = test_vector.loc[:, 1].astype(str) + ', ' + test_vector.loc[:, 2].astype(str)

for i in range(98): #100 vectors expected
    concat_test_vector = concat_test_vector + ', ' + test_vector.loc[:, i + 2].astype(str)


test_vector_df = test_vector.loc[:, 0].to_frame()
test_vector_df['vectors'] = concat_test_vector
test_vector_df.columns = ['word', 'vectors']

final_test_data = pd.merge(combined_senses, test_vector_df, on='word')

final_test_data.to_csv('test_data_vectors.csv', sep='\t', encoding='UTF-8')