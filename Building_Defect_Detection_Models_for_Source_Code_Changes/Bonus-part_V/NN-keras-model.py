import numpy as np
import csv as csv
import pandas as pd
import os
from os import path
import argparse
import nltk
import string
from nltk.tokenize import word_tokenize, sent_tokenize
import re
from sklearn.metrics import precision_recall_fscore_support
from sklearn.feature_extraction.text import CountVectorizer
from numpy import loadtxt
import tensorflow
from keras.models import Sequential
from keras.layers import Dense


Parser = argparse.ArgumentParser()
Parser.add_argument('-proj', dest='param1', type=str)
params = Parser.parse_args()
project = params.param1
false_positive = 0
false_negatitve = 0
true_positive = 0

def calculate_performance(training_data_file, testing_data_file):
    
    global accuracy

    # load the training data as a matrix
    dataset = pd.read_csv(training_data_file, header=0)

    # separate the data from the target attributes
    train_data = dataset.drop('500_Buggy?', axis=1)

    # remove unnecessary features
    train_data = train_data.drop('412_full_path', axis=1)
    train_data = train_data.drop('411_commit_time', axis=1)
    dim = len(train_data.columns)

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

    # define the kares model
    model = Sequential()
    model.add(Dense(12, input_dim=dim, activation='relu'))
    model.add(Dense(dim, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    # compile the keras model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # fit the keras model on the dataset
    model.fit(train_data, train_target, epochs=150, batch_size=10)

    # make class predictions with the model
    test_pred = model.predict_classes(test_data)
    
    test_target = list(test_target)
    test_pred = list(test_pred)

    calculate_accuracy_data_pridiction(test_pred, test_target)
    
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
    for folder in data_folders:
        training_data_file = path.join(path.dirname(__file__), project, project, folder,input_file_training)
        testing_data_file = path.join(path.dirname(__file__), './' + project + '/' + project + '/' + folder + '/' + input_file_test)
        calculate_performance(training_data_file, testing_data_file)
    F1 = calculate_f1_score()
    print(project + " F1:" + " " +  str(F1))

if __name__ == "__main__":
    main()
    


























    
#     i = 0
#     for label in list(test_pred):
#         if(label == 1 and test_target[i] == 1):
#             true_positive += 1
#         elif (label == 1 and test_target[i] == 0):
#             false_positive += 1
#         elif (label == 0 and test_target[i] == 1):
#             false_negatitve += 1
#         i = i + 1
    
#     Precision = true_positive/(true_positive + false_positive)
#     Recall = true_positive/(true_positive + false_negatitve)
#     F1 = (2 * Precision * Recall)/(Precision + Recall)

#     report = classification_report(test_target, test_pred, output_dict=True)
#     f1_score = report['1']['f1-score']
#     return f1_score

# def main():
#     input_file_training = "train.csv"
#     input_file_test = "test.csv"
#     F1_score = 0
#     F1 = 0
#     data_folders = ['0', '1', '2', '3', '4', '5']
#     for folder in data_folders:
#         training_data_file = path.join(path.dirname(__file__), './' + project + '/' + project + '/' + folder + '/' + input_file_training)
#         testing_data_file = path.join(path.dirname(__file__), './' + project + '/' + project + '/' + folder + '/' + input_file_test)
#         F1_score = F1_score + calculate_performance(training_data_file, testing_data_file)
#     print(project + " F1_score:" + " " +  str(F1_score/6))

# if __name__ == "__main__":
#     main()
    


