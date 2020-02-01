#!/usr/bin/env python3
import csv
from os import path, listdir, makedirs

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

''' 
1
00:00:16,536 --> 00:00:18,536
UserName: comment text

'''

# Reformat a particular .srt to a .csv file
def reformatSrt(srtName, csvName):
	srtFile = open(srtName, 'r')
	csvFile = csv.writer(open(csvName, 'w'), delimiter=',')
	csvFile.writerow(['ID', 'TIME', 'USER', 'TEXT'])
	while True:
		firstLine = srtFile.readline()
		if firstLine == '':
			srtFile.close()
			break
		ID = firstLine[:-1]
		TIME = srtFile.readline().split()[0]
		thirdLine = srtFile.readline().split(': ', 1)
		USER = thirdLine[0]
		TEXT = thirdLine[1][:-1]
		srtFile.readline()
		csvFile.writerow([ID, TIME, USER, TEXT])

# Get the name of the csv file to write to
def getCsvName(channel, srtFile):
	folder = path.join(
		config['REFACTOR']['FolderToPutReformattedCsvComments'],
		channel
	)
	if not path.exists(folder):
		makedirs(folder)
	csvName = srtFile[:-3] + 'csv'
	return path.join(folder, csvName)

# Iterate over the srt files
srtComments = config['SCRAPER']['FolderToPutScrapedSrtComments']
for channel in listdir(srtComments):
	channelFolder = path.join(srtComments, channel)
	if not path.isdir(channelFolder):
		continue
	print('Converting ' + channel + ':')
	for srtFile in listdir(channelFolder):
		if not srtFile.endswith('.srt'):
			continue
		print('   ' + srtFile)
		srtName = path.join(channelFolder, srtFile)
		csvName = getCsvName(channel, srtFile)
		reformatSrt(srtName, csvName)
