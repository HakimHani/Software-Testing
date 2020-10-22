import numpy as np
import csv as csv
import pandas as pd
import os
from os import path
import argparse
import nltk
from nltk.corpus import stopwords
import string
from nltk.tokenize import word_tokenize, sent_tokenize
import re
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

Parser = argparse.ArgumentParser()
Parser.add_argument('-proj', dest='param1', type=str)
params = Parser.parse_args()
project = params.param1

accuracy = 0
false_positive = 0
false_negatitve = 0
true_positive = 0

def add_new_features():  

    data_folders = ['0', '1', '2', '3', '4', '5']

    input_file_training = "train.csv"
    input_file_test = "test.csv"

    for folder in data_folders:

        key_word_index = {}
        features_values = []
        test_features_values = []
        key_words_list = []

        training_data_file = path.join(path.dirname(__file__), './' + project + '/' + project + '/' + folder + '/' + input_file_training)
        testing_data_file = path.join(path.dirname(__file__), './' + project + '/' + project + '/' + folder + '/' + input_file_test)

        # load the training data as a dataframe
        training_set_df = pd.read_csv(training_data_file)
        testing_set_df = pd.read_csv(testing_data_file)
        change_id_series = training_set_df.change_id
        test_change_id_series = testing_set_df.change_id


        directory = os.path.join(path.dirname(__file__), project, project)

        key_word_count = {}
        stop_words = ['int', 'double', 'boolean', 'class', 'public', 'void', 'private']

        for change_id in change_id_series:
            for subdir, dirs, files in os.walk(directory):
                for file in files:
                    # print (os.path.join(subdir, file))
                    filepath = subdir + os.sep + file

                    if str(change_id) in file:
            #           print (file)
                        with open (filepath, 'r', encoding="ISO-8859-1") as f:
                            text = f.read()
                            tokens = word_tokenize(text)
                            tokens = [w.lower() for w in tokens]
                            table = str.maketrans('', '', string.punctuation)
                            stripped = [w.translate(table) for w in tokens]
                            words = [word for word in stripped if word.isalpha()]       
                            words = [w for w in words if w not in stop_words]
                            for word in words:  
                                if word not in key_word_count.keys(): 
                                    key_word_count[word] = 1
                                else: 
                                    key_word_count[word] += 1


        bag_of_words = { k:v for k,v in key_word_count.items() if v > 3 and  1 < len(k) < 20 }   

        for index, key in enumerate(bag_of_words):
            key_word_index [key] = index

        key_words_list = list(key_word_index.keys())

        for change_id in change_id_series:
            for subdir, dirs, files in os.walk(directory):
                for file in files:
                    # print (os.path.join(subdir, file))
                    filepath = subdir + os.sep + file
                    if str(change_id) in file:
                        with open (filepath, 'r', encoding="ISO-8859-1") as f:     
                            # tokens = word_tokenize(text)
                            vectorizer = CountVectorizer(input='file', decode_error='ignore', strip_accents='unicode', vocabulary=key_word_index)
                            # corpus = open(filepath, encoding="ISO-8859-1")
                            matrix = vectorizer.fit_transform([f]).toarray()
                            features_values.append(matrix[0])
        features_values = np.array(features_values)  
                
        df = pd.DataFrame(data=features_values[0:,0:],
                index=[i for i in range(features_values.shape[0])],
                columns=key_words_list)
                # columns=['f'+str(i) for i in range(features_values.shape[1])])

        for test_change_id in test_change_id_series:
            for subdir, dirs, files in os.walk(directory):
                for file in files:
                    # print (os.path.join(subdir, file))
                    filepath = subdir + os.sep + file
                    if str(test_change_id) in file:
                        with open (filepath, 'r', encoding="ISO-8859-1") as f:     
                            # tokens = word_tokenize(text)
                            vectorizer = CountVectorizer(input='file', decode_error='ignore', strip_accents='unicode', vocabulary=key_word_index)
                            # corpus = open(filepath, encoding="ISO-8859-1")
                            matrix = vectorizer.fit_transform([f]).toarray()
                            test_features_values.append(matrix[0])
        test_features_values = np.array(test_features_values)

        test_df = pd.DataFrame(data=test_features_values[0:,0:],
                index=[i for i in range(test_features_values.shape[0])],
                columns=key_words_list)
                # columns=['feature'+str(i) for i in range(test_features_values.shape[1])]) 

        training_set_df = pd.concat([training_set_df, df], ignore_index=False, axis=1).dropna()
        testing_set_df = pd.concat([testing_set_df, test_df], ignore_index=False, axis=1).dropna()
        # print(training_set_df.head())
        data = 'data'
        training_data_file = path.join(path.dirname(__file__), data, project, folder, input_file_training)
        testing_data_file = path.join(path.dirname(__file__), data, project, folder, input_file_test)
        training_set_df.to_csv(training_data_file, index=None)
        testing_set_df.to_csv(testing_data_file, index=None)


def calculate_performance(training_data_file, testing_data_file):

    global accuracy
    # load the training data as a matrix
    dataset = pd.read_csv(training_data_file, header=0)

    # separate the data from the target attributes
    train_data = dataset.drop('500_Buggy?', axis=1)

    # remove unnecessary features
    train_data = train_data.drop('412_full_path', axis=1)
    train_data = train_data.drop('411_commit_time', axis=1)
    #print(train_data)

    # the lables of training data. `label` is the title of the  last column in your CSV files
    train_target = dataset['500_Buggy?']

    # load the testing data
    dataset2 = pd.read_csv(testing_data_file, header=0)

    # separate the data from the target attributes
    test_data = dataset2.drop('500_Buggy?', axis=1)

    # remove unnecessary features
    test_data = test_data.drop('412_full_path', axis=1)
    test_data = test_data.drop('411_commit_time', axis=1)

    # the lables of test data
    test_target = dataset2['500_Buggy?']

    logistic_r = LogisticRegression(random_state=0, max_iter=120000, solver='lbfgs')
    test_pred = logistic_r.fit(train_data, train_target).predict(test_data)
    test_target = list(test_target)
    test_pred = list(test_pred)
    
    calculate_accuracy_data_pridiction(test_pred, test_target)
    
    accuracy = accuracy + accuracy_score(test_target, test_pred)
    
def calculate_accuracy_data_pridiction(test_pred, test_target):
    global true_positive
    global false_positive
    global false_negatitve
    i = 0
    for label in list(test_pred):
        if(label == 1 and test_target[i] == 1):
            true_positive += 1
        elif (label == 1 and test_target[i] == 0):
            false_positive += 1
        elif (label == 0 and test_target[i] == 1):
            false_negatitve += 1
        i = i + 1
    
def calculate_f1_score(): 
    Precision = 0
    Recall = 0
    F1 = 0
    if true_positive != 0: 
        Precision = true_positive/(true_positive + false_positive)
    if true_positive != 0: 
        Recall = true_positive/(true_positive + false_negatitve) 
    if Precision != 0: 
        F1 = (2 * Precision * Recall)/(Precision + Recall)
    return F1

def main():
    input_file_training = "train.csv"
    input_file_test = "test.csv"
    data_folders = ['0', '1', '2', '3', '4', '5']
    F1 = 0
    data = 'data'
    for folder in data_folders:
        training_data_file = path.join(path.dirname(__file__), data, project, folder, input_file_training)
        testing_data_file = path.join(path.dirname(__file__), data, project, folder, input_file_test)
        calculate_performance(training_data_file, testing_data_file)
    F1 = calculate_f1_score()
    print(project + " F1:" + " " +  str(F1))
    print("accuracy is: ", str(accuracy/6*100) + '%')


add_new_features()
main()


