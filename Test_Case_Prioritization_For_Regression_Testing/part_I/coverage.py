import re
import collections
import argparse
import subprocess
from os import path
from itertools import combinations
from collections import OrderedDict

Parser = argparse.ArgumentParser()
Parser.add_argument('-path', dest='param1', type=str)
params = Parser.parse_args()
print("processing...")

caller_callee_dic = {} # dictionary of caller callee functoins {func1:[A, B, C], func2:[A, B, C], ...}
jar = params.param1
project = jar.split('.')
project = project[0]
jar_path = path.join(path.dirname(__file__), jar)
f = open("call-graph.txt", "w")
subprocess.call(["java", "-jar", "javacg-0.1-SNAPSHOT-static.jar", jar_path], stdout=f)

def main():
    functions = []
    caller_functions = []
    callee = ""
    caller = ""
    global caller_callee_dic
    global jar
    with open('call-graph.txt','r') as fp:
    # with open('cg2.txt','r') as fp:
        caller_callee_dic = collections.defaultdict(list)
        for line in fp:
            array_line = line.strip().split(' ')
            if(check_text(array_line[0])):         
                full_caller_name = array_line[0][2::]
                caller_functions.append(full_caller_name)

                callee = array_line[1][3::] 
                caller = array_line[0][2::]       
                
                # append the callee function to the functions list               
                functions.append(callee)
                caller_callee_dic[caller].append(callee)
        f.close()
    # perform caller function expantion
    for func in caller_functions:
        for key, value in caller_callee_dic.items(): 
            if func in value:
                # value.remove(func)
                value = value + caller_callee_dic[func]
                caller_callee_dic[key] = list(set(value))

    # eleminate duplicates in caller callee dictionary
    for key, value in caller_callee_dic.items():
        caller_callee_dic[key] = list(set(value))
    caller_callee_dic = OrderedDict(sorted(caller_callee_dic.items()))
    
    # output the coverage
    method_coverage()

# clean the caller functions
def check_text(text):
    test_method = text.split(":")
    if(text[0] == 'M' and re.search('test', test_method[len(test_method) - 1])):
        return True
    else: 
        return False
                             
# print method coverage
def method_coverage():
    file1 = open(r"../data/" + project + "-coverage.txt","w")
    for key, value in caller_callee_dic.items():
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
                                          
if __name__ == "__main__":
    main()
