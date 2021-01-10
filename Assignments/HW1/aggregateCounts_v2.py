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
for line in sys.stdin:
    # extract words & counts
    word, count  = line.split()
    print("{}\t{}".format(word,count))
    # tally counts
    #counts[word] += int(count)
# print counts
#for wrd, count in counts.items():
    #print("{}\t{}".format(wrd,count))






# ############### (END) YOUR CODE #################

# # For reference only
# from collections import defaultdict

# ########### PROVIDED IMPLEMENTATION ##############  

# counts = defaultdict(int)
# # stream over lines from Standard Input
# for line in sys.stdin:
#     # extract words & counts
#     word, count  = line.split()
#     # tally counts
#     counts[word] += int(count)
# # print counts
# for wrd, count in counts.items():
#     print("{}\t{}".format(wrd,count))
    
# ########## (END) PROVIDED IMPLEMENTATION #########