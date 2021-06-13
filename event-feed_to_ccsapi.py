#!/usr/bin/env python3
import base64
import os
import re
import json
import sys
from time import time, sleep
import logging
from logging import debug, info, warning, error, critical
import urllib3
import requests
import dateutil.parser

events = []
with open('event-feed.json', 'r') as f:
	lines = f.read().split('\n')
	for line in lines:
		if line.strip() != '':
			events.append(json.loads(line))

endpoints = dict()

for event in events:
	if event['type'] == 'state':
		continue
	if not event['type'] in endpoints:
		endpoints[event['type']] = dict()
	ep = endpoints[event['type']]
	if event['op'] == 'delete':
		del ep[event['data']['id']]
	else:
		ep[event['data']['id']] = event['data']

if len(endpoints['contests']) != 1:
	print('???? Why there`s many contests?')
else:
	with open('contest.json', 'w') as f:
		f.write(json.dumps(list(endpoints['contests'].values())[0]))
	del endpoints['contests']

for type in endpoints:
	with open(type + '.json', 'w') as f:
		f.write(json.dumps(list(endpoints[type].values())))
