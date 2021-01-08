#!/usr/bin/env python
"""
This script reads word counts from STDIN and aggregates
the counts for any duplicated words.

INPUT & OUTPUT FORMAT:
    word \t count
USAGE (standalone):
    python aggregateCounts_v1.py < yourCountsFile.txt

Instructions:
    For Q6 - Use the provided code as is. 

"""

# imports
import sys
from collections import defaultdict

########### PROVIDED IMPLEMENTATION ##############  

counts = defaultdict(int)
# stream over lines from Standard Input
for line in sys.stdin:
    # extract words & counts
    word, count  = line.split()
    # tally counts
    counts[word] += int(count)
# print counts
for wrd, count in counts.items():
    print("{}\t{}".format(wrd,count))
    
########## (END) PROVIDED IMPLEMENTATION #########
