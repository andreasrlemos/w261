#!/usr/bin/env python
"""
This script reads word counts from STDIN and aggregates
the counts for any duplicated words.

INPUT & OUTPUT FORMAT:
    word \t count
USAGE (standalone):
    python aggregateCounts_v2.py < yourCountsFile.txt

Instructions:
    For Q7 - Your solution should not use a dictionary or store anything   
             other than a single total count - just print them as soon as  
             you've added them. HINT: you've modified the framework script 
             to ensure that the input is alphabetized; how can you 
             use that to your advantage?
"""

# imports
import sys


################# YOUR CODE HERE #################

lastword = ""
lastcount = 0
iteration = 1
linecount = 0

for line in sys.stdin:
    word, count  = line.split()
    
    if (iteration == 1):
        lastword = word
        iteration += 1

    if (lastword != word):
        print("{}\t{}".format(lastword,lastcount))
        lastword = word
        lastcount = int(count)
        iteration += 1

    else:
        lastcount = lastcount + int(count)
        lastword = word
        iteration += 1

print("{}\t{}".format(lastword,lastcount))
        
############### (END) YOUR CODE #################

