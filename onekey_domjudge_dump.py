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

cid = 6
dump_zips = True
dump_runs = True
base_url = 'http://172.11.13.2/domjudge'
userpwd = 'admin:oBh6AO89tnfTOFwx'
headers = { 'Authorization': 'Basic ' + base64.encodebytes(userpwd.encode('utf-8')).decode('utf-8').strip() }

def requestJson(endpoint):
	url = base_url + '/api/contests/' + str(cid) + '/' + endpoint
	print('GET ' + url + ' ...',end='')
	res = requests.get(url=url, headers=headers)
	print(res.status_code)
	if res.status_code != 200:
		print('An error occurred during request.')
		exit()
	return res.text

def downloadZip(sid):
	url = base_url + '/api/contests/' + str(cid) + '/submissions/' + str(sid) + '/files'
	res = requests.get(url=url, headers=headers)
	if res.status_code != 200:
		print('An error occurred during request GET ' + url)
		exit()
	with open('submissions/' + str(sid) + '.zip', 'wb') as f:
		f.write(res.content)

def requestJsonAndSave(endpoint, filename):
	text = requestJson(endpoint)
	with open(filename, 'w') as f:
		f.write(text)
	return text

requestJsonAndSave('', 'contest.json')
requestJsonAndSave('groups', 'groups.json')
requestJsonAndSave('clarifications', 'clarifications.json')
requestJsonAndSave('judgement-types', 'judgement-types.json')
requestJsonAndSave('languages', 'languages.json')
requestJsonAndSave('organizations', 'organizations.json')
requestJsonAndSave('problems', 'problems.json')
requestJsonAndSave('teams', 'teams.json')
requestJsonAndSave('scoreboard', 'scoreboard.json')
subs = json.loads(requestJsonAndSave('submissions', 'submissions.json'))
requestJsonAndSave('judgements', 'judgements.json')

if dump_runs:
	r = json.loads(requestJsonAndSave('runs?limit=10000', 'runs.1.json'))
	i = 2
	while len(r) != 0:
		r = json.loads(requestJsonAndSave('runs?limit=10000&first_id=' + str(int(r[-1]['id'])+1), 'runs.' + str(i) + '.json'))
		i = i + 1

if dump_zips:
	total = len(subs)
	i = 0
	if not os.path.exists('submissions'):
		os.mkdir('submissions')
	for sub in subs:
		downloadZip(sub['id'])
		i = i + 1
		if i % 50 == 0:
			print('Submissions: ' + str(i) + ' / ' + str(total))
