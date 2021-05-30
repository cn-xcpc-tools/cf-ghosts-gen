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

def readJson(filename):
	with open(filename, 'r', encoding='utf-8') as f:
		return json.loads(f.read())

verdict_map = { 'CE': 'CE', 'MLE': 'ML', 'OLE': 'IL', 'RTE': 'RT', 'TLE': 'TL', 'WA': 'WA', 'PE': 'WA', 'NO': 'WA', 'AC': 'OK' }

contest = readJson('contest.json')
raw_submissions = readJson('submissions.json')
raw_teams = readJson('teams.json')
raw_judgings = readJson('judgements.json')
raw_problems = readJson('problems.json')
raw_groups = readJson('groups.json')
mapped_judgings = dict()
allowed_categories = dict()
probs = dict()
probs2 = dict()
teams = dict()
subed_team = dict()

for j in raw_judgings:
	if j['valid']:
		mapped_judgings[j['submission_id']] = j['judgement_type_id']

for c in raw_groups:
	if not c['hidden']:
		allowed_categories[c['id']] = c

for p in raw_problems:
	probs[p['label']] = p['name']
	probs2[p['id']] = p['label']

start_time = dateutil.parser.parse(contest['start_time'])
end_time = dateutil.parser.parse(contest['end_time'])

res = dict()
max_sid = 0
for s in raw_submissions:
	time = dateutil.parser.parse(s['time'])
	if time >= end_time or time < start_time:
		continue
	stat = dict()
	stat['id'] = s['id']
	stat['verdict'] = verdict_map[mapped_judgings[s['id']]]
	stat['prob'] = probs2[s['problem_id']]
	stat['time'] = int((time - start_time).seconds)
	stat['team'] = s['team_id']
	res[stat['id']] = stat
	subed_team[s['team_id']] = True
	sid2 = int(s['id'])
	if max_sid < sid2:
		max_sid = sid2

for t in raw_teams:
	hidden = True
	for g in t['group_ids']:
		if g in allowed_categories:
			hidden = False
	if hidden:
		continue
	name = t['name']
	if t['affiliation'] != None:
		name = name + ' (' + t['affiliation'] + ')'
	teams[t['id']] = name
	if not t['id'] in subed_team:
		max_sid = max_sid + 1
		res[str(max_sid)] = { 'id': str(max_sid), 'verdict': 'CE', 'prob': 'A', 'time': 99999, 'team': t['id'] }

lss = dict()
def last_submit(prob, team):
	key = prob + '_' + str(team)
	res = 1
	if key in lss:
		res = lss[key] + 1
	lss[key] = res
	return res

print('@contest "' + contest['formal_name'] + '"')
print('@contlen ' + str((end_time - start_time).seconds // 60))
print('@problems ' + str(len(probs)))
print('@teams ' + str(len(teams)))
print('@submissions ' + str(len(res)))

for p in sorted(probs.keys()):
	print('@p ' + p + ',"' + probs[p] + '",20,0')
for t in sorted(teams.keys()):
	print('@t ' + str(t) + ',0,1,"' + teams[t] + '"')
for r in sorted(res.keys()):
	res[r]['last'] = last_submit(res[r]['prob'], res[r]['team'])
	print('@s ' + str(res[r]['team']) + ',' + str(res[r]['prob']) + ',' + str(res[r]['last']) + ',' + str(res[r]['time']) + ',' + res[r]['verdict'])
