# -*- coding: utf-8 -*-
"""COMP330_A6_TASK3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AkeVnS1ORy3Nq-NVo7bIqDJR3b9UNpdL
"""

import tensorflow.compat.v1 as tf
import numpy as np
import urllib
tf.compat.v1.disable_eager_execution()

# the number of iterations to train for
numTrainingIters = 10000

# the number of hidden neurons that hold the state of the RNN
hiddenUnits = 1000

# the number of classes that we are learning over
numClasses = 3

# the number of data points in a batch
batchSize = 100

# this function takes a dictionary (called data) which contains
# of (dataPointID, (classNumber, matrix)) entries.  Each matrix
# is a sequence of vectors; each vector has a one-hot-encoding of
# an ascii character, and the sequence of vectors corresponds to
# one line of text.  classNumber indicates which file the line of
# text came from.
#
# The argument maxSeqLen is the maximum length of a line of text
# seen so far.  fileName is the name of a file whose contents
# we want to add to data.  classNum is an indicator of the class
# we are going to associate with text from that file.  linesToUse
# tells us how many lines to sample from the file.
#
# The return val is the new maxSeqLen, as well as the new data
# dictionary with the additional lines of text added
def addToData (maxSeqLen, data, fileName, classNum, linesToUse):
    #
    # open the file and read it in
    response = urllib.request.urlopen(fileName)
    content = response.readlines ()
    #
    # sample linesToUse numbers; these will tell us what lines
    # from the text file we will use
    myInts = np.random.randint (0, len(content), linesToUse)
    #
    # i is the key of the next line of text to add to the dictionary
    i = len(data)
    #
    # loop thru and add the lines of text to the dictionary
    for whichLine in myInts.flat:
        #
        # get the line and ignore it if it has nothing in it
        line = content[whichLine].decode("utf-8")
        if line.isspace () or len(line) == 0:
            continue;
        #
        # take note if this is the longest line we've seen
        if len (line) > maxSeqLen:
            maxSeqLen = len (line)
        #
        # create the matrix that will hold this line
        temp = np.zeros((len(line), 256))
        #
        # j is the character we are on
        j = 0
        #
        # loop thru the characters
        for ch in line:
            #
            # non-ascii? ignore
            if ord(ch) >= 256:
                continue
            #
            # one hot!
            temp[j][ord(ch)] = 1
            #
            # move onto the next character
            j = j + 1
            #
        # remember the line of text
        data[i] = (classNum, temp)
        #
        # move onto the next line
        i = i + 1
    #
    # and return the dictionary with the new data
    return (maxSeqLen, data)

# this function takes as input a data set encoded as a dictionary
# (same encoding as the last function) and pre-pends every line of
# text with empty characters so that each line of text is exactly
# maxSeqLen characters in size
def pad (maxSeqLen, data):
   #
   # loop thru every line of text
   for i in data:
        #
        # access the matrix and the label
        temp = data[i][1]
        label = data[i][0]
        #
        # get the number of chatacters in this line
        len = temp.shape[0]
        #
        # and then pad so the line is the correct length
        padding = np.zeros ((maxSeqLen - len,256))
        data[i] = (label, np.transpose (np.concatenate ((padding, temp), axis = 0)))
   #
   # return the new data set
   return data

# this generates a new batch of training data of size batchSize from the
# list of lines of text data. This version of generateData is useful for
# an RNN because the data set x is a NumPy array with dimensions
# [batchSize, 256, maxSeqLen]; it can be unstacked into a series of
# matrices containing one-hot character encodings for each data point
# using tf.unstack(inputX, axis=2)
def generateDataRNN (maxSeqLen, data):
    #
    # randomly sample batchSize lines of text
    myInts = np.random.randint (0, len(data), batchSize)
    #
    # stack all of the text into a matrix of one-hot characters
    x = np.stack ([data[i][1] for i in myInts.flat])
    #
    # and stack all of the labels into a vector of labels
    y = np.stack ([np.array((data[i][0])) for i in myInts.flat])
    #
    # return the pair
    return (x, y)

# this also generates a new batch of training data, but it represents
# the data as a NumPy array with dimensions [batchSize, 256 * maxSeqLen]
# where for each data point, all characters have been appended.  Useful
# for feed-forward network training
def generateDataFeedForward(maxSeqLen, data):
    myInts = np.random.randint(0, len(data), batchSize)
    x_list = [data[i][1].flatten() for i in myInts.flat]
    y_list = [np.array(data[i][0]) for i in myInts.flat]
    x = np.stack(x_list)
    y = np.stack(y_list)
    return (x, y)


def splitTest(test, train, length):
    test_indices = range(len(train) - length, len(train)) # not random
    test_data = [train.pop(i) for i in test_indices]
    index = len(test)
    for data in test_data:
        test[index] = data
        index += 1
    return (test, train)

def append(dic1, dic2):
    start = len(dic1)
    dic2_shifted = {key + start: value for key, value in dic2.items()}
    dic1.update(dic2_shifted)

# create the data dictionary
maxSeqLen = 0
data = {}
data_holmes = {}
data_war = {}
data_william = {}
test = {}

# load up the three data sets
(maxSeqLen, data_holmes) = addToData (maxSeqLen, data_holmes, "https://s3.amazonaws.com/chrisjermainebucket/text/Holmes.txt", 0, 11000)
(test, data_holmes) = splitTest(test, data_holmes, 1000) # 1000 test for each doc

(maxSeqLen, data_war) = addToData (maxSeqLen, data_war, "https://s3.amazonaws.com/chrisjermainebucket/text/war.txt", 1, 11000)
(test, data_war) = splitTest(test, data_war, 1000) # 1000 test for each doc

(maxSeqLen, data_william) = addToData (maxSeqLen, data_william, "https://s3.amazonaws.com/chrisjermainebucket/text/william.txt", 2, 11000)
(test, data_william) = splitTest(test, data_william, 1000) # 1000 test for each doc

# aggregate all data
data = dict(data_holmes)
append(data, data_war)
append(data, data_william)

# pad each entry in the dictionary with empty characters as needed so
# that the sequences are all of the same length
data = pad (maxSeqLen, data)
test = pad (maxSeqLen, test)

# now we build the TensorFlow computation... there are two inputs,
# a batch of text lines and a batch of labels
inputX = tf.placeholder(tf.float32, [batchSize, 256 * maxSeqLen])
inputY = tf.placeholder(tf.int32, [batchSize])

# this is the inital state of the RNN, before processing any data
initialState = tf.placeholder(tf.float32, [batchSize, hiddenUnits])

# the weight matrix that maps the inputs and hidden state to a set of values
Wfir = tf.Variable(np.random.normal(0, 0.01, (256 * maxSeqLen, hiddenUnits)), dtype=tf.float32)
Wsec = tf.Variable(np.random.normal(0, 0.01, (hiddenUnits, hiddenUnits)), dtype=tf.float32)

# weights and bias for the final classification
W2 = tf.Variable(np.random.normal (0, 0.05, (hiddenUnits, numClasses)),dtype=tf.float32)
b2 = tf.Variable(np.zeros((1,numClasses)), dtype=tf.float32)

# # unpack the input sequences so that we have a series of matrices,
# # each of which has a one-hot encoding of the current character from
# # every input sequence
# sequenceOfLetters = tf.unstack(inputX, axis=2)
#
# # now we implement the forward pass
# currentState = initialState
#
# state_record = []
# # Fill the state record with initial state for the first 10
# for i in range(10):
#     state_record.append(initialState)
#
# for timeTick in sequenceOfLetters:
#     #
#     # concatenate the state with the input, then compute the next state
#     tenth_state = state_record[0]
#     state_record.pop(0)
#     state_record.append(currentState)
#     inputPlusState = tf.concat([timeTick, tenth_state, currentState], 1)
#     next_state = tf.tanh(tf.matmul(inputPlusState, Wfir))
#     last_state = tf.tanh(tf.matmul(next_state, Wsec))
#     currentState = last_state

# compute the set of outputs
next_state = tf.tanh(tf.matmul(inputX, Wfir))
last_state = tf.tanh(tf.matmul(next_state, Wsec))
outputs = tf.matmul(last_state, W2) + b2

predictions = tf.nn.softmax(outputs)

# compute the loss
losses = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=outputs, labels=inputY)
totalLoss = tf.reduce_mean(losses)

# use gradient descent to train
trainingAlg = tf.compat.v1.train.AdagradOptimizer(0.01).minimize(totalLoss)

# and train!!
with tf.Session() as sess:
    #
    # initialize everything
    sess.run(tf.compat.v1.global_variables_initializer())
    #
    # and run the training iters
    for epoch in range(numTrainingIters):
        #
        # get some data
        x, y = generateDataFeedForward (maxSeqLen, data)
        #
        # do the training epoch
        # _currentState = np.zeros((batchSize, hiddenUnits))
        _totalLoss, _trainingAlg, _predictions, _outputs = sess.run(
                [totalLoss, trainingAlg, predictions, outputs],
                feed_dict={
                    inputX:x,
                    inputY:y,
                })
        #
        # just FYI, compute the number of correct predictions
        numCorrect = 0
        for i in range (len(y)):
           maxPos = -1
           maxVal = 0.0
           for j in range (numClasses):
               if maxVal < _predictions[i][j]:
                   maxVal = _predictions[i][j]
                   maxPos = j
           if maxPos == y[i]:
               numCorrect = numCorrect + 1
        #
        # print out to the screen
        print("Step", epoch, "Loss", _totalLoss, "Correct", numCorrect, "out of", batchSize)

    # Task1, compute accuracy in test
    loss = 0
    cnt = 0
    for i in range(30):
        test_sub = {}
        for m in range(batchSize):
            test_sub[m] = test[i * batchSize + 1]
        x, y = generateDataFeedForward(maxSeqLen, test_sub)
        # _currentState = np.zeros((batchSize, hiddenUnits))
        _totalLoss, _predictions = sess.run(
                [totalLoss, predictions],
                feed_dict={
                    inputX:x,
                    inputY:y,
                })
        loss += _totalLoss

        numCorrect = 0
        for j in range (len(y)):
           maxPos = -1
           maxVal = 0.0
           for k in range (numClasses):
               if maxVal < _predictions[j][k]:
                   maxVal = _predictions[j][k]
                   maxPos = k
           if maxPos == y[j]:
               numCorrect = numCorrect + 1
        cnt += numCorrect
    loss /= 30  # average the loss over all the batches of test data
    print("Loss for {size} randomly chosen documents is {loss}, number correct labels is {numCorrect} out of {size}".format(size=len(test), loss=loss, numCorrect=cnt))