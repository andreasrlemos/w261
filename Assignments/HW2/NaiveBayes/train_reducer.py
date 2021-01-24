#!/usr/bin/env python
"""
Reducer aggregates word counts by class and emits frequencies.

INPUT:
    partitionKey \t word \t class0_partialCount,class1_partialCount 
OUTPUT:
    ID \t word \t class0_count,class1count,P(word|class0),P(word|class1)
    
Instructions:
    Again, you are free to design a solution however you see 
    fit as long as your final model meets our required format
    for the inference job we designed in Question 8. Please
    comment your code clearly and concisely.
    
    A few reminders: 
    1) Don't forget to emit Class Priors (with the right key).
    2) In python2: 3/4 = 0 and 3/float(4) = 0.75
"""
##################### YOUR CODE HERE ####################

import re                                                   
import sys                                                  
import numpy as np      

from operator import itemgetter
import os

# initialize trackers
cur_word = None
countClass0, countClass1 = 0, 0
value0, value1 = 0, 0
totalWords, totalWordsClass0, totalWordsClass1 = 0, 0, 0
totalDocs, totalDocsClass0, totalDocsClass0 = 0, 0, 0

# read input key-value pairs from standard input
for line in sys.stdin:
    
    line.rstrip('\n')
    pKey, word, value = line.split('\t',2)
    value_tuple = tuple(value.split (","))
    valueTemp0 = int(value_tuple[0])
    valueTemp1 = int(value_tuple[1])

    # tally counts from current key
    if word == cur_word:     
        value0 += valueTemp0
        value1 += valueTemp1
    else:
        # get totals
        if cur_word == "!totalWordCount":
            totalWords = value0 + value1
            totalWordsClass0 = value0
            totalWordsClass1 = value1
        if cur_word == "!totalDocClassCount":
            totalDocs = value0 + value1
            totalDocsClass0 = value0
            totalDocsClass1 = value1
        if (cur_word and cur_word != "!totalWordCount" and cur_word != "!totalDocClassCount"):
            print(f'{cur_word}\t{float(value0)}, {float(value1)}, \
                 {float(value0/totalWordsClass0)}, {float(value1/totalWordsClass1)}')
        cur_word, value0, value1 = word, int(value_tuple[0]), int(value_tuple[1])

print(f'{cur_word}\t{float(value0)}, {float(value1)}, \
     {float(value0/totalWordsClass0)}, {float(value1/totalWordsClass1)}')
print(f'ClassPriors\t{float(totalDocsClass0)}, {float(totalDocsClass1)}, \
     {float(totalDocsClass0/totalDocs)}, {float(totalDocsClass1/totalDocs)}')



##################### (END) CODE HERE ####################