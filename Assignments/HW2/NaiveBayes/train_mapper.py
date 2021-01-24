#!/usr/bin/env python
"""
Mapper reads in text documents and emits word counts by class.
INPUT:                                                    
    DocID \t true_class \t subject \t body                
OUTPUT:                                                   
    partitionKey \t word \t class0_partialCount,class1_partialCount       
    

Instructions:
    You know what this script should do, go for it!
    (As a favor to the graders, please comment your code clearly!)
    
    A few reminders:
    1) To make sure your results match ours please be sure
       to use the same tokenizing that we have provided in
       all the other jobs:
         words = re.findall(r'[a-z]+', text-to-tokenize.lower())
         
    2) Don't forget to handle the various "totals" that you need
       for your conditional probabilities and class priors.
       
Partitioning:
    In order to send the totals to each reducer, we need to implement
    a custom partitioning strategy.
    
    We will generate a list of keys based on the number of reduce tasks 
    that we read in from the environment configuration of our job.
    
    We'll prepend the partition key by hashing the word and selecting the
    appropriate key from our list. This will end up partitioning our data
    as if we'd used the word as the partition key - that's how it worked
    for the single reducer implementation. This is not necessarily "good",
    as our data could be very skewed. However, in practice, for this
    exercise it works well. The next step would be to generate a file of
    partition split points based on the distribution as we've seen in 
    previous exercises.
    
    Now that we have a list of partition keys, we can send the totals to 
    each reducer by prepending each of the keys to each total.
       
"""

import re                                                   
import sys                                                  
import numpy as np      

from operator import itemgetter
import os

#################### YOUR CODE HERE ###################

def getPartitionKey(word):
    """ 
    Helper function to assign partition key ('A', 'B', or 'C').
    Args:  word (str) 
    """
    # Set thresholds for partitions based on first letter in Word
    if word[0] < 'h': 
        return  'A'
    elif word[0] < 'p':
        return  'B'
    else:
        return 'C'

# initialize trackers
current_word = None
class0_partialCount, class1_partialCount = 0, 0
totalWordsClass0, totalWordsClass1 = 0, 0
countDocClass0, countDocClass1 = 0, 0

# read from standard input
for line in sys.stdin:
    
    # parse input and tokenize
    docID, _class, subject, body = line.lower().split('\t')
    words = re.findall(r'[a-z]+', subject + ' ' + body)
    if int(_class) == 0:
        countDocClass0 += 1
    else:
        countDocClass1 += 1
    # emit words and count of 1 plus total counter
    for word in words:
        class0_partialCount, class1_partialCount = 0, 0
        partitionKey = getPartitionKey(word)
        
        if int(_class) == 0:
            class0_partialCount = 1
            totalWordsClass0 += 1

        else:
            class1_partialCount = 1
            totalWordsClass1 += 1

        print(f"{partitionKey}\t{word}\t{class0_partialCount},{class1_partialCount}")


# emit total count to each partition (note this is a partial total)
for pkey in ['A','B','C']: 
        print(f'{pkey}\t!totalWordCount\t{totalWordsClass0},{totalWordsClass1}')     
        print(f'{pkey}\t!totalDocClassCount\t{countDocClass0},{countDocClass1}')


#################### (END) YOUR CODE ###################