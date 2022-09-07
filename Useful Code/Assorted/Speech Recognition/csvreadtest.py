# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 23:24:31 2021

@author: Bigbo
"""
import numpy as np
import csv


fname = 'commands.csv'
# data = np.loadtxt(fname, delimiter=',', comments='#',usecols=(0,1,2),skiprows=1)
datafile = open(fname, 'r')
myreader = csv.reader(datafile)

identifiers=[]
functions=[]
arguments=[]
for row in myreader:
    identifiers.append(row[0].split(','))
    functions.append(row[1])
    arguments.append(row[2])
    
identifiers=identifiers[1:len(identifiers)]
functions=functions[1:len(functions)]
arguments=arguments[1:len(arguments)]

print(identifiers,functions,arguments)


def hello1(string):
    print(string)
    
def hello2(string,string2):
    print(string,string2)
    
def stringeval(strfn,strargs):
    argsstring=''
    for i in range(len(strargs)):
        if i>0:
            argsstring+=","
        argsstring+="\'"+strargs[i]+"\'"
    funeval=strfn+"("+argsstring+")"
    print(funeval)
    eval(funeval)
    
printstring='\'hello there\''
fnname='hello1'
funeval=fnname+"("+printstring+")"
print(funeval)

eval(fnname+"("+printstring+")")

print(stringeval("hello2",["hi there","hello fdwa"]))


def hotkeys(*arg):
    print(arg)
    hotkeys2(*arg)
    
def hotkeys2(*arg):
    print(arg)
    
    
hotkeys("a","b","c")
    
    
    