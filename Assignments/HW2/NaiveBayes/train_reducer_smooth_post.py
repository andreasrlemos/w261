#!/usr/bin/env python

#train_reducer_smooth_post

# japan        1.0,  0.0,  0.3333333333333333,  0.0
# macao        0.0,  1.0,  0.0,                 0.125
# ClassPriors  1.0,  3.0,  0.25,                0.75
# !TotalTerms  2.0,  2.0,  1.0,                 1.0
# shanghai     0.0,  1.0,  0.0,                 0.125
# tokyo        1.0,  0.0,  0.3333333333333333,  0.0
# ClassPriors  1.0,  3.0,  0.25,                0.75
# !TotalTerms  2.0,  2.0,  1.0,                 1.0
# beijing      0.0,  1.0,  0.0,                 0.125
# chinese      1.0,  5.0,  0.3333333333333333,  0.625
# ClassPriors  1.0,  3.0,  0.25,                0.75
# !TotalTerms  2.0,  2.0,  1.0,                 1.0

import os
import sys                                                  
import numpy as np  

#################### YOUR CODE HERE ###################

# initialize trackers
cur_word = None
totalTerms = 0
totalWords, totalWordsClass0, totalWordsClass1 = 0, 0, 0
value0, value1, value2, value3 = 0, 0, 0, 0

# read input key-value pairs from standard input
for line in sys.stdin:
    
#    print(line)
    line.rstrip('\n')
    word, value = line.split('\t',1)
#     word, value = line.split('\t')
    value_tuple = tuple(value.split (","))
#    print(word)
#     print(value)
    valueTemp0 = float(value_tuple[0])
    valueTemp1 = float(value_tuple[1])
    valueTemp2 = float(value_tuple[2])
    valueTemp3 = float(value_tuple[3])
    
    # tally counts from current key
    if word == cur_word:     
        value0 += valueTemp0
        value1 += valueTemp1
        value2 += valueTemp2
        value3 += valueTemp3
    else:
        # get totals
        if cur_word == "!TotalTerms":
            totalTerms = value0
            totalWordsClass0 = value2
            totalWordsClass1 = value3
#            print(totalTerms, totalWordsClass0, totalWordsClass1)
        if cur_word == "ClassPriors":
            value0 = pre_value0
            value1 = pre_value1
            value2 = pre_value2
            value3 = pre_value3
            totalWords = value0 + value1
#            totalWordsClass0 = value0
#            totalWordsClass1 = value1
            print(f'{cur_word}\t{float(value0)},{float(value1)},\
                 {float(value0/totalWords)},{float(value1/totalWords)}')        
        if (cur_word and cur_word != "!TotalTerms" and cur_word != "ClassPriors"):
#            print(totalTerms, totalWords, totalWordsClass0, totalWordsClass1)
            print(f'{cur_word}\t{float(value0)}, {float(value1)}, \
                 {float((value0+1)/(totalWordsClass0+totalTerms))}, {float((value1+1)/(totalWordsClass1+totalTerms))}') 
        cur_word, value0, value1, value2, value3 = \
           word, float(value_tuple[0]), float(value_tuple[1]), float(value_tuple[2]), float(value_tuple[3])
    pre_value0 = valueTemp0
    pre_value1 = valueTemp1
    pre_value2 = valueTemp2
    pre_value3 = valueTemp3
#    print("Current: ", cur_word)

#print(totalTerms, totalWords, totalWordsClass0, totalWordsClass1)
print(f'{cur_word}\t{float(value0)}, {float(value1)}, \
     {float((value0+1)/(totalWordsClass0+totalTerms))}, {float((value1+1)/(totalWordsClass1+totalTerms))}') 
# print(f'ClassPriors\t{float(totalDocsClass0)}, {float(totalDocsClass1)}, \
#      {float(totalDocsClass0/totalDocs)}, {float(totalDocsClass1/totalDocs)}')
# print(f'!TotalTerms\t{float(totalTerms)}, {float(totalTerms)}, \
#      {float(1)}, {float(1)}')































#################### (END) YOUR CODE ###################