#!/usr/bin/env python
"""
Reducer to calculate precision and recall as part
of the inference phase of Naive Bayes.
INPUT:
    ID \t true_class \t P(ham|doc) \t P(spam|doc) \t predicted_class
OUTPUT:
    precision \t ##
    recall \t ##
    accuracy \t ##
    F-score \t ##
         
Instructions:
    Complete the missing code to compute these^ four
    evaluation measures for our classification task.
    
    Note: if you have no True Positives you will not 
    be able to compute the F1 score (and maybe not 
    precision/recall). Your code should handle this 
    case appropriately feel free to interpret the 
    "output format" above as a rough suggestion. It
    may be helpful to also print the counts for true
    positives, false positives, etc.
"""
import sys

# initialize counters
FP = 0.0 # false positives
FN = 0.0 # false negatives
TP = 0.0 # true positives
TN = 0.0 # true negatives

precision = 0
recall = 0
accuracy = 0
f_score = 0

# read from STDIN
for line in sys.stdin:
    # parse input
    docID, class_, pHam, pSpam, pred = line.split()
    # emit classification results first
#    print(line[:-2], class_ == pred)
    
    # then compute evaluation stats
#################### YOUR CODE HERE ###################
#    print(class_, pred)
    class_ = float(class_)
    pred = float(pred)
#    print(class_, pred)
    
    if (class_ == 1 and pred == 1):
        TP += 1
    if (class_ == 1 and pred == 0):
        FN += 1
    if (class_ == 0 and pred == 1):
        FP += 1
    if (class_ == 0 and pred == 0):
        TN += 1

print(f"True Positives\t{TP}")
print(f"True Negatives\t{TN}")
print(f"False Positives\t{FP}")
print(f"False Negatives\t{FN}")

if (TP+FP) > 0:
    precision = TP / (TP+FP)
else:
    precision = 'N/A'

if (TP+FN) > 0:
    recall = TP / (TP+FN)
else:
    recall = 'N/A'

accuracy = (TP+TN) / (TP+TN+FP+FN)

if TP > 0:
    f_score = (2*precision*recall) / (precision + recall)
else:
    f_score = 'N/A'

print(f"Precision\t{precision}")
print(f"Recall\t{recall}")
print(f"Accuracy\t{accuracy}")
print(f"F-score\t{f_score}")


#     precision \t ## Precision = TruePositives / (TruePositives + FalsePositives)
#     recall \t ## Recall = TruePositives / (TruePositives + FalseNegatives)
#     accuracy \t ## Accuracy = (TruePositives + TrueNegatives) / (TP + TN + FP + FN)
#     F-score \t ## F-Measure = (2 * Precision * Recall) / (Precision + Recall)



















#################### (END) YOUR CODE ###################
    