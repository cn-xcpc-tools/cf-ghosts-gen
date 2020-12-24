#!/usr/bin/env python3
from nowcoder_common import *
from datetime import datetime
import pytz

teams = dict()
probs = dict()
subs = dict()

with open('nowcoder-teams-c' + str(contestid) + '.ndjson', 'r', encoding='utf-8') as f:
	while True:
		line = f.readline()
		if not line:
			break
		jobj = json.loads(line)
		teams[jobj['uid']] = jobj

with open('nowcoder-probs-c' + str(contestid) + '.ndjson', 'r', encoding='utf-8') as f:
	while True:
		line = f.readline()
		if not line:
			break
		jobj = json.loads(line)
		probs[jobj['index']] = jobj

for teamId in teams:
	with open('nowcoder-submissions-c' + str(contestid) + '-t' + str(teamId) + '.ndjson', 'r', encoding='utf-8') as f:
		while True:
			line = f.readline()
			if not line:
				break
			jobj = json.loads(line)
			subTime = datetime.fromtimestamp(jobj['submitTime'] / 1000.0).replace(tzinfo=start_time.tzinfo)
			if subTime < end_time:
				jobj['submitRelativeTime'] = int((subTime - start_time).seconds)
				subs[jobj['submissionId']] = jobj

print('@contest "CONTEST NAME"')
print('@contlen 300')
print('@problems ' + str(len(probs)))
print('@teams ' + str(len(teams)))
print('@submissions ' + str(len(subs)))

for p in sorted(probs.keys()):
	print('@p ' + p + ',' + probs[p]['title'] + ',20,0')
for t in sorted(teams.keys()):
	print('@t ' + str(t) + ',0,1,' + teams[t]['userName'])

lss = dict()
def last_submit(prob, team):
	key = prob + '_' + str(team)
	res = 1
	if key in lss:
		res = lss[key] + 1
	lss[key] = res
	return res

for r in sorted(subs.keys()):
	sub = subs[r]
	team = sub['userId'] - teamid_offset
	prob = sub['index']
	last = last_submit(prob, team)
	verdcit = verdicts[sub['statusMessage']]
	print('@s ' + str(team) + ',' + prob + ',' + str(last) + ',' + str(sub['submitRelativeTime']) + ',' + verdcit)
