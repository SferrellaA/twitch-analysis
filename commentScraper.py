#!/usr/bin/env python3
from subprocess import run as subprocess
from multiprocessing import Process as multiprocess
from os import path

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

# Download the comments from the last X videos from a given channel
def downloadChannelComments(channel_id, scrape_count, output_location, client_id):
    subprocess([
        'tcd',
        '--channel', channel_id,
        '--first', scrape_count,
        '--format', 'srt',
        '--output', output_location,
        '--client-id', client_id
    ])

# Scrape each channel in their own process
for channel in config['SCRAPER']['ChannelsToScrape']:
    multiprocess(
        target=downloadChannelComments,
        args=(
            channel,
            config['SCRAPER']['HowManyStreamsToScrape'],
            path.join(
                config['SCRAPER']['FolderToPutScrapedSrtComments'],
                channel
            ),
            config['SCRAPER']['TwitchClientId']
        )
    ).start()

