#!/usr/bin/env python
"""
Mapper to help partition our model file based
on the conditional probability in Spam & Ham
Since the class prior probabilities will be highest,
and we don't care about them for this task,
we'll omit them from the mapper output.
INPUT:
    word \t hamCount,spamCount,pHam,pSpam
OUTPUT:
    word \t hamCount,spamCount,pHam,pSpam \t maxClass \t maxClassProbabilty
"""
import sys
for line in sys.stdin:
    word, payload = line.split()
    ham_cProb, spam_cProb = payload.strip().split(',')[2:]
    
    if word != "ClassPriors":
    
        if float(ham_cProb) >= float(spam_cProb):
            maxClass, maxClassP = 'ham', ham_cProb
        else:
            maxClass, maxClassP = 'spam', spam_cProb
        print(f"{word}\t{payload}\t{maxClass}\t{maxClassP}")