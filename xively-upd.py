#!venv/bin/python
# -*- coding: utf-8 -*-

# Xively Client for Raspberry Pi and DHTxx controller
# https://xively.com/dev/tutorials/pi/
# crontab [sudo] */2 * * * * cd /PATH/TO/FILES && ./xively-upd.py > /dev/null > 2&1

import os
# import sys
import xively
# import time
import datetime
from config import *
# import subprocess
# import requests

## initialize api client
api = xively.XivelyAPIClient(XIVELY_API_KEY)

# status = 0
# if len(sys.argv) > 1:
# 	status=sys.argv[1]

__DIR__  = os.path.dirname(os.path.abspath(__file__))

cmd  = __DIR__+'/readDHT 11 4'
data = os.popen(cmd).readline().split(",")
temp = data[0].split(" ")[2]
hum  = data[1].split(" ")[3]

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed,name):
  try:
    datastream = feed.datastreams.get(name)
    return datastream
  except:
    datastream = feed.datastreams.create(name, tags=name)
    return datastream


# main program entry point - runs continuously updating our datastream with the
# latest temperature reading
def run():
	if (temp != '' and hum != ''):

		now  = datetime.datetime.utcnow()
		feed = api.feeds.get(XIVELY_FEED_ID)

		feed.datastreams = [
			xively.Datastream(id='temperature', current_value=temp, at=now),
			xively.Datastream(id='humidity', current_value=hum, at=now)
		]
		feed.update()
		# print temp, hum
run()
