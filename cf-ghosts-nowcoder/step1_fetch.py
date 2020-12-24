#!/usr/bin/env python3
from nowcoder_common import *

def load_probs():
	ret_probs = dict()
	jobj = json.loads(req('acm/contest/problem-list?token=&id=' + contestid + '&page=1&pageSize=100'))
	probs = jobj['data']['data']
	for prob in probs:
		ret_probs[prob['index']] = { 'title': prob['title'], 'problemId': prob['problemId'], 'index': prob['index'] }
	return ret_probs

def load_teams():
	page = 1
	ret_teams = dict()
	while True:
		resp = req('acm-heavy/acm/contest/real-time-rank-data?token=&id=' + contestid + '&page=' + str(page) + '&limit=0')
		jobj = json.loads(resp)['data']
		for rank in jobj['rankData']:
			uid = rank['uid'] - teamid_offset
			if 'school' in rank:
				school = rank['school']
				user = rank['userName']
				team = school + ' ' + user
			else:
				team = rank['userName']
				user = team
				print('Warning: ' + str(uid) + ' doesn\'t belong to a school.', file=sys.stderr)
			ret_teams[uid] = { 'team': team, 'userName': user, 'uid': uid }
		if jobj['basicInfo']['pageCount'] == jobj['basicInfo']['pageCurrent']:
			break
		page = page + 1
	return ret_teams

def notice_fix_run(teamId, teamName, probId, probIdx):
	with open('step2_run.py', 'a', encoding='utf-8') as f:
		f.write('load_submissions(' + json.dumps(teamName, ensure_ascii=False) + ',' + str(teamId) + ',' + str(probId) + ',\'' + probIdx + '\')')
		f.write('\n')

def load_submissions(teamId, teamName, probId, probIdx):
	subs = dict()
	args = { 'token': '', 'id': contestid, 'orderBy': 'submitTime', 'searchUserName': teamName, 'problemIdFilter': str(probId) }
	reqBase = 'acm-heavy/acm/contest/status-list?' + urllib.parse.urlencode(args)
	page = 1
	while True:
		urlE = reqBase + '&orderType=ASC&page=' + str(page)
		jobj = json.loads(req(urlE))['data']
		for item in jobj['data']:
			if item['submissionId'] in subs:
				print('Error loading ' + reqBase, file=sys.stderr)
				exit(0)
			if item['userId'] == teamid_offset + teamId:
				subs[item['submissionId']] = item
			else:
				print('Warning loading team "' + teamName + '" (' + str(teamId) + ') at problem ' + probIdx + ', search may failed.', file=sys.stderr)
				notice_fix_run(teamId, teamName, probId, probIdx)
				return dict()
		if jobj['basicInfo']['pageCount'] <= jobj['basicInfo']['pageCurrent']:
			break
		page = page + 1
	if len(subs) < 200:
		return subs
	page = 1
	while True:
		urlE = reqBase + '&orderType=DESC&page=' + str(page)
		jobj = json.loads(req(urlE))['data']
		for item in jobj['data']:
			if item['submissionId'] in subs:
				# fetchOver
				return subs
			if item['userId'] == teamid_offset + teamId:
				subs[item['submissionId']] = item
			else:
				print('Warning loading team "' + teamName + '" (' + str(teamId) + '), search may failed.', file=sys.stderr)
				notice_fix_run(teamId, teamName, probId, probIdx)
				return dict()
		if jobj['basicInfo']['pageCount'] == jobj['basicInfo']['pageCurrent']:
			break
		page = page + 1
	print('Team "' + teamName + '" (' + str(teamId) + ') may submitted ' + probIdx + ' for more than 400 times, ignoring this team. You may have to handle this manually later.', file=sys.stderr)
	notice_fix_run(teamId, teamName, probId, probIdx)
	return dict()

probs = load_probs()
teams = load_teams()

with open('nowcoder-teams-c' + str(contestid) + '.ndjson', 'w', encoding='utf-8') as f:
	for t in teams:
		f.write(json.dumps(teams[t], ensure_ascii=False))
		f.write('\n')

with open('nowcoder-probs-c' + str(contestid) + '.ndjson', 'w', encoding='utf-8') as f:
	for t in probs:
		f.write(json.dumps(probs[t], ensure_ascii=False))
		f.write('\n')

with open('step2_run.py', 'w', encoding='utf-8') as f:
	f.write('#!/usr/bin/env python3\n')
	f.write('from nowcoder_common import *\n')
	f.write('from step2_fix_lib import *\n\n\n')

subs = dict()
prog = 1
totprog = len(teams)
for teamId in teams:
	for probIdx in probs:
		s = load_submissions(teamId, teams[teamId]['userName'], probs[probIdx]['problemId'], probIdx)
		#print(teams[teamId]['userName'] + ' and ' + probIdx + ' loaded ' + str(len(s)) + ' items')
		subs.update(s)
	if prog % 10 == 1:
		print('progress: ' + str(prog) + ' / ' + str(totprog), file=sys.stderr)
	prog = prog + 1
	with open('nowcoder-submissions-c' + str(contestid) + '-t' + str(teamId) + '.ndjson', 'w', encoding='utf-8') as f:
		for t in subs:
			f.write(json.dumps(subs[t], ensure_ascii=False))
			f.write('\n')
	subs = dict()

print('total ' + str(len(subs)) + ' submissions', file=sys.stderr)
print('Please handle the errors and run cf-ghost-nowcoder-post.py', file=sys.stderr)
