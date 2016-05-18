#Import string for stuff like string.punctuation
#used to clean text
import string

#Import csv for writing/reading csv files
import csv

import math
from itertools import islice
from multiprocessing import Process, Queue
import multiprocessing

class Classifier:
  'Class for classifying tweets'
  
  def __init__(self):
    'Constructor: initiate dictionaries'

    # initiate stopword list
    self.stopwords = []

    # initiate dictionaries for counting words and classes
    self.totalWordCounts = {}
    self.classWordCounts = {}
    self.totalClassCounts = {}

    # initiate ints for counting total words and classes
    self.totalWords = 0
    self.totalClasses = 0

    # initiate dictionaries for storing probabilities
    self.wordProbabilities = {}
    self.classProbabilities = {}
#    self.wordProbabilitiesGivenClass = {}
    self.classProbabilitiesGivenWord = {}

  #end def __init__

  def setStopwords(self, stopwords):
    self.stopwords = stopwords
  #end def setStopWords

  def learn(self, txt, theClass):
    'Scan an entry and count stuff.'

    self.totalClasses += 1
    
    if(not self.classWordCounts.has_key(theClass)):
      self.classWordCounts[theClass] = {}

    if(self.totalClassCounts.has_key(theClass)):
      self.totalClassCounts[theClass] = self.totalClassCounts[theClass] + 1
    else:
      self.totalClassCounts[theClass] = 1
    
    cleanedTxt = self.cleanText(txt)
    words = cleanedTxt.split()
    
    for word in words:
      self.totalWords = self.totalWords + 1
      if(self.totalWordCounts.has_key(word)):
        self.totalWordCounts[word] = self.totalWordCounts[word] + 1
      else:
        self.totalWordCounts[word] = 1
      
      if(self.classWordCounts[theClass].has_key(word)):
        self.classWordCounts[theClass][word] = self.classWordCounts[theClass][word] + 1
      else:
        self.classWordCounts[theClass][word] = 1
  #end def learn

  def calculateWordProbability(self, file):
    'Calculate and save the probabilities for any given word'
    fieldnames = ['word', 'probability']

    removeKeys = []

    writer = csv.DictWriter(file, fieldnames, delimiter=';', quotechar='"')

    for key, wordCount in self.totalWordCounts.iteritems():
#      if(wordCount < 3):
#        removeKeys.append(key)
#      else:
        self.wordProbabilities[key] = float(wordCount)/self.totalWords
        writer.writerow({ 'word': key, 'probability': self.wordProbabilities[key]})

#    for key in removeKeys:
#      del self.totalWordCounts[key]

  #end def calculateWordProbability

  def calculateClassProbability(self, file):
    'Calculate and save the probabilities for any given class'
    fieldnames = ['class', 'probability']

    removeKeys = []

    writer = csv.DictWriter(file, fieldnames, delimiter=';', quotechar='"')

    for key, classCount in self.totalClassCounts.iteritems():
#      if(classCount < 3):
#        removeKeys.append(key)
#      else:
        self.classProbabilities[key] = float(classCount)/self.totalClasses
        writer.writerow({ 'class': key, 'probability': self.classProbabilities[key]})

#    for key in removeKeys:
#      del self.totalClassCounts[key]
#      del self.classWordCounts[key]

  #end def calculateClassProbability

  def calculateExtendedProbabilities(self, classGivenFileName):
    'Calculate and save the probabilitues for any given word, given class'
    fieldnames = ['word', 'class', 'probability']
    
    vocSize = len(self.totalWordCounts)
    i = 0

    for theClass, wordCounts in self.classWordCounts.iteritems():
      self.classProbabilitiesGivenWord[theClass] =  {}
      cleanClass = theClass.translate(None, '/');
      if 1==1:

#      with open(classGivenFileName + cleanClass + '.csv', 'w+') as classGivenFile:
#        classGivenWriter = csv.DictWriter(classGivenFile, fieldnames, delimiter=';', quotechar='"')

          #formulae: P(word|class) = \frac{nk + 1}{n + |voc|}, where:
          #nk    = times the word is used, given this class
          #n     = times the word is used in total
          #|voc| = size of the vocabulary, i.e. total distinct words

        for word, totalWordCount in self.totalWordCounts.iteritems():
          i = i + 1
          if i % 100 == 0:
            print i
 
          wordCount = 0
          if(wordCounts.has_key(word)):
            wordCount = wordCounts[word]

          probability = (float(wordCount) + 1)/(totalWordCount + vocSize)

          probability = (probability*self.classProbabilities[theClass])/self.wordProbabilities[word]
#          classGivenWriter.writerow({'word': word, 'class': theClass, 'probability': probability })
          self.classProbabilitiesGivenWord[theClass][word] = probability
      
  #end def calculateExtendedProbabilities


  def classifyEntry(self, text, description, queue):
    'classify an entry'
    text = self.cleanText(text)

    probabilities = {}

    words = set(text.split())
    
    for theClass, wordProbabilities in self.classProbabilitiesGivenWord.iteritems():
      probability = float(0)
      
      keys_wordProbabilities = set(wordProbabilities.keys())
      usedWords = keys_wordProbabilities & words

      for word in usedWords:
        probability += math.log(wordProbabilities[word])

      probabilities[theClass] = probability

    mostLikely = max(probabilities, key=probabilities.get)
    
    queue.put([description, mostLikely, probabilities[mostLikely]])
  
  #end def classifyEntry

  def classifyEntryFromFiles(self, text, description, queue):
    'Classify an entry from files'
    text = self.cleanText(text)

    probabilities = {}

    words = set(text.split())

    fieldnames = ['word', 'class', 'probability']

    # TODO: THIS IS NOT THE RIGHT WAY TO DO THIS!!!
    wordGivenFileName = 'outputData/wordGivenClass-'
    classGivenFileName = 'outputData/classGivenWord-'

    for theClass in self.totalClassCounts:
      cleanClass = theClass.translate(None, '/')
      probability = 0
      with open(classGivenFileName + cleanClass + '.csv', 'rb') as classGivenFile:
        classReader = csv.DictReader(classGivenFile, fieldnames, delimiter=';', quotechar='"')
        
        for row in classReader:
          if row['word'] in words:
             probability +=math.log(float(row['probability']))

        probabilities[theClass] = probability

    mostLikely = max(probabilities, key=probabilities.get)

#    print mostLikely

    queue.put([description, mostLikely, probabilities[mostLikely]])

#  end def classifyEntryFromFriles

  def classifyEntries(self, entries, descriptors, queue):
    i = 0
    while(i < len(entries)):
      self.classifyEntry(entries[i], descriptors[i], queue)
      i = i + 1
  #end def classifyEntries

  def cleanText(self, text):
    'Clean text for processing'

    text = text.lower()

    cleanedWords = text.split()

    resultWords = [word for word in cleanedWords if word not in self.stopwords]

#    resultWords = [word for word in resultWords if "@" not in word]

    resultWords = [word for word in resultWords if "http" not in word]

    cleanedTxt =' '.join(resultWords)

    cleanedTxt = cleanedTxt.translate(None, string.punctuation)
    
    return cleanedTxt

  #end def cleanText

  def chunkifyDict(self, seq, chunks):
    avg = len(seq)/chunks + 1
    it = iter(seq)
  
    for i in xrange(0, len(seq), avg):
      yield {k:seq[k] for k in islice(it, avg)}

  #end def chunkifyDict
