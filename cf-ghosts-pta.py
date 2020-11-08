#!/usr/bin/env python3
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

contestid = '1216205439967371264' # problem-set/{this id}/...
lolipop = '7ec135f9c4950066a0db180b8022592d' # look at the request header?
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'
cookie = # Your cookie (copy from HTTP Request header)
start_time = dateutil.parser.parse('2020-01-13T13:30:00+08:00')
http = requests.Session()

verdicts = { "WRONG_ANSWER": "WA", "SEGMENTATION_FAULT": "RT", "PRESENTATION_ERROR": "WA", "COMPILE_ERROR": "CE", "ACCEPTED": "OK", "TIME_LIMIT_EXCEEDED": "TL", "OUTPUT_LIMIT_EXCEEDED": "RJ", "FLOAT_POINT_EXCEPTION": "RT", "NON_ZERO_EXIT_CODE": "RT", "MEMORY_LIMIT_EXCEEDED": "ML", "RUNTIME_ERROR": "RT", "INTERNAL_ERROR": "RJ" };

for co in cookie.split('; '):
	idx = co.index('=')
	http.cookies.set(co[:idx], co[idx+1:])

res = dict()
teams = dict()
teams2 = dict()
probs = dict()

def get_team_id(ro):
	teamId = '0'
	if 'studentUser' in ro:
		user = ro['studentUser']
		if not user['studentNumber'] in teams2:
			teamId = len(teams)+1
			teams[teamId] = user['name']
			teams2[user['studentNumber']] = teamId
		else:
			teamId = teams2[user['studentNumber']]
	elif 'user' in ro:
		user = ro['user']
		if not user['id'] in teams2:
			teamId = len(teams)+1
			teams[teamId] = user['nickname']
			teams2[user['id']] = teamId
		else:
			teamId = teams2[user['id']]
	return teamId

def get_prob_id(ro):
	label = '?'
	if '7-' in ro['label']:
		label = chr(ord('A')+int(ro['label'].split('-')[1])-1)
	else:
		label = ro['label']
	probs[label] = ro
	return label

after = '1'
while True:
	sleep(0.25)
	headers = { 'Accept': 'application/json', 'User-Agent': useragent, 'X-Lolipop': lolipop, 'X-Marshmallow': '', 'Referer': 'https://pintia.cn/problem-sets/' + contestid + '/submissions?after=' + after }
	resp = http.get('https://pintia.cn/api/problem-sets/' + contestid + '/submissions?show_all=true&after=' + after + '&limit=100&filter=%7B%7D', headers=headers)
	jobj = json.loads(resp.text)
	
	for submission in jobj['submissions']:
		#print(submission)
		if submission['id'] > after:
			after = submission['id']

		if submission['problemType'] != 'PROGRAMMING':
			continue
		
		stat = dict()
		stat['id'] = submission['id']
		if submission['status'] == 'INTERNAL_ERROR':
			print('Hello, verdict of s' + submission['id'] + ' is INTERNAL_ERROR', file=sys.stderr)
		stat['verdict'] = verdicts[submission['status']]
		stat['prob'] = get_prob_id(submission['problemSetProblem'])
		stat['time'] = (dateutil.parser.parse(submission['submitAt']) - start_time).seconds
		stat['team'] = get_team_id(submission['user'])
		res[stat['id']] = stat
	
	print('after = ' + after, file=sys.stderr)
	if jobj['hasAfter'] == False:
		break
	#break

lss = dict()
def last_submit(prob, team):
	key = prob + '_' + str(team)
	res = 1
	if key in lss:
		res = lss[key] + 1
	lss[key] = res
	return res

print('@contest "CONTEST NAME"')
print('@contlen 300')
print('@problems ' + str(len(probs)))
print('@teams ' + str(len(teams)))
print('@submissions ' + str(len(res)))

for p in sorted(probs.keys()):
	print('@p ' + p + ',TITLE,20,0')
for t in sorted(teams.keys()):
	print('@t ' + str(t) + ',0,1,' + teams[t])
for r in sorted(res.keys()):
	res[r]['last'] = last_submit(res[r]['prob'], res[r]['team'])
	print('@s ' + str(res[r]['team']) + ',' + str(res[r]['prob']) + ',' + str(res[r]['last']) + ',' + str(res[r]['time']) + ',' + res[r]['verdict'])
