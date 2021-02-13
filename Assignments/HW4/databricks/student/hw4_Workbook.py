# Databricks notebook source
# MAGIC %md # HW 4 - Supervised Learning at Scale.
# MAGIC __`MIDS w261: Machine Learning at Scale | UC Berkeley School of Information | Fall 2018`__
# MAGIC 
# MAGIC In the first three homeworks you became familiar with the Map-Reduce programming paradigm as manifested in the Hadoop Streaming and Spark frameworks. We explored how different data structures and design patterns can help us manage the computational complexity of an algorithm. As part of this process you implemented both a supervised learning alogorithm (Naive Bayes) and an unsupervised learning algorithm (synonym detection via cosine similarity). In both of these tasks parallelization helped us manage calculations involving a large number of features. However a large feature space isn't the only situation that might prompt us to want to parallelize a machine learning algorithm. In the final two assignments we'll look at cases where the iterative nature of an algorithm is the main driver of its computational complexity (and the reason we might want to parallelize it).
# MAGIC 
# MAGIC In this week's assignment we'll perform 3 kinds of linear regression: OLS, Ridge and Lasso. As in previous assignments you will implement the core calculations using Spark RDDs... though we've provided more of a code base than before since the focus of the latter half of the course is more on general machine learning concepts. By the end of this homework you should be able to:  
# MAGIC * ... __define__ the loss functions for OLS, Ridge and Lasso regression.
# MAGIC * ... __calculate__ the gradient for each of these loss functions.
# MAGIC * ... __identify__ which parts of the gradient descent algorithm can be parallelized.
# MAGIC * ... __implement__ parallelized gradient descent with cross-validation and regularization.
# MAGIC * ... __compare/contrast__ how L1 and L2 regularization impact model parameters & performance.
# MAGIC 
# MAGIC Additional Reference: [Spark 3.0.0 Documentation - RDD programming guide](https://spark.apache.org/docs/3.0.0/rdd-programming-guide.html)
# MAGIC 
# MAGIC __Please refer to the `README` for homework submission instructions and additional resources.__ 

# COMMAND ----------

# MAGIC %md ### Notebook Set-Up
# MAGIC Before starting your homework run the following cells to confirm your setup.

# COMMAND ----------

# imports
import re
import time
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ast
import os

# COMMAND ----------

# MAGIC %md ### Run the next cell to create your directory in dbfs
# MAGIC You do not need to understand this scala snippet. It simply dynamically fetches your user directory name so that any files you write can be saved in your own directory.

# COMMAND ----------

# RUN THIS CELL AS IS
# This code snippet reads the user directory name, and stores is in a python variable.
# Next, it creates a folder inside your home folder, which you will use for files which you save inside this notebook.
username = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('user')
userhome = 'dbfs:/user/' + username
print(userhome)
hw4_path = userhome + "/HW4/" 
hw4_path_open = '/dbfs' + hw4_path.split(':')[-1] # for use with python open()
dbutils.fs.mkdirs(hw4_path)

# COMMAND ----------

# RUN THIS CELL AS IS. You should see 348625. If you do not see this, please let an Instructor or TA know.
total = 0
DATA_PATH = 'dbfs:/mnt/mids-w261/HW4/'
for item in dbutils.fs.ls(DATA_PATH):
  total = total+item.size
total



# COMMAND ----------

# RUN THIS CELL AS IS - A test to make sure your directory is working as expected.
# You should see a result like:
# dbfs:/user/youremail@ischool.berkeley.edu/hw4/sample_docs.txt
dbutils.fs.put(hw4_path+'test.txt',"hello world",True)
display(dbutils.fs.ls(hw4_path))


# COMMAND ----------

sc = spark.sparkContext
spark

# COMMAND ----------

# MAGIC %md # Question 1: Opimization Theory 
# MAGIC 
# MAGIC As you know from w207, Gradient Descent is an iterative process that seeks to find the optimal parameters for a model given a particular training data set. It does this by using the vector of partial derivatives of a loss function to strategically update parameters in a way that will reduce the loss. In live session 6 you discussed some of the theory behnid why gradient descent works and looked at a small example of gradient descent in the context of linear regression.
# MAGIC 
# MAGIC ### Q1 Tasks:
# MAGIC 
# MAGIC * __a) short response:__ What are the first and second order conditions for convexity and why do we care about them when performing Gradient Descent?
# MAGIC 
# MAGIC * __b) short response:__ Explain the relationship between problem domain space and model parameter space in the context of Gradient Descent. In practice, why can't we find the optimal model by simply looking at the error surface in model parameter space?
# MAGIC 
# MAGIC * __c) short response:__ In the context of Gradient Descent, what is the 'learning rate' and what are the tradeoffs associated with setting this hyperparameter?
# MAGIC 
# MAGIC * __d) BONUS:__ In the context of OLS, what do we mean by a 'closed form solution' and why is it not scalable?

# COMMAND ----------

# MAGIC %md ### Q1 Student Answers:
# MAGIC > __a)__ Type your answer here!
# MAGIC 
# MAGIC > __b)__ Type your answer here!
# MAGIC 
# MAGIC > __c)__ Type your answer here!  
# MAGIC 
# MAGIC > __d)__ Type your (optional bonus) answer here!  

# COMMAND ----------

# MAGIC %md # About the Data
# MAGIC 
# MAGIC For the main task in this portion of the homework you will use data about red and white Portuguese wines. [This data](http://archive.ics.uci.edu/ml/datasets/Wine+Quality) was made available to the UC Irvine public repository of Machine Learning datasets by researchers at the University of Minho in association with [this paper](https://www.sciencedirect.com/science/article/pii/S0167923609001377?via%3Dihub):
# MAGIC > P. Cortez, A. Cerdeira, F. Almeida, T. Matos and J. Reis. 
# MAGIC Modeling wine preferences by data mining from physicochemical properties. In Decision Support Systems, Elsevier, 47(4):547-553, 2009.
# MAGIC 
# MAGIC The dataset includes 12 fields:
# MAGIC >`fixed acidity`  
# MAGIC `volatile acidity`  
# MAGIC `citric acid`  
# MAGIC `residual sugar`  
# MAGIC `chlorides`  
# MAGIC `free sulfur dioxide`  
# MAGIC `total sulfur dioxide`  
# MAGIC `density`  
# MAGIC `pH`  
# MAGIC `sulphates`  
# MAGIC `alcohol`  
# MAGIC `quality`   -- (_a score between 0 and 10_)
# MAGIC 
# MAGIC __`IMPORTANT NOTE:`__ The outcome variable in our data is a human assigned score ranging from 0 to 10. Since the scores are integers this is actually an ordinal and not numerical outcome varaible. However for the purposes of this assignment we'll treat it as a numerical quantity.
# MAGIC 
# MAGIC The data are in two files: one containing red wines and another containing white wines.  Use the following cells to download the data, add a field for red/white, and split it into a test and train set.

# COMMAND ----------

headers = dbutils.fs.head(DATA_PATH + '/winequality-red.csv',200)
headers = headers.split('\n')[0]
FIELDS = ['color'] + re.sub('"', '',headers).split(';')

# COMMAND ----------

# RUN THIS CELL AS IS. You should see winequality-red.csv and winequality-white.csv. Please contact an Instructor or TA if you do not see these two files.
dbutils.fs.ls(DATA_PATH)

# COMMAND ----------

# load the raw data into an RDD - RUN THIS CELL AS IS
redsRDD = sc.textFile(DATA_PATH + '/winequality-red.csv')\
            .filter(lambda x: x != headers)\
            .map(lambda x: '1;' + x) # set first field 1 to indicate red wine
whitesRDD = sc.textFile(DATA_PATH + '/winequality-white.csv')\
              .filter(lambda x: x != headers)\
              .map(lambda x: '0;' + x) # set first field 0 to indicate white wine

# COMMAND ----------

redsRDD.take(5)

# COMMAND ----------

whitesRDD.take(5)

# COMMAND ----------

# Generate 80/20 (pseudo)random train/test split - RUN THIS CELL AS IS
trainRDD, heldOutRDD = redsRDD.union(whitesRDD).randomSplit([0.8,0.2], seed = 1)
print(f"... held out {heldOutRDD.count()} records for evaluation and assigned {trainRDD.count()} for training.")

# COMMAND ----------

# helper function - RUN THIS CELL AS IS
def parse(line):
    """
    Map record_csv_string --> (tuple,of,fields)
    """
    fields = np.array(line.split(';'), dtype = 'float')
    features,quality = fields[:-1], fields[-1]
    return(features, quality)

# COMMAND ----------

# cache the training set - RUN THIS CELL AS IS 
trainRDDCached = trainRDD.map(parse).cache()

# COMMAND ----------

# MAGIC %md # Question 2: EDA
# MAGIC 
# MAGIC A statistician's approach to Linear Regression typically involves a series of EDA steps to examine each feature in the data and then a series of steps to test assumptions about their potential contribution to a multi-feature linear model. In particular, we'd want to look for a set of features that exhibit a likely linear relationship with the outcome variable and that are _not_ highy correlated with each other. In the context of machine learning, these considerations remain important techniques for improving model generalizability despite the common practice to use model evaluation techniques (and large data sets) to get the final word on feature selection. 
# MAGIC 
# MAGIC In this question we'll briefly look at the features in our data set. To mimic an 'at scale' analysis we'll start by sampling from our Spark RDD training set so that we have a manageable amount of data to work with in our visuals.
# MAGIC 
# MAGIC ### Q2 Tasks:
# MAGIC * __a) short response:__ Run the provided code to sample 1000 points and visualize histograms of each feature. Comment on the distributions you observe (eg. _Which features appear normaly distributed, which don't? Which features vary most/least?_) How is the varaible `color` different than the other features & what does that mean about how we interpret its regression coefficient?
# MAGIC 
# MAGIC * __b) short response:__ Run the provided code to create boxplots of each feature. Which, if any, appear to have a positive linear relationship with `quality`? Which if any appear to have a negative linear relationship with `quality`?
# MAGIC 
# MAGIC 
# MAGIC * __c) short response:__ Run the provided code to plot the correlations matrix. Which pairs of features are most _strongly_ (postively or negatively) associated with each other? What implications would that have for our feature selection?

# COMMAND ----------

# MAGIC %md ### Q2 Student Answers:
# MAGIC > __a)__ Type your answer here!  
# MAGIC 
# MAGIC > __b)__ Type your answer here!  
# MAGIC 
# MAGIC > __c)__ Type your answer here!  

# COMMAND ----------

# part a - take a 1000 point sample for EDA (RUN THIS CELL AS IS)
sample = np.array(trainRDDCached.map(lambda x: np.append(x[0], [x[1]]))
                                .takeSample(False, 1000))
sample_df = pd.DataFrame(np.array(sample), columns = FIELDS)

# COMMAND ----------

# part a - take a look at histograms for each feature (RUN THIS CELL AS IS)
sample_df[FIELDS[:-1]].hist(figsize=(15,15), bins=15)
display(plt.show())

# COMMAND ----------

# part b -  plot boxplots of each feature vs. the outcome (RUN THIS CELL AS IS)
fig, ax_grid = plt.subplots(4, 3, figsize=(15,15))
y = sample_df['quality']
for idx, feature in enumerate(FIELDS[:-1]):
    x = sample_df[feature]
    sns.boxplot(x, y, ax=ax_grid[idx//3][idx%3], orient='h', linewidth=.5)
    ax_grid[idx//3][idx%3].invert_yaxis()
fig.suptitle("Individual Features vs. Outcome (qualilty)", fontsize=15, y=0.9)
display(plt.show())

# COMMAND ----------

# plot heatmap for correlations matrix - RUN THIS CELL AS IS
corr = sample_df[FIELDS[:-1]].corr()
fig, ax = plt.subplots(figsize=(11, 9))
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True
cmap = sns.diverging_palette(240, 10, as_cmap=True)
sns.heatmap(corr, mask=mask, cmap=cmap, center=0, linewidths=.5)
plt.title("Correlations between features.")
display(plt.show())

# COMMAND ----------

# MAGIC %md # Question 3: OLS Loss
# MAGIC 
# MAGIC For a parametric model, the key factor that will impact how easy it is to optimize is your choice of how to define the loss function. In Ordinary Least Squares (OLS) Regression our loss function is just about as convenient as you will get: not only is it convex, its also very easy to interpret. 
# MAGIC 
# MAGIC When doing supervised learning, a simple sanity check consists of comparing one’s estimator against simple rules of thumb. It is useful as a simple baseline to compare with other (real) regressors. Examples of regression baselines include:
# MAGIC * "mean": always predicts the mean of the training set
# MAGIC * "median": always predicts the median of the training set
# MAGIC * "quantile": always predicts a specified quantile of the training set,provided with the quantile parameter.
# MAGIC * "constant": always predicts a constant value that is provided by the user.
# MAGIC 
# MAGIC In this question you'll "choose" a baseline model and then write a function to compute the loss of a linear model in Spark. You'll reuse this function in Q4 when you implement gradient descent.
# MAGIC 
# MAGIC #### Baseline example illustrated:

# COMMAND ----------

# points from our mini example from the demo 6 notebook
points = np.array([[1,2],[3,4],[5,5],[4,3],[2,3]])
x = points[:,0]
y = points[:,1]

plt.figure()
plt.plot(x, y,'o', label='data points')
plt.axhline(np.mean(y),c='r', label='"mean" model')
plt.title('Example of "mean" baseline model')
plt.ylabel("y")
plt.xlabel("x")
plt.legend()
display(plt.show())

# COMMAND ----------

# MAGIC %md ### Q3 Tasks:
# MAGIC * __a) code:__ Fill in the code below to compute the mean and variance of your outcome variable. [__`HINT:`__ _use `trainRDDCached` as the input & feel free to use Spark built-in functions._]
# MAGIC 
# MAGIC 
# MAGIC * __b) short response:__ Write the formula for the OLS loss function and explain how to interpret it graphically.
# MAGIC 
# MAGIC 
# MAGIC * __c) short response:__ In the context of linear models & vector computations what does it mean to 'augment' a data point and why do we do this?
# MAGIC 
# MAGIC 
# MAGIC * __d) code + short response:__ Fill in the missing code to complete the`OLSLoss` function. Is computing the loss "embarassingly parallel'? Explain. [__`TIP:`__ Use `augmentedData` as your input when computing the loss.]
# MAGIC 
# MAGIC * __e) code + short response:__ Fill in the missing code to define a baseline model for this data set that has a bias term equal to the mean of your outcome variable and `0.0` for all coefficients. Note that in the docstring for `OLSLoss` we specified that the model should be a numpy array with the bias in the first position. Once you've defined your model, run the provided cells to check that your model has the correct dimensions and then compute the loss for your baseline model. Compare your results to the result you got in `part a` and explain what you see.

# COMMAND ----------

# MAGIC %md ### Q3 Student Answers:
# MAGIC > __b)__ Type your answer here!  
# MAGIC 
# MAGIC > __c)__ Type your answer here!  
# MAGIC 
# MAGIC > __d)__ Type your answer here!  
# MAGIC 
# MAGIC > __e)__ Type your answer here!  

# COMMAND ----------

# part a - mean and variance of the outcome variable 
meanQuality = None # FILL IN YOUR CODE HERE
varQuality = None # FILL IN YOUR CODE HERE
print(f"Mean: {meanQuality}")
print(f"Variance: {varQuality}")

# COMMAND ----------

# part d - write function to compute loss (FILL IN MISSING CODE BELOW)
def OLSLoss(dataRDD, W):
    """
    Compute mean squared error.
    Args:
        dataRDD - each record is a tuple of (features_array, y)
        W       - (array) model coefficients with bias at index 0
    """
    augmentedData = dataRDD.map(lambda x: (np.append([1.0], x[0]), x[1]))
    ################## YOUR CODE HERE ##################
    loss = None
    ################## (END) YOUR CODE ##################
    return loss

# COMMAND ----------

# part e - define your baseline model here
BASELINE = None

# COMMAND ----------

# part e - compute the loss for your baseline model (RUN THIS CELL AS IS)
assert len(BASELINE) == len(trainRDDCached.take(1)[0][0]) + 1, "Double check model dimensions"
print(f"Baseline model loss: {OLSLoss(trainRDDCached, BASELINE)}")

# COMMAND ----------

# MAGIC %md # Question 4: Vanilla Gradient Descent
# MAGIC 
# MAGIC Performing Gradient Descent technically only requires two steps: 1) _use the current model to calculate the gradient_; 2) _use the gradient to update the current model parameters_. In practice though, we'll want to add a third step which is to compute the loss for our new model so that we can see if its working. In this question you'll implement gradient descent for OLS regression and take a look at a few update steps.
# MAGIC 
# MAGIC ### Q4 Tasks:
# MAGIC * __a) short response:__ Jimi describes the main part of the gradient calculation for OLS Regression using a short mantra: _'the mean of the data weighted by the errors'_. . Write the formula for the gradient and explain how it reflects this phrase. 
# MAGIC 
# MAGIC * __b) short response:__ Looking at the formula you wrote in `part a`, what parts of this calculation can be parallelized and what has to happen after reducing?
# MAGIC 
# MAGIC 
# MAGIC * __c) code:__ Fill in the missing lines in `GDUpdate` to compute the gradient and perform a single update of the model parameters.   
# MAGIC     * __`TIP 1:`__ _remember that the gradient is a vector of partial derivatives, `grad` should be a numpy array_    
# MAGIC     * __`TIP 2:`__ _Spark's built in `mean()` function may help you here_  
# MAGIC 
# MAGIC 
# MAGIC * __d) short response:__ Run the provided code to perform 5 steps of Gradient Descent on our data. What is wrong with these results?
# MAGIC 
# MAGIC 
# MAGIC * __e) code + short response:__ Fill in the missing code in `normalize` so that this function scales each feature and centers it at 0. Then use the provide code block to rerun your same gradient descent code on the scaled data. Use these results to explain what the problem was in 'd'.
# MAGIC     * __`TIP:`__ _You may find [this brief illustration](https://www.coursera.org/lecture/machine-learning/gradient-descent-in-practice-i-feature-scaling-xx3Da) from Andrew Ng's Coursera helpful._

# COMMAND ----------

# MAGIC %md ### Q4 Student Answers:
# MAGIC > __a)__ Type your answer here!  
# MAGIC 
# MAGIC > __b)__ Type your answer here! 
# MAGIC 
# MAGIC > __c)__ _complete the coding portions of this question before answering d & e_ 
# MAGIC 
# MAGIC > __d)__ Type your answer here!  
# MAGIC 
# MAGIC > __e)__ Type your answer here!  

# COMMAND ----------

# part b - function to perform a single GD step
def GDUpdate(dataRDD, W, learningRate = 0.1):
    """
    Perform one OLS gradient descent step/update.
    Args:
        dataRDD - records are tuples of (features_array, y)
        W       - (array) model coefficients with bias at index 0
    Returns:
        new_model - (array) updated coefficients, bias at index 0
    """
    # add a bias 'feature' of 1 at index 0
    augmentedData = dataRDD.map(lambda x: (np.append([1.0], x[0]), x[1])).cache()
    
    ################## YOUR CODE HERE ################# 
    grad = None
    new_model = None
    ################## (END) YOUR CODE ################# 
   
    return new_model

# COMMAND ----------

# MAGIC %%time
# MAGIC # part c - take a look at a few Gradient Descent steps (RUN THIS CELL AS IS)
# MAGIC 
# MAGIC nSteps = 5
# MAGIC model = BASELINE
# MAGIC print(f"BASELINE:  Loss = {OLSLoss(trainRDDCached,model)}")
# MAGIC for idx in range(nSteps):
# MAGIC     print("----------")
# MAGIC     print(f"STEP: {idx+1}")
# MAGIC     model = GDUpdate(trainRDDCached, model)
# MAGIC     loss = OLSLoss(trainRDDCached, model)
# MAGIC     print(f"Loss: {loss}")
# MAGIC     print(f"Model: {[round(w,3) for w in model]}")

# COMMAND ----------

# part d - helper function to normalize the data (FILL IN THE MISSING CODE BELOW)
def normalize(dataRDD):
    """
    Scale and center data round mean of each feature.
    Args:
        dataRDD - records are tuples of (features_array, y)
    Returns:
        normedRDD - records are tuples of (features_array, y)
    """
    featureMeans = dataRDD.map(lambda x: x[0]).mean()
    featureStdev = np.sqrt(dataRDD.map(lambda x: x[0]).variance())
    
    ################ YOUR CODE HERE #############
    normedRDD = None
    ################ FILL IN YOUR CODE HERE #############
    
    return normedRDD

# COMMAND ----------

# part d - cache normalized data (RUN THIS CELL AS IS)
normedRDD = normalize(trainRDDCached).cache()

# COMMAND ----------

# MAGIC %%time
# MAGIC # part e - take a look at a few GD steps w/ normalized data  (RUN THIS CELL AS IS)
# MAGIC nSteps = 5
# MAGIC model = BASELINE
# MAGIC print(f"BASELINE:  Loss = {OLSLoss(trainRDDCached,model)}")
# MAGIC for idx in range(nSteps):
# MAGIC     print("----------")
# MAGIC     print(f"STEP: {idx+1}")
# MAGIC     model = GDUpdate(normedRDD, model)
# MAGIC     loss = OLSLoss(normedRDD, model) 
# MAGIC     print(f"Loss: {loss}")
# MAGIC     print(f"Model: {[round(w,3) for w in model]}")

# COMMAND ----------

# MAGIC %md # Question 5: Assessing the performance of your model.
# MAGIC 
# MAGIC Printing out the loss as we perform each gradient descent step allows us to confirm that our Gradient Descent code appears to be working, but this number doesn't accurately reflect "how good" our model is. In this question you'll plot error curves for a test and training set in order to discuss model performance. Note that although we split out a test & train set when we first loaded the data... in the spirit of keeping that 20% truly 'held out' until then end of the assignment, we'll make an additional split for the purposes of this question dividing the existing training set into two smaller RDDs.
# MAGIC 
# MAGIC ### Q5 Tasks:
# MAGIC * __a) short response:__ Why doesn't the loss that we printed in Question 4 accurately reflect "how good" our model is? 
# MAGIC 
# MAGIC 
# MAGIC * __b) code:__ Since we're going to be running Gradient Descent a number of times let's package it into a function for convenience. Fill in the missing code in `GradientDescent()`, note that the missing code is going to look a lot like the provided code blocks in Q5 -- feel free to use those as a starting point.
# MAGIC 
# MAGIC 
# MAGIC * __c) short response:__ Use the provided code to split the normalized data into a test and train set, then run 50 iterations of gradient descent and plot the MSE curves for each. Describe what you see and speculate about why this might be happening.
# MAGIC 
# MAGIC 
# MAGIC * __d) short response:__ Note that passing the optional parameter `seed` to the Spark method `randomSplit` allows us to pseudo randomize our test/train split in a way that is replicable. Re-run the code for part 'c but this time in the line where we perform the `normedRDD.randomSplit` change the seed to _`seed = 5`_. What changes in the plot? Repeat for _`seed = 4`_. How does this change your interpret the results you saw in 'c'. What is the more likely explanation?

# COMMAND ----------

# MAGIC %md ### Q5 Student Answers:
# MAGIC > __a)__ Type your answer here!  
# MAGIC 
# MAGIC > __c)__ Type your answer here! 
# MAGIC 
# MAGIC > __d)__ Type your answer here!  

# COMMAND ----------

# part b - OLS gradient descent function
def GradientDescent(trainRDD, testRDD, wInit, nSteps = 20, 
                    learningRate = 0.1, verbose = False):
    """
    Perform nSteps iterations of OLS gradient descent and 
    track loss on a test and train set. Return lists of
    test/train loss and the models themselves.
    """
    # initialize lists to track model performance
    train_history, test_history, model_history = [], [], []
    
    # perform n updates & compute test and train loss after each
    model = wInit
    for idx in range(nSteps): 
        
        ############## YOUR CODE HERE #############
        model = None
        training_loss = None
        test_loss = None
        ############## (END) YOUR CODE #############
        
        # keep track of test/train loss for plotting
        train_history.append(training_loss)
        test_history.append(test_loss)
        model_history.append(model)
        
        # console output if desired
        if verbose:
            print("----------")
            print(f"STEP: {idx+1}")
            print(f"training loss: {training_loss}")
            print(f"test loss: {test_loss}")
            print(f"Model: {[round(w,3) for w in model]}")
    return train_history, test_history, model_history

# COMMAND ----------

# plot error curves - RUN THIS CELL AS IS
def plotErrorCurves(trainLoss, testLoss, title = None):
    """
    Helper function for plotting.
    Args: trainLoss (list of MSE) , testLoss (list of MSE)
    """
    fig, ax = plt.subplots(1,1,figsize = (16,8))
    x = list(range(len(trainLoss)))[1:]
    ax.plot(x, trainLoss[1:], 'k--', label='Training Loss')
    ax.plot(x, testLoss[1:], 'r--', label='Test Loss')
    ax.legend(loc='upper right', fontsize='x-large')
    plt.xlabel('Number of Iterations')
    plt.ylabel('Mean Squared Error')
    if title:
        plt.title(title)
    display(plt.show())

# COMMAND ----------

# run 50 iterations (RUN THIS CELL AS IS)
wInit = BASELINE
trainRDD, testRDD = normedRDD.randomSplit([0.8,0.2], seed = 2018)
start = time.time()
MSEtrain, MSEtest, models = GradientDescent(trainRDD, testRDD, wInit, nSteps = 50)
print(f"\n... trained {len(models)} iterations in {time.time() - start} seconds")

# COMMAND ----------

# take a look (RUN THIS CELL AS IS)
plotErrorCurves(MSEtrain, MSEtest, title = 'Ordinary Least Squares Regression' )

# COMMAND ----------

# save the models & their performance for comparison later (RUN THIS CELL AS IS)
np.savetxt(hw4_path_open + 'OLSmodels.csv', np.array(models), delimiter=',')
np.savetxt(hw4_path_open + 'OLSloss.csv', np.array([MSEtrain, MSEtest]), delimiter=',')

# COMMAND ----------

# take a look (RUN THIS CELL AS IS)
dbutils.fs.put(hw4_path + 'ols_models.txt', str(models), True)
dbutils.fs.put(hw4_path + 'ols_loss.txt', str([MSEtrain, MSEtest]), True)
plotErrorCurves(MSEtrain, MSEtest, title = 'Ordinary Least Squares Regression' )

# COMMAND ----------

# run 50 iterations (RUN THIS CELL AS IS)
wInit = BASELINE
trainRDD, testRDD = normedRDD.randomSplit([0.8,0.2], seed = 4)
start = time.time()
MSEtrain, MSEtest, models = GradientDescent(trainRDD, testRDD, wInit, nSteps = 50)
print(f"\n... trained {len(models)} iterations in {time.time() - start} seconds")

# COMMAND ----------

# take a look (RUN THIS CELL AS IS)
plotErrorCurves(MSEtrain, MSEtest, title = 'Ordinary Least Squares Regression' )

# COMMAND ----------

# MAGIC %md # Question 6: Cross Validation
# MAGIC 
# MAGIC In question 5 we mentioned that computing the loss after each iteration is not strictly a part of Gradient Descent, its just convenient for visualizing our progress. This "third step" however comes with a tradeoff: it requires an extra pass through the data. Normally this would cause us to cringe except for the fact that both the loss computation and the gradient computation are very easy to parallelize - lots of the work can be done in place no shuffle needed for the aggregation. 
# MAGIC 
# MAGIC [Cross-validation](https://en.wikipedia.org/wiki/Cross-validation_(statistics)) , sometimes called rotation estimation, or out-of-sample testing, is a model validation technique for assessing how well the model will generalize to an independent data set. The goal of cross-validation is to test the model's ability to predict new data. 
# MAGIC 
# MAGIC Cross validation, which will solve the problem of the unreliable test-loss that we saw in question 5, presents a bit more of a scalability challenge. To avoid over-dependence on a particulary good or bad test/train split we divide the data into `k` roughly equal size parts and train `k` models. The `k-th` model is trained on all the data _except_ the `k-th` split which is used as a test set for that model. Finally we compute the loss by averaging together the test/train loss for each model. In this question we've provided a code base to perform gradient descent and cross validation in parallel. You'll fill in some of the key details based on your understanding from questions 1-5.
# MAGIC 
# MAGIC #### From ISLR Chapter 5.1 - Cross Validation
# MAGIC <img src="https://github.com/kyleiwaniec/w261_assets/blob/master/images/CV-ISLRp181.png?raw=true">
# MAGIC 
# MAGIC 
# MAGIC ### Q6 Tasks:
# MAGIC * __a) short response:__ A naive approach to training an OLS Regression model with cross validation might be to simply perform Gradient Descent on each of the 5 models in sequence. In this naive approach, how many total passes would be made over the data? [__`HINT:`__ _it will depend on factors that you should be able to name._]
# MAGIC 
# MAGIC 
# MAGIC * __b) short response:__ Read through the provided helper function `kResiduals()` and note where it gets used in the subsequent function `CVLoss()`. For each record in the original dataset, how many tuples does `kResiduals()` emit? What are the keys of these newly emitted records? How will these keys help us compute cross validated loss?
# MAGIC 
# MAGIC 
# MAGIC * __c) code:__ Complete the missing Spark code in `CVLoss()` so that this function returns the test/train cross validated error for a given set of data splits and their corresponding models. [__`TIP:`__ _your goal is to start from `partialLossRDD` and compute the test & train loss for each model so that the provided code can take the final average_].
# MAGIC 
# MAGIC 
# MAGIC * __d) code:__ Read through the provided functions `partialGradients()` and `CVUpdate()`. These should have a familiar feel. Fill in the missing line in `CVUpdate()` to update each model and add the (new) array of coefficients to the `new_models` list. 
# MAGIC 
# MAGIC 
# MAGIC * __e) short response:__ Read `GradientDescent_withCV()` and then run the provided code to perform 50 iterations and plot the error curves. What can you conclude from this graph? 

# COMMAND ----------

# MAGIC %md ### Q6 Student Answers:
# MAGIC > __a)__ Type your answer here!  
# MAGIC 
# MAGIC > __b)__ Type your answer here!  
# MAGIC 
# MAGIC > __e)__ Type your answer here!  

# COMMAND ----------

# part b - helper function to emit residuals (RUN THIS CELL AS IS)
def kResiduals(dataPoint, models, splitNum):
    """
    Compute the (squared) residuals for a data point given k different models.
    Note that points from the k-th split are part of the test set for model number k
    and part of the training set for all other models. We'll emit a key to track this.
    Args:
        dataPoint - tuple of (features_array, y)
        models    - list of arrays representing model weights (bias at index 0)
    Returns:
        (stringFormattedKey, squared_error)
    """
    # augment the data point with a bias term at index 0
    X = np.append([1.0], dataPoint[0])
    y = dataPoint[1]
    # emit squared residuals for each model
    for modelNum, W in enumerate(models):
        if modelNum == splitNum:
            yield(f"{modelNum}-test", (W.dot(X) - y)**2)
        else:
            yield(f"{modelNum}-train", (W.dot(X) - y)**2)

# COMMAND ----------

# part c - fill in the missing code below
def CVLoss(dataSplits, models):
    """
    Compute the k-fold cross-validated test and train loss.
    Args:
        dataSplits - list of RDDs corresponding to the k test splits.
        models     - list of k arrays representing model weights (bias at index 0)
    Returns: 
        tuple of floats: (training_loss, test_loss)
    """
    # compute k residuals for each dataPoint (one for each model)
    partialLossRDD = sc.parallelize([])
    for splitNum, splitRDD in enumerate(dataSplits):
        residuals = splitRDD.flatMap(lambda x: kResiduals(x, models, splitNum))
        partialLossRDD = sc.union([partialLossRDD, residuals])
    
    ################ YOUR CODE HERE #################        
    loss = None
    
    
    
    
    ################ (END) YOUR CODE ################# 
    
    test_loss = np.mean([x[1] for x in loss if x[0].split('-')[1] == 'test'])
    training_loss = np.mean([x[1] for x in loss if x[0].split('-')[1] == 'train'])
    return training_loss, test_loss

# COMMAND ----------

# part d - helper function RUN THIS CELL AS IS
def partialGradients(splitNum, dataPoint, models):
    """
    Emit partial gradient for this data point for each model.
    NOTE: a data point from split-number k is in the test set for 
    model-k so we don't compute a partial gradient for that model.
    """
    # augment the data point
    X = np.append([1.0], dataPoint[0])
    y = dataPoint[1]
    # emit partial gradients for each model with a counter for averaging later
    for modelNum, W in enumerate(models):
        if modelNum != splitNum:
            yield (modelNum, [(W.dot(X) - y)*X, 1])

# COMMAND ----------

# part d - perform GD updates for all k models (FILL IN MISSING CODE BELOW)
def CVUpdate(dataSplits, models, learningRate = 0.1):
    """
    Compute gradients for k models given k corresponding dataSplits.
    NOTE: the training set for model-k is all records EXCEPT those in the k-th split.
    """
    # compute partial gradient k-1 times for each fold
    partialsRDD = sc.parallelize([])
    for splitNum, splitRDD in enumerate(dataSplits):
        thisFoldPartialGrads = splitRDD.flatMap(lambda x: partialGradients(splitNum, x, models))
        partialsRDD = sc.union([partialsRDD, thisFoldPartialGrads])

    # compute gradients by taking the average partialGrad for each fold
    gradients = partialsRDD.reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))\
                           .mapValues(lambda x: x[0]/x[1])\
                           .map(lambda x: x[1])\
                           .collect()
    
    # update all k models & return them in a list
    new_models = []
    for W, grad in zip(models, gradients):
        ############# YOUR CODE HERE ############
        pass
        ############# (END) YOUR CODE ###########
    return new_models

# COMMAND ----------

# part e - RUN THIS CELL AS IS
def GradientDescent_withCV(dataSplits, wInit, learningRate=0.1, nSteps = 5, verbose = False):
    """
    Train k models in parallel and track cross validated test/train loss.
    Returns:
        train_hist - (list) of floats
        test_hist - (list) of floats
        model_hist - (list) of arrays representing model coefficients (bias at index 0)
    """
    # broadcast initial models (one for each fold)
    bModels = sc.broadcast([wInit] * len(dataSplits))
    
    
    # initialize lists to track performance
    train_loss_0, test_loss_0 = CVLoss(dataSplits, bModels.value)
    train_hist, test_hist, model_hist = [train_loss_0], [test_loss_0], [wInit]
    
    # perform k gradient updates at a time (one for each fold)
    start = time.time()
    for step in range(nSteps):
        new_models = CVUpdate(dataSplits, bModels.value, learningRate)
           
        bModels = sc.broadcast(new_models)

        # log progress
        train_loss, test_loss = CVLoss(dataSplits, bModels.value)
        train_hist.append(train_loss)
        test_hist.append(test_loss)
        model_hist.append(new_models[0])
        
        if verbose:
            print("-------------------")
            print(f"STEP {step}: ")
            print(f"model 1: {[round(w,4) for w in new_models[0]]}")
            print(f" train loss: {round(train_loss,4)}")
            print(f" test loss: {round(test_loss,4)}")
            
    print(f"\n... trained {nSteps} iterations in {time.time() - start} seconds")
    return train_hist, test_hist, model_hist


# COMMAND ----------

# part d -  run 50 iterations (RUN THIS CELL AS IS)
dataSplits = normedRDD.randomSplit([0.2, 0.2, 0.2, 0.2, 0.2], seed = 2018) 
wInit = BASELINE
trainLoss, testLoss, models = GradientDescent_withCV(dataSplits, wInit, learningRate=0.1, nSteps = 50, verbose = False)

# COMMAND ----------

# part d - take a look (RUN THIS CELL AS IS)
plotErrorCurves(trainLoss, testLoss, title = '5-fold Cross Validated Loss' )

# COMMAND ----------

# MAGIC %md # Question 7: Regularization.
# MAGIC 
# MAGIC Our goal, as always, is to build a linear model that will extend well to unseen data. Chosing the right combination of features to optimize generalizability can be extremely computationally costly given that there are \\(2^{p}\\) potential models that can be built from \\(p\\) features. Traditional methods like forward selection would involve iteratively testing these options to asses which combinations of features achieve a statistically significant prediction.
# MAGIC 
# MAGIC Ridge Regression and Lasso Regression are two popular alternatives to OLS, which enable us to train generalizable models without the trouble of forward selection and/or manual feature selection.  Both methods take advantage of the bias-variance tradeoff by _shrinking_ the model coefficients towards 0 which reduces the variance of our model with little increase in bias. In practice this 'shrinkage' is achieved by adding a penalty (a.k.a. 'regularization') term to the means squared error loss function. In this question you will implement Gradient Descent with ridge and lasso regularization.
# MAGIC 
# MAGIC __`IMPORTANT NOTE:`__ When performing regularization _do not_ include the bias in your regularization term calcultion (Recall, that throughout this assignment we've included the bias at index 0 in the vector of weights that is your model).
# MAGIC 
# MAGIC ### Q7 Tasks:
# MAGIC * __a) short response:__ The regularization term for ridge regression is the square of the \\(L2\\) norm of the weights vector (i.e. the sum of squares of the coefficients) times the regularization parameter, \\(\lambda\\). Write the formulas for both the loss function and the gradient for Ridge Regularization and explain what extra step this will add to our gradient descent algorithm.
# MAGIC 
# MAGIC 
# MAGIC * __b) short response:__ The regularization term for lasso regression is the \\(L1\\) norm of the weights vector (i.e. the sum of the absolute values of the coefficients) times the regularization parameter, \\(\lambda\\). Write the formulas for both the loss function and the gradient for Lasso Regularization and explain how the gradient descent update in Lasso will be different than it was in Ridge.
# MAGIC 
# MAGIC 
# MAGIC * __c) code:__ Fill in the first two missing code blocks in `GDUpdate_wReg()` so that this function will perform a single parameter update using \\(L2\\) regularization if the parameter `regType` is set to `ridge`, \\(L1\\) regularization if set to `lasso` and unregularized OLS otherwise.
# MAGIC 
# MAGIC 
# MAGIC * __d) code + short response:__ Use the provided code to train 50 iterations of ridge and lasso regression and plot the test/train error. Comment on the curves you see. Does this match your expectation?

# COMMAND ----------

# MAGIC %md ### Q7 Student Answers:
# MAGIC > __a)__ Type your answer here!  
# MAGIC 
# MAGIC > __b)__ Type your answer here!  
# MAGIC 
# MAGIC > __d)__ Type your answer here!  

# COMMAND ----------

# part c - gradient descent with regularization
def GDUpdate_wReg(dataRDD, W, learningRate = 0.1, regType = None, regParam = 0.1):
    """
    Perform one gradient descent step/update with ridge or lasso regularization.
    Args:
        dataRDD - tuple of (features_array, y)
        W       - (array) model coefficients with bias at index 0
        learningRate - (float) defaults to 0.1
        regType - (str) 'ridge' or 'lasso', defaults to None
        regParam - (float) regularization term coefficient
    Returns:
        model   - (array) updated coefficients, bias still at index 0
    """
    # augmented data
    augmentedData = dataRDD.map(lambda x: (np.append([1.0], x[0]), x[1]))
    
    new_model = None
    #################### YOUR CODE HERE ###################

    
    
    
    
    ################## (END) YOUR CODE ####################
    return new_model

# COMMAND ----------

# part d - ridge/lasso gradient descent function
def GradientDescent_wReg(trainRDD, testRDD, wInit, nSteps = 20, learningRate = 0.1,
                         regType = None, regParam = 0.1, verbose = False):
    """
    Perform nSteps iterations of regularized gradient descent and 
    track loss on a test and train set. Return lists of
    test/train loss and the models themselves.
    """
    # initialize lists to track model performance
    train_history, test_history, model_history = [], [], []
    
    # perform n updates & compute test and train loss after each
    model = wInit
    for idx in range(nSteps):  
        # update the model
        model = GDUpdate_wReg(trainRDD, model, learningRate, regType, regParam)
        
        # keep track of test/train loss for plotting
        train_history.append(OLSLoss(trainRDD, model))
        test_history.append(OLSLoss(testRDD, model))
        model_history.append(model)
        
        # console output if desired
        if verbose:
            print("----------")
            print(f"STEP: {idx+1}")
            print(f"training loss: {training_loss}")
            print(f"test loss: {test_loss}")
            print(f"Model: {[round(w,3) for w in model]}")
    return train_history, test_history, model_history

# COMMAND ----------

# run 50 iterations of ridge (RUN THIS CELL AS IS)
wInit = BASELINE
trainRDD, testRDD = normedRDD.randomSplit([0.8,0.2], seed = 5)
start = time.time()
ridge_results = GradientDescent_wReg(trainRDD, testRDD, wInit, nSteps = 50, 
                                     regType='ridge', regParam = 0.05 )
print(f"\n... trained {len(ridge_results[2])} iterations in {time.time() - start} seconds")

# COMMAND ----------

# part d - save and display ridge results (RUN THIS CELL AS IS)
trainLoss, testLoss, models = ridge_results
dbutils.fs.put(hw4_path + 'ridge_models.txt', str(models), True)
dbutils.fs.put(hw4_path + 'ridge_loss.txt', str([trainLoss, testLoss]), True)
plotErrorCurves(trainLoss, testLoss, title = 'Ridge Regression Error Curves' )

# COMMAND ----------

# run 50 iterations of lasso (RUN THIS CELL AS IS)
wInit = BASELINE
trainRDD, testRDD = normedRDD.randomSplit([0.8,0.2], seed = 5)
start = time.time()
lasso_results = GradientDescent_wReg(trainRDD, testRDD, wInit, nSteps = 50,
                                     regType='lasso', regParam = 0.05)
print(f"\n... trained {len(lasso_results[2])} iterations in {time.time() - start} seconds")

# COMMAND ----------

# part d - save and display lasso results (RUN THIS CELL AS IS)
trainLoss, testLoss, models = lasso_results
dbutils.fs.put(hw4_path + 'lasso_models.txt', str(models), True)
dbutils.fs.put(hw4_path + 'lasso_loss.txt', str([trainLoss, testLoss]), True)
plotErrorCurves(trainLoss, testLoss, title = 'Lasso Regression Error Curves' )

# COMMAND ----------

# MAGIC %md # Question 8: Results
# MAGIC 
# MAGIC In this final question we'll use a few different plots to help us compare the OLS, Ridge and Lasso models that we have trained. Use the provided code to load the training history from file and retrieve the best (i.e. last) model from each method.
# MAGIC 
# MAGIC ### Q8 Tasks:
# MAGIC * __a) code:__ Use the provided code to load the training history from file and retrieve the best (i.e. last) model from each method. Then computereate a new RDD called `validationRDD` by computing the mean squared error on the held out dataset for each of the three models. [__`TIP:`__ _the held out data is in it's raw form, don't forget to parse and normalize before applying your calculations, you should also be careful to normalize using the same scaling parameters that you used for the training data._]
# MAGIC 
# MAGIC * __b) short response:__ Which model performed best? Discuss how you interpret these results and what you would want to try next.
# MAGIC 
# MAGIC 
# MAGIC * __c) short response:__ Use the provided code to plot side by side boxplots of the residuals vs. the outcome (i.e. `quality`). What can you observe about our model performance? [__`TIP:`__ _note that the heldout data set is plenty small enough to fit in memory so no need to sample. Feel free to do your plotting in pandas or any other comfortable python package._]
# MAGIC 
# MAGIC 
# MAGIC * __d) short response:__ Run the provided code to visualize the model coefficients for the first 50 iterations of training. What do you observe about how the OLS, ridge and lasso coefficients change over the course of the training process. Please be sure to discuss all three in your response.

# COMMAND ----------

# MAGIC %md ### Q8 Student Answers:
# MAGIC > __b)__ Type your answer here!  
# MAGIC 
# MAGIC > __c)__ Type your answer here!  
# MAGIC 
# MAGIC > __d)__ Type your answer here!  

# COMMAND ----------

# part a - load the models from file (RUN THIS CELL AS IS)
ridge_models = open(hw4_path_open + 'ridge_models.txt', 'r').read()
lasso_models = open(hw4_path_open + 'lasso_models.txt', 'r').read()
ols_models = open(hw4_path_open + 'ols_models.txt', 'r').read()
ridge_models = np.array(ast.literal_eval(re.sub(r'[()\n]','',re.sub('array', '', ridge_models))))
lasso_models = np.array(ast.literal_eval(re.sub(r'[()\n]','',re.sub('array', '', lasso_models))))
ols_models = np.array(ast.literal_eval(re.sub(r'[()\n]','',re.sub('array', '', ols_models))))
best_ols = ols_models[-1,:]
best_ridge = ridge_models[-1,:]
best_lasso = lasso_models[-1,:]

# COMMAND ----------

# part a - compute MSE on the held out data for all three 'best' models
olsMSE, ridgeMSE, lassoMSE = None, None, None
validationRDD = None
############### YOUR CODE HERE #################






############### YOUR CODE HERE #################

print(f"OLS Mean Squared Error: {olsMSE}")
print(f"Ridge Mean Squared Error: {ridgeMSE}")
print(f"Lasso Mean Squared Error: {lassoMSE}")

# COMMAND ----------

# part c - helper function (RUN THIS CELL AS IS)
def get_residuals(dataRDD, model):
    """
    Return a collected list of tuples (residual, quality_score)
    """
    augmentedData = dataRDD.map(lambda x: (np.append([1.0], x[0]), x[1]))
    residuals = augmentedData.map(lambda x: (x[1] - model.dot(x[0]), x[1]))
    return residuals.collect()

# COMMAND ----------

# part c - compute residuals for all three models (RUN THIS CELL AS IS)
ols_resid = np.array(get_residuals(validationRDD, best_ols))
ridge_resid = np.array(get_residuals(validationRDD, best_ridge))
lasso_resid = np.array(get_residuals(validationRDD, best_lasso))

# COMMAND ----------

# part c - boxplots of residuals for all three models (RUN THIS CELL AS IS)
fig, axes = plt.subplots(1, 3, figsize=(15,5))
stuff_to_plot = zip(axes, ["OLS", "Ridge", "Lasso"], [ols_resid, ridge_resid, lasso_resid])
for ax, title, data in stuff_to_plot:
    ax.set_title(title)
    y = data[:, 0]
    x = data[:, 1]
    sns.boxplot(x, y, ax=ax)
fig.suptitle("Prediction Error vs. Quality Score", fontsize=15, y=0.98)
display(plt.show())

# COMMAND ----------

# part d - plotting function (RUN THIS CELL AS IS)
def plotCoeffs(models, featureNames, title):
    """
    Helper Function to show how coefficients change as we train.
    """
    fig, ax = plt.subplots(figsize = (15,8))
    X = list(range(len(models)))
    for data, name in zip(models.T, featureNames):
        if name == "Bias":
            continue
        ax.plot(X, data, label=name)
    ax.plot(X,[0]*len(X), 'k--')
    plt.title(title)
    plt.legend()
    display(plt.show())

# COMMAND ----------

# take a look (RUN THIS CELL AS IS)
plotCoeffs(ols_models, ['Bias'] + FIELDS, "OLS Coefficients over 50 GD steps")

# COMMAND ----------

# take a look (RUN THIS CELL AS IS)
plotCoeffs(ridge_models, ['Bias'] + FIELDS, "Ridge Coefficients over 50 GD steps")

# COMMAND ----------

# take a look (RUN THIS CELL AS IS)
plotCoeffs(lasso_models, ['Bias'] + FIELDS, "Lasso Coefficients over 50 GD steps")

# COMMAND ----------

# MAGIC %md ### Congratulations, you have completed HW4! Please refer to the readme for submission instructions.
# MAGIC 
# MAGIC If you would like to provide feedback regarding this homework, please use the survey at: https://docs.google.com/forms/d/e/1FAIpQLSce9feiQeSkdP43A0ZYui1tMGIBfLfzb0rmgToQeZD9bXXX8Q/viewform

# COMMAND ----------

