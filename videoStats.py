#!/usr/bin/env python3
import csv
from os import path, listdir, makedirs
from datetime import datetime
from _collections import OrderedDict

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

csvComments = config['REFACTOR']['FolderToPutReformattedCsvComments']
csvFindings = config['ANALYSIS']['FolderToPutAnomalousFindings']
significantRatio = int(config['ANALYSIS']['SignificantRatio'])

# Load comments from the csv comments folder
def loadComments():
	globalComments = {}
	streamAccounts = {}
	print('Reading comments from:')
	for channel in listdir(csvComments):
		channelFolder = path.join(csvComments, channel)
		if not path.isdir(channelFolder):
			continue
		print('   ' + channel)
		for streamCsv in listdir(channelFolder):
			if not streamCsv.endswith('.csv'):
				continue
			csvName = path.join(channelFolder, streamCsv)
			stream = csvName.split('/')[-1][:-4]
			streamAccounts[stream] = channel
			globalComments[stream] = loadStreamComments(csvName)
	return streamAccounts, globalComments

# Setup global library of comments per user per stream
def loadStreamComments(csvName):
	comments = {}
	csvFile = csv.reader(open(csvName, 'r'), delimiter=',')
	next(csvFile) # skip the header
	for row in csvFile:
		# ID,TIME,USER,TEXT
		TIME = row[1]
		USER = row[2]
		TEXT = row[3]
		if USER not in comments:
			comments[USER] = []
		comments[USER].append((TIME, TEXT))
	return comments

# Comment count distribution (of users) in a given stream
def commentCountDistribution(streamComments):
	commentCount = OrderedDict()
	for user in streamComments:
		count = len(streamComments[user])
		if count not in commentCount:
			commentCount[count] = []
		commentCount[count].append(user)
	commentDistribution = {}
	for count in sorted(commentCount.keys()):
		commentDistribution[count] = len(commentCount[count])
	return commentDistribution

# Posting speed stats of users in a given stream
def commentSpeedDistribution(streamComments):
	speedDistribution = OrderedDict()
	for user in streamComments:
		userCount = len(streamComments[user])
		if userCount < 3:
			continue
		lastTimestamp = None
		timegaps = []
		for comment in streamComments[user]:
			timestamp = datetime.strptime(comment[0], '%H:%M:%S,%f')
			if lastTimestamp:
				gap = timestamp - lastTimestamp
				gapTime = int(gap.seconds * 1e3)
				gapTime += int(gap.microseconds / 1e3)
				timegaps.append(gapTime)
			lastTimestamp = timestamp
		gapAverage = int(sum(timegaps) / len(timegaps))
		gapRange = max(timegaps) - min(timegaps)
		speedDistribution[user] = (gapAverage, gapRange)
	return speedDistribution


# Find average, median of comment counts of users in stream
def commentCountStats(countDistribution):
	totalComments = 0
	totalUsers = 0
	meanCount = 0
	medianCount = 0

	# Average comment count of users in stream
	for commentCount in countDistribution:
		userCount = countDistribution[commentCount]
		totalComments += (commentCount * userCount)
		totalUsers += userCount
	if totalUsers > 0:
		meanCount = int(totalComments / totalUsers)

	# User comment count range in stream
	halfUsers = totalUsers / 2
	for commentCount in countDistribution:
		userCount = countDistribution[commentCount]
		if halfUsers < userCount:
			if medianCount == 0:
				medianCount = commentCount
			else:
				medianCount = int((medianCount + commentCount) / 2)
			break
		else:
			halfUsers -= userCount
			if halfUsers < 1:
				medianCount += commentCount
	return meanCount, medianCount

# Find average, median of comment speed of users in stream
def commentSpeedStats(speedDistribution):
	meanSpeed = 0
	medianSpeed = 0
	userCount = 0
	userSpeeds = []

	# Average comment speed in stream
	for user in speedDistribution:
		userCount += 1
		userGapAverage, userGapRange = speedDistribution[user]
		meanSpeed += userGapAverage
		userSpeeds.append(userGapAverage)

	# In the unlikely event there are too few comments in the stream to be useful
	if userCount <= 1:
		return meanSpeed, medianSpeed

	# This way we avoid a divide by 0 error
	meanSpeed = int(meanSpeed / userCount)

	# Median comment speed in stream
	if len(userSpeeds) % 2 == 0:
		medianSpeed = sorted(userSpeeds)[int(len(userSpeeds) / 2)]
	else:
		lower = int(len(userSpeeds) / 2)
		upper = lower + 1
		medianSpeed = int((sorted(userSpeeds)[lower] + sorted(userSpeeds)[upper]) / 2)
	return meanSpeed, medianSpeed

# Return a list of anomalous users from a given stream
def anomalousUsers(streamStats, streamComments, speedDistribution):
	userList = []
	countThreshold = streamStats[1] * significantRatio # mean N times as many as median count
	speedThreshold = int(streamStats[3] / significantRatio) # mean is N times as fast as median speed (in milliseconds)

	for user in streamComments:
		if user not in speedDistribution:
			continue
			# user must be anomalous in speed
		userCount = len(streamComments[user]) # user count of comments in stream
		userSpeed = speedDistribution[user][0] # user's *average* speed in stream
		if userCount >= countThreshold and userSpeed <= speedThreshold:
			userList.append(user)
	return userList

# Record comments of anomalous users in interesting streams
def storeAnomalousFindings(streamComments, streamer, stream, user):
	filePath = path.join(csvFindings, streamer, stream)
	if not path.exists(filePath):
		makedirs(filePath)
	fileName = path.join(filePath, user) + '.csv'
	csvWriter = csv.writer(open(fileName, 'w'), delimiter=',')
	csvWriter.writerow(['TIMESTAMP', 'COMMENT'])
	for comment in streamComments[user]:
		csvWriter.writerow([comment[0], comment[1]])


# {stream: streamer}
# {stream: {user: (commentTime, commentText}}
streamAccounts, globalComments = loadComments()

print('Processing stream:')
for streamId in globalComments:
	printLine = '   {}/{}'.format(streamAccounts[streamId], streamId)
	streamComments = globalComments[streamId]

	countDistribution = commentCountDistribution(streamComments) # {commentCount: [user...]}
	speedDistribution = commentSpeedDistribution(streamComments) # {user: (gapMean, gapRange)}

	countMean, countMedian = commentCountStats(countDistribution)
	speedMean, speedMedian = commentSpeedStats(speedDistribution)

	# a mean three times the median is our arbitrary measure for the anomalous
	if countMean >= (countMedian * significantRatio) or speedMean <= int(speedMedian / significantRatio):
		streamStats = [countMean, countMedian, speedMean, speedMedian]
		userList = anomalousUsers(streamStats, streamComments, speedDistribution)
		for userName in userList:
			storeAnomalousFindings(streamComments, streamAccounts[streamId], streamId, userName)

		printLine += ' [countMean: {}, countMedian: {}, speedMean: {}, speedMedian: {}] - {} suspicious users' \
			.format(countMean, countMedian, speedMean, speedMedian, len(userList))
	print(printLine)
