import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

#Load data with vectors
train_df = pd.read_csv('training_data_vectors_arxh.csv', sep= '\t', encoding='UTF-8')
test_df = pd.read_csv('test_data_vectors_arxh.csv', sep= '\t', encoding='UTF-8')


#Convert vector strings to proper floats
train_df['vectors'] = train_df['vectors'].apply(lambda y: [float(x) for x in y.split(', ')])
test_df['vectors'] = test_df['vectors'].apply(lambda y: [float(x) for x in y.split(', ')])

#Initialize random forest
forest = RandomForestClassifier(n_estimators = 25)

#Fit forest to training data
forest = forest.fit(train_df['vectors'].to_list(), train_df['sense_2'].to_list())

#Predict results
result = forest.predict(test_df['vectors'].to_list())

#Print out report
print(classification_report(test_df['sense_2'].to_list(), result))