#Import string for stuff like string.punctuation
#used to clean text
import string

#Import csv for writing/reading csv files
import csv

from itertools import ifilter

import math

class Classifier:
  'Class for classifying tweets'

  def __init__(self, settings = {}):
    self.settings = {}
    
    self.settings['classes'] = []
    self.settings['fileTemplate'] = 'outputData/wordProbabilities-$_CLASS_$.csv'
    
    for key, setting in settings.iteritems():
      self.settings[key] = setting
  # end def __init__

  def setStopwords(self, stopwords):
    self.stopwords = stopwords
  #end def setStopWords

  def classifyEntries(self, entries, descriptors):
    fieldnames = ['word', 'class', 'probability']
    
    percentLength = int(len(entries) * len(self.settings['classes']) / 100)
    
    i = 0
    
    self.entries = []

    usedWords = set()
    
    while(i < len(entries)):
      _words = set(self.cleanText(entries[i]).split())
      self.entries.append({'words': _words, 'descriptor': descriptors[i], 'likelihood': -10000000.0, 'class': ''})
      i = i + 1
      usedWords |= _words # Set union. Sweet baby jesus, this is where python shines!
      
        
    i = 0
    for theClass in self.settings['classes']:
      cleanClass = theClass.translate(None, '/')
        
      filename = self.fileName(self.settings['fileTemplate'], {'$_CLASS_$': cleanClass})
    
      probabilities = {}

      with open(filename, 'r+') as classGivenFile:
        
        usedRows = ifilter(lambda x: x.split(';')[0] in usedWords, classGivenFile)
        classReader = csv.DictReader(usedRows, fieldnames, delimiter=';', quotechar='"')
        for row in classReader:
#          print row['word']
          probabilities[row['word']] = math.log(float(row['probability']))
        
        for entry in self.entries:
          i = i + 1
          if i % percentLength == 0:
            print (i / percentLength).__str__() + "%"
            
          probability = 0
          for word, wordProbability in probabilities.iteritems():
            if word in entry['words']:
                probability += wordProbability
                
          if probability > entry['likelihood']:
            entry['likelihood'] = probability
            entry['class'] = theClass
            
    return self.entries
  #end def classifyEntries

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
