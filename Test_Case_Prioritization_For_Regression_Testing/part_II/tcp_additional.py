import re
import collections
import argparse
import subprocess
from os import path
from collections import OrderedDict

Parser = argparse.ArgumentParser()
Parser.add_argument('-path', dest='param1', type=str)
params = Parser.parse_args()
print("processing...")

caller_callee_dict = {} # dictionary of caller callee functoins {func1:[A, B, C], func2:[A, B, C], ...}
caller_callee_dic_count = dict()
caller_callee_ordered_dict = dict()
caller_callee_method_count_dict = dict()
tcp_additional_method_coverage_dict = dict()
text_file = params.param1
project_method_level_txt = path.join(path.dirname(__file__), '../data', text_file)

def main():
    functions = []
    caller_functions = []
    callee = ""
    caller = ""
    global caller_callee_dict
    global caller_callee_dic_count
    global caller_callee_ordered_dict
    global tcp_additional_method_coverage_dict
    global project_method_level_txt
    with open('call-graph.txt','r') as fp:
    # with open('cg2.txt','r') as fp:
        caller_callee_dict = collections.defaultdict(list)
        for line in fp:
            array_line = line.strip().split(' ')
            if(check_text(array_line[0])):       
                full_caller_name = array_line[0][2::]
                caller_functions.append(full_caller_name)

                callee = array_line[1][3::] 
                caller = array_line[0][2::]       
                
                # append the callee function to the functions list               
                functions.append(callee)
                caller_callee_dict[caller].append(callee)

    # perform caller function expantion
    for func in caller_functions:
        for key, value in caller_callee_dict.items(): 
            if func in value:
                # value.remove(func)
                value = value + caller_callee_dict[func]
                # caller_callee_dict[key] = list(set(value))

    # eleminate duplicates in caller callee dictionary
    for key, value in caller_callee_dict.items():
        caller_callee_dict[key] = list(set(value))
    
    # for key, value in caller_callee_dic.items():
    #         caller_callee_dic_count[key] = len(value)
    
    functions = list(set(functions))

    additional_method_coverage(functions)
    output_total_coverage()
    calculate_APFD()
        
# clean the caller functions
def check_text(text):
    test_method = text.split(":")
    if(text[0] == 'M' and re.search('test', test_method[2])):
        return True
    else: 
        return False
                             
# perform the method coverage according to the max number of methods that have not been covered already
def additional_method_coverage(functions):
    while (len(functions) != 0): 
        caller_callee_method_count_dict.clear()     
        for key, value in caller_callee_dict.items():
            method_counter = 0
            for method in value:
                if(method in functions):
                    method_counter += 1
            caller_callee_method_count_dict[key] = method_counter
        max_tuple_method = get_max_uncovered_methods(caller_callee_method_count_dict)
        tcp_additional_method_coverage_dict[max_tuple_method[0]] = caller_callee_dict[max_tuple_method[0]]
        covered_methods = set(caller_callee_dict[max_tuple_method[0]])
        functions = list(filter(lambda x: x not in covered_methods, functions))
                    
# get the max number of test cases that have not been covered previously
def get_max_uncovered_methods(caller_callee_method_count_dict):
    caller_callee_tuple_list = caller_callee_method_count_dict.items()
    caller_callee_tuple_list = list(caller_callee_tuple_list)
    caller_callee_tuple_list = sorted(caller_callee_tuple_list, key = lambda x: x[1], reverse=True)
    return caller_callee_tuple_list[0]
        
# form the output to a text file
def output_total_coverage():
    file1 = open(r"../data/mahout-additional-result.txt","w")
    for key, value in tcp_additional_method_coverage_dict.items():
        i=0
        num_items = len(value)
        key1 = key.split(".")        
        class_method = key1[len(key1) - 1].split(':')
        if(len(class_method) > 1):
            tester_class = class_method[0]
            tester_method = class_method[1]
            string = ""
            for item in value:
                item1 = item.split(":")
                # class_method = item1[len(item1) - 1].split(':')
                if(len(item1) > 1):
                    t_class = item1[0].split('.')
                    tested_class = t_class[len(t_class) - 1]
                    tested_method = item1[1] 
                    if i != num_items - 1:
                        string += tested_class + '.' + tested_method +  ', '  
                    else:
                        string += tested_class + '.' + tested_method 
                i += 1
            file1.write(tester_class + '.' + tester_method + ": " + '[' + string + ']' + '\n')
    file1.close()

# calculate the value of APFD accroding to the faults given
def calculate_APFD():
    tf_sum = 0
    numt = len(open('../data/mahout-additional-result.txt').readlines())
    numf = len(open('faults.txt').readlines())
    faults_file = open('faults.txt','r')
    with open('../data/mahout-additional-result.txt','r') as fp:
        for line in faults_file:
            tf = 0
            i = 0
            fault_line_list = line.strip().split('.')
            fault_method = fault_line_list[len(fault_line_list) - 1]
            for i, line in enumerate(fp):
                coverage_line_list = line.strip().split(':')
                tester_class_method = coverage_line_list[0]
                # if(fault_method+"()" in tester_class_method):
                if(re.search(fault_method+"()", tester_class_method)):
                    tf = i
                    tf_sum += tf
                    break
            fp.seek(0)
    faults_file.close()
    APFD = 1 - (tf_sum/(numt*numf) + 1/(2*numt))  
    apfd_file = open(r"../data/mahout-additional-apfd.txt","w")   
    apfd_file.write(str(APFD))  
    apfd_file.close()         
                                            
if __name__ == "__main__":
    main()
