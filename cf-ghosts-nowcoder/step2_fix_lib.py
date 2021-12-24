#!/usr/bin/env python3
from nowcoder_common import *

def load_submissions_without_saving(teamId, teamName, probId, probIdx):
	subs = dict()
	args = { 'token': '', 'id': contestid, 'orderBy': 'submitTime', 'searchUserName': teamName, 'problemIdFilter': str(probId) }
	reqBase = 'acm-heavy/acm/contest/status-list?' + urllib.parse.urlencode(args)
	page = 1
	tots_with_error = 0
	while True:
		urlE = reqBase + '&orderType=ASC&page=' + str(page)
		jobj = json.loads(req(urlE))['data']
		for item in jobj['data']:
			if item['submissionId'] in subs:
				print('Error loading ' + reqBase, file=sys.stderr)
				exit(0)
			tots_with_error = tots_with_error + 1
			if item['userId'] == teamid_offset + teamId:
				subs[item['submissionId']] = item
			else:
				continue
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
			tots_with_error = tots_with_error + 1
			if item['userId'] == teamid_offset + teamId:
				subs[item['submissionId']] = item
			else:
				continue
		if jobj['basicInfo']['pageCount'] == jobj['basicInfo']['pageCurrent']:
			break
		page = page + 1
	
	print('Hi there is ' + str(tots_with_error) + ' submissions occurring this.')
	print('Team "' + teamName + '" (' + str(teamId) + ') may submitted ' + probIdx + ' for more than 400 times, ignoring this team. You may have to handle this manually later.', file=sys.stderr)
	return dict()

def load_submissions(teamName, teamId, probId, probIdx):
	subs = load_submissions_without_saving(teamId, teamName, probId, probIdx)
	with open(os.path.join(cache_dir, 'nowcoder-submissions-c' + str(contestid) + '-t' + str(teamId) + '.ndjson'), 'a', encoding='utf-8') as f:
		for t in subs:
			f.write(json.dumps(subs[t], ensure_ascii=False))
			f.write('\n')
