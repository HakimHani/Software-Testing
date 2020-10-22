import numpy as np
import csv as csv
import pandas as pd
from os import path
import argparse
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


Parser = argparse.ArgumentParser()
Parser.add_argument('-proj', dest='param1', type=str, default='jackrabbit')
params = Parser.parse_args()
project = params.param1
accuracy = 0
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

    svm = LinearSVC(penalty='l1', dual=False, max_iter=10000000, loss='squared_hinge',tol=1e-3)
    svm.fit(train_data, train_target)
    test_pred = svm.predict(test_data)
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
    for folder in data_folders:
        training_data_file = path.join(path.dirname(__file__), './' + project + '/' + project + '/' + folder + '/' + input_file_training)
        testing_data_file = path.join(path.dirname(__file__), './' + project + '/' + project + '/' + folder + '/' + input_file_test)
        calculate_performance(training_data_file, testing_data_file)
    F1 = calculate_f1_score()
    print(project + ", F1:" + " " +  str(F1))
    print("accuracy is: ", str(accuracy/6*100) + '%')

if __name__ == "__main__":
    main()
    



