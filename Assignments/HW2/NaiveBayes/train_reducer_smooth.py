#!/usr/bin/env python

import os
import sys                                                  
import numpy as np  

#################### YOUR CODE HERE ###################

# initialize trackers
cur_word = None
countClass0, countClass1 = 0, 0
value0, value1 = 0, 0
totalWords, totalWordsClass0, totalWordsClass1 = 0, 0, 0
totalDocs, totalDocsClass0, totalDocsClass0 = 0, 0, 0
totalTerms = 1   # >>> New element to handle Smoothing <<<
totalClass0, totalClass1 = 0, 0

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
            totalTerms += 1
            totalClass0 += value0
            totalClass1 += value1
        cur_word, value0, value1 = word, int(value_tuple[0]), int(value_tuple[1])

totalClass0 += value0
totalClass1 += value1
print(f'{cur_word}\t{float(value0)}, {float(value1)}, \
     {float(value0/totalWordsClass0)}, {float(value1/totalWordsClass1)}')
print(f'ClassPriors\t{float(totalDocsClass0)}, {float(totalDocsClass1)}, \
     {float(totalDocsClass0/totalDocs)}, {float(totalDocsClass1/totalDocs)}')
print(f'!TotalTerms\t{float(totalTerms)}, {float(totalTerms)}, \
     {float(totalClass0)}, {float(totalClass1)}')































#################### (END) YOUR CODE ###################