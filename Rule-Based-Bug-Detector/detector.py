import re
import collections
import argparse
import subprocess
from os import path
from itertools import combinations

Parser = argparse.ArgumentParser()
Parser.add_argument('-sup', dest='param1', type=int)
Parser.add_argument('-c', dest='param2', type=float)
Parser.add_argument('-jar', dest='param3', type=str)
Parser.add_argument('-inp', dest='param4', type=bool, default=False)
params = Parser.parse_args()
print("processing files...")

sup = {} # dictionary to hold the support of each callee function
fucn_pair_sup = {} # dictionary to hold the function pair suppot
caller_callee_dic = {} # dictionary of caller callee functoins {func1:[A, B, C], func2:[A, B, C], ...}
funcs_hash_map = {} # dictionary of mappring functoins to thier hash values
caller_callee_dic_hash_value = {} # dictionary to hold the hash values of callee functions {func1:[1,2,3], func2:[4,5,6], ...} where the integer values are hashes of functions
combination_pairs_dict = {} # dictionary to hold the combinations pairs {func1:[(1,2),(5,6)], func2:[(3,4)], ...} where integers are hash values of functions A, B etc...
pairs_array = [] 
pairs_array_multiples = []
c = params.param2
s = params.param1
jar = params.param3
flag = params.param4
jar_path = path.join(path.dirname(__file__), '../proj/' + jar)
f = open("call-graph.txt", "w")
subprocess.call(["java", "-jar", "javacg-0.1-SNAPSHOT-static.jar", jar_path], stdout=f)

def main():
    functions = []
    caller_functions = []
    callee = ""
    caller = ""
    global sup
    global caller_callee_dic
    global c
    global s
    global jar
    with open('call-graph.txt','r') as fp:
    #with open('cg2.txt','r') as fp:
        caller_callee_dic = collections.defaultdict(list)
        for line in fp:
            array_line = line.strip().split(' ')
            if(check_text(array_line[0])):
                # class_type_1 = array_line[0] 
                if(flag):         
                    full_caller_name = array_line[0][2::]
                    caller_functions.append(full_caller_name)

                callee = array_line[1][3::] 
                caller = array_line[0][2::]       
                # class_func_1 = class_type_1.split(':')
                # caller = class_func_1[len(class_func_1) - 1]
                
                # append the callee function to the functions list               
                functions.append(callee)
                caller_callee_dic[caller].append(callee)
  
    # perform caller function expantion
    if(flag):
        for func in caller_functions:
            for key, value in caller_callee_dic.items(): 
                if func in value:
                    value.remove(func)
                    value = value + caller_callee_dic[func]
                    caller_callee_dic[key] = list(set(value))

    # eleminate duplicates in caller callee dictionary
    for key, value in caller_callee_dic.items():
        caller_callee_dic[key] = list(set(value))

    support(functions)
    hash_map_funcs(sorted(list(set(functions))))
    map_callee_funcs_to_hash_value()
    form_combination_pairs()
    pair_support()
    predict_bugs()

# clean the caller functions
def check_text(text):
    flag = True
    if(text[0] != 'M' or re.search('java.lang.Object:<init>',text) or re.search('main',text)):
        flag = False
    return flag
    
# find the support of callee functios {func1:4, func2:6, ...}
def support(funcs):
    for func in funcs:
        if(func in sup):
            sup[func] +=1 
        else:
            sup[func] = 1

# map each function to a hash value
def hash_map_funcs(funcs):
    global funcs_hash_map
    for index, func in enumerate(funcs):
        funcs_hash_map[func] = index

# map functions in the vlaues of the dictoinary to hash values for easy comparison {func1:[1,2,3,6, ..], func2:[1,5,6,...], ...}
def map_callee_funcs_to_hash_value():
    global caller_callee_dic_hash_value
    caller_callee_dic_hash_value = collections.defaultdict(list) 
    for key,value in caller_callee_dic.items():
        for item in value:
            caller_callee_dic_hash_value[key].append(funcs_hash_map[item])

# form the combinations of pairs array [(6,8), (3,5), ...]
def form_combination_pairs():
    global combination_pairs_dict
    global pairs_array
    combination_pairs_dict = collections.defaultdict(list) 
    for key, value in caller_callee_dic_hash_value.items():
        comb = list(combinations(sorted(value),2))
        combination_pairs_dict[key] = comb
    for key, value in combination_pairs_dict.items():
        for tup in value:
            pairs_array.append(tup)
    pairs_array = list(set(pairs_array))
                         
# find the support of all pairs {(5,7):4, (8,9):2, ...}
def pair_support():
    global pairs_array_multiples
    for key, value in combination_pairs_dict.items():
        for val in value:
            pairs_array_multiples.append(val)
    for item in pairs_array_multiples:
        if(item in fucn_pair_sup):
                fucn_pair_sup[item] +=1
        else:
            fucn_pair_sup[item] = 1

# make the rules and print bugs
def predict_bugs():
    for pair in pairs_array:
        key1 = get_key(pair[0])
        key2 = get_key(pair[1])
        conf1 = (fucn_pair_sup[pair]/float(sup[key1]))
        if(conf1 > c and fucn_pair_sup[pair] >= s):
            for key, value in caller_callee_dic.items():
                if(key1 in value and key2 not in value):
                    key = key.split(":")
                    caller1 = key[len(key)-1]
                    print("bug: " + key1[:key1.index("(")] + " in " + caller1 + " pair: " + "(" + key1[:key1.index("(")] + ", " + key2[:key2.index("(")] + ")" + ", " + "support: " + str(fucn_pair_sup[pair]) + ", " + "confidence: " + str(conf1*100) + "%")
        conf2 = float(fucn_pair_sup[pair]/float(sup[key2]))

        if(conf2 > c and fucn_pair_sup[pair] >= s):  
            for key, value in caller_callee_dic.items():
                if(key2 in value and key1 not in value):
                    key = key.split(":")
                    caller2 = key[len(key)-1]
                    print("bug: " + key2[:key2.index("(")] + " in " + caller2 + " pair: " + "(" + key1[:key1.index("(")] + ", " + key2[:key2.index("(")] + ")" ", " + "support: " + str(fucn_pair_sup[pair]) + ", " + "confidence: " + str(conf2*100) + "%")

# get the key from the dictionary
def get_key(val): 
    for key, value in funcs_hash_map.items(): 
        if val == value: 
            return key
                                 
if __name__ == "__main__":
    main()