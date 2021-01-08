#!/bin/bash
# pWordCount.sh
# Author: James G. Shanahan
# Usage: pWordCount.sh m testFile.txt mapper.py [reducer.py]
# Input:
#   m = number of processes (maps), e.g., 4
#   inputFile = a text input file
#   mapper = an executable that reads from STDIN and prints to STDOUT
#   reducer = (optional) an executable that reads from STDIN and prints 
#             to STDOUT, if no reducer is provided, the framework will
#             simply stream the mapper output.
#
# Instructions:
#    For Q7b - Ammend this script in STEP 2 and STEP 3 to 
#              alphabtetically sort the contents of each chunk before
#              piping them into the reducer script and redirecting on to 
# .            $data.output.
# --------------------------------------------------------------------

usage()
{
    echo ERROR: No arguments supplied
    echo
    echo To run use
    echo "pWordCount.sh m inputFile mapper.py [reducer.py]"
    echo Input:
    echo "number of processes/maps, EG, 4"
    echo "mapper.py = an executable script to apply to each chunk in parallel"
    echo "reducer.py = an executable script after the parallel processes are complete."
    echo NOTE: if no reducer is supplied, we will simply combine the output files.
}


# print the usage message if this script is called without required args
if [ $# -lt 3 ]
  then
    usage
    exit 1
fi

# collect the arguments
m=$1
data=$2
mapper=$3


################# STEP 1: Split up the data #################
# 'wc' determines the number of lines in the data
# 'perl -pe' regex strips the piped wc output to a number
linesindata=`wc -l $data | perl -pe 's/^.*?(\d+).*?$/$1/'`

# determine the lines per chunk for the desired number of processes
linesinchunk=`echo "$linesindata/$m+1" | bc`

# split the original file into chunks by line
split -l $linesinchunk $data $data.chunk.


############## STEP 2: Process in "Parallel" #################
for datachunk in $data.chunk.*; do
    # redirect the lines of text into the user supplied executable (mapper)
    # and redirect STDOUT to a temporary file on disk
    
    
    ################ YOUR CODE HERE #############
    # Modify the line from pWordCount_v1.sh, so that  
    # each chunk is individually sorted. 

    
    ################# (END YOUR CODE)###########
    
done
# wait for the mappers to finish their work
wait





############## STEP 3: Collect the results #################
# 'ls' makes a list of the temporary count files
# 'perl -pe' regex replaces line breaks with spaces
countfiles=`\ls $data.chunk.*.counts | perl -pe 's/\n/ /'`

# If no 'reducer' executable was provided ...
if [ $# -eq 3 ]
  then
    # combine all the count files into one
    cat $countfiles > $data.output
fi

# Otherwise...
if [ $# -eq 4 ]
  then
    reducer=$4
    ################ YOUR CODE HERE #############
    # write one line to merge the individual chunks,
    # pipe to the reducer script, and redirect to 
    # output file
    


    ################# (END YOUR CODE)###########
fi


############## STEP 4: Final Output #################
# clean up the data chunks and temporary count files
\rm $data.chunk.*
# display the content of the output file:
cat $data.output

exit
