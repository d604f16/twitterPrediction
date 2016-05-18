#Import string for stuff like string.punctuation
#used to clean text
import string

#Import csv for writing/reading csv files
import csv

import math

class ModelBuilder:
  'Class for classifying tweets'
  
  def __init__(self, settings = {}):
    'Constructor: initiate dictionaries'

    # initiate stopword list
    self.stopwords = []
    
    self.settings = {}
    
    # Default settings
    self.settings['useMentions'] = 1
    self.settings['useLinks'] = 1
    self.settings['fileTemplate'] = 'outputData/wordProbabilities-$_CLASS_$.csv'
    
    # Overwrite settings
    for name, setting in settings.iteritems():
      self.settings[name] = setting

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
      if(classCount < 3):
        removeKeys.append(key)
      else:
        self.classProbabilities[key] = float(classCount)/self.totalClasses
        writer.writerow({ 'class': key, 'probability': self.classProbabilities[key]})

    for key in removeKeys:
      del self.totalClassCounts[key]
      del self.classWordCounts[key]

  #end def calculateClassProbability

  def calculateExtendedProbabilities(self):
    'Calculate and save the probabilitues for any given word, given class'
    fieldnames = ['word', 'class', 'probability']
    
    vocSize = len(self.totalWordCounts)
    i = 0

    for theClass, wordCounts in self.classWordCounts.iteritems():
#      self.classProbabilitiesGivenWord[theClass] =  {}
      cleanClass = theClass.translate(None, '/');
        
      filename = self.fileName(self.settings['fileTemplate'], {'$_CLASS_$': cleanClass})

      with open(filename, 'w+') as classGivenFile:
        classGivenWriter = csv.DictWriter(classGivenFile, fieldnames, delimiter=';', quotechar='"')

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
          classGivenWriter.writerow({'word': word, 'class': theClass, 'probability': probability })
#          self.classProbabilitiesGivenWord[theClass][word] = probability
      
  #end def calculateExtendedProbabilities

  def fileName(self, template, replace):
    for old, new in replace.iteritems():
      template = template.replace(old, new);
    return template
  #end def fileName
    
  def setGrams(self, grams):
    self.grams = grams
  #end def setGrams

  def cleanText(self, text):
    'Clean text for processing'

    text = text.lower()
    
    for ngram in self.grams:
      text = text.replace(ngram, ngram.replace(' ', '.'))
  
    if self.settings['useMentions'] == 0:
      text = ' '.join(filter(lambda x:x[0]!='@', text.split()))

    cleanedText = text.translate(None, string.punctuation)

    cleanedWords = cleanedText.split()

    resultWords = [word for word in cleanedWords if word not in self.stopwords]

    if self.settings['useLinks'] == 0:
      resultWords = [word for word in resultWords if "http" not in word]

    cleanedTxt =' '.join(resultWords)

    return cleanedTxt

  #end def cleanText

#end def class ModelBuilder
