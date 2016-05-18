#!/usr/bin/python

import csv
from tweet import Tweet
from buckets import Buckets
from modelBuilder import ModelBuilder
from classifier import Classifier
import time
from multiprocessing import Process, Queue
import sys

#make it into buckets
buckets = Buckets(10)

modelSettings = {}
modelSettings['useMentions'] = 1
modelSettings['useLinks'] = 1

modelBuilder = ModelBuilder()

stopwords = []

startTime = time.time()

if(len(sys.argv) > 1):
  stopnum = sys.argv[1]
else:
  stopnum = 1

if(len(sys.argv) > 2):
  tweetFileName = 'inputData/' + sys.argv[2] + '.csv'
else:
  tweetFileName = 'inputData/tweets.csv'

if(len(sys.argv) > 3):
    gramsFileName = 'inputData/' + sys.argv[3] + '.csv'
    useGrams = 1
else:
    useGrams = 0
    

with open('inputData/stop{}.csv'.format(stopnum), 'rb') as csvfile:
  fieldnames = ['str']
  stopreader = csv.DictReader(csvfile, fieldnames, delimiter=';', quotechar='"')
  for row in stopreader:
    stopwords.append(row['str'])
    
grams = []
if useGrams == 1:
  with open(gramsFileName, 'rb') as csvfile:
    fieldnames = ['str']
    gramreader = csv.DictReader(csvfile, fieldnames, delimiter=';', quotechar='"')
    for row in gramreader:
      grams.append(row['str'])

modelBuilder.setGrams(grams)

modelBuilder.setStopwords(stopwords)
elapsedTime = time.time() - startTime
print "Loaded stopwords in {} ms".format(int(elapsedTime*1000))

startTime = time.time()
with open(tweetFileName, 'rb') as csvfile:
  fieldnames = ['id', 'user', 'txt', 'location']
  tweetreader = csv.DictReader(csvfile, fieldnames, delimiter=';', quotechar='"')
  for row in tweetreader:
    t = Tweet(row['id'], row['user'], row['txt'], row['location'])
    buckets.add(t)
elapsedTime = time.time() - startTime
print "Loaded tweets in {} ms".format(int(elapsedTime * 1000))

startTime = time.time()
i = 0
for x in buckets.buckets:
  i+= 1
  if(not i == 1):
#    print "Bucket no " + i.__str__()
    for y in x:
      modelBuilder.learn(y.txt, y.location)
#    print "len of bucket: " + len(x).__str__()
elapsedTime = time.time() - startTime
print "Learned Tweets in {} ms".format(int(elapsedTime * 1000))

startTime = time.time()
with open('outputData/wordProbabilities.csv', 'w+') as wordProbFile:
  modelBuilder.calculateWordProbability(wordProbFile)
#print "Done calculating word probabilitites"
elapsedTime = time.time() - startTime
print "Calculated word probabilities in {} ms".format(int(elapsedTime * 1000))

startTime = time.time()
with open('outputData/classProbabilities.csv', 'w+') as classProbFile:
  modelBuilder.calculateClassProbability(classProbFile)
#print "Done calculating class probabilitities"
elapsedTime = time.time() - startTime
print "Calculated class probabilities in {} ms".format(int(elapsedTime * 1000))

startTime = time.time()
modelBuilder.calculateExtendedProbabilities()
#print "Done calculating word probabilities given class"
elapsedTime = time.time() - startTime
print "Calculated word|class and class|word probablilities in {} ms".format(int(elapsedTime * 1000))

#print len(classifier.totalClassCounts)
#print len(classifier.classWordCounts)
#print len(classifier.wordProbabilitiesGivenClass['the'])
#print len(classifier.wordProbabilitiesGivenClass)
#print len(classifier.totalWordCounts)

#system.exit()

startTime = time.time()
with open('outputData/guesses.csv', 'w+') as guessFile:
  correctGuesses = 0
  totalGuesses = 0
  fieldnames = ['id', 'user', 'txt', 'guessedLocation', 'realLocation', 'certainty', 'correct']
  writer = csv.DictWriter(guessFile, fieldnames, delimiter=';', quotechar='"')

  tweets = buckets.buckets[0]

  tweetTexts = []
  tweetIds = []

  for tweet in tweets:
    tweetTexts.append(tweet.txt)
    tweetIds.append(tweet)

  classifierSettings = {'classes': modelBuilder.totalClassCounts, 'useMentions': 1, 'useLinks': 1}

  classifier = Classifier(classifierSettings)

  classifier.setStopwords(stopwords)
  classifier.setGrams(grams)

  guesses = classifier.classifyEntries(tweetTexts, tweetIds)

  correctGuesses = 0
  
  locationGuesses = {}
  correctLocationGuesses = {}

  for theClass in modelBuilder.totalClassCounts:
    locationGuesses[theClass] = 0
    correctLocationGuesses[theClass] = 0

  for guess in guesses:
    writer.writerow({'id': guess['descriptor'].id, 'user': guess['descriptor'].user, 'txt': guess['descriptor'].txt, 'guessedLocation': guess['class'], 'realLocation': guess['descriptor'].location, 'certainty': guess['likelihood'], 'correct': guess['class'] == guess['descriptor'].location})
    print guess['class'] + ' =? ' + guess['descriptor'].location 
    if guess['class'] == guess['descriptor'].location:
      correctGuesses += 1
      correctLocationGuesses[guess['class']] = correctLocationGuesses[guess['class']] + 1
    locationGuesses[guess['class']] = locationGuesses[guess['class']] + 1

  for theClass in modelBuilder.totalClassCounts:
    print theClass + ": " + locationGuesses[theClass].__str__() + ", " + correctLocationGuesses[theClass].__str__()

print "I guessed " + correctGuesses.__str__() + " correctly."
elapsedTime = time.time() - startTime
print "Guessed classes in {} ms".format(int(elapsedTime * 1000))
print "Done"
