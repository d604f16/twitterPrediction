#!/usr/bin/python

import csv
from tweet import Tweet

#locations = ['England', 'CA', 'TX', 'NY', 'MA', 'MD', 'FL', 'Ontario', 'IL', 'WA', 'CO', 'PA', 'GA', 'OH', 'TN', 'VA', 'AZ', 'MI', 'NC', 'NJ', 'OR', 'MN', 'NV']

locations = []
with open('inputData/split.csv', 'rb') as csvfile:
  fieldnames = ['txt']
  splitreader = csv.DictReader(csvfile, fieldnames, delimiter=';', quotechar='"')
  for row in splitreader:
    locations.append(row['txt'])

tweetCounts = {}
tweets = {}
for location in locations:
  tweetCounts[location] = 0
  tweets[location] = []

#startTime = time.time()
with open('inputData/allTweets.csv', 'rb') as csvfile:
  with open('inputData/loc.csv', 'w+') as writefile:
    fieldnames = ['id', 'user', 'txt', 'location']
    tweetreader = csv.DictReader(csvfile, fieldnames, delimiter=';', quotechar='"')
    tweetwriter = csv.DictWriter(writefile, fieldnames, delimiter=';', quotechar='"')
    for row in tweetreader:
      if row['location'] in locations:
        if tweetCounts[row['location']] < 2000:
          tweets[row['location']].append(Tweet(row['id'], row['user'], row['txt'], row['location']))
#          tweetwriter.writerow({'id': row['id'], 'user': row['user'], 'txt': row['txt'], 'location': row['location']})
          tweetCounts[row['location']] = tweetCounts[row['location']] + 1

    for location in locations:
      for tweet in tweets[location]:
        tweetwriter.writerow({'id': tweet.id, 'user': tweet.user, 'txt': tweet.txt, 'location': tweet.location})

#elapsedTime = time.time() - startTime
#print "Loaded tweets in {} ms".format(int(elapsedTime * 1000))

for key, var in tweetCounts.iteritems():
  print key + ": " + var.__str__()
