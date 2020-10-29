#!/usr/bin/env python3
import os
import re
import json
from time import time, sleep
import logging
from logging import debug, info, warning, error, critical
import urllib3
import requests
import dateutil.parser

username = 'guest'
password = 'guest'
contestid = '930'
start_time = dateutil.parser.parse('2020-10-11 09:00:00')

def login():
	http = requests.Session()
	http.get('http://acm.hdu.edu.cn/contests/contest_show.php?cid=' + contestid)
	head = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Connection': 'close', 'Referer': 'http://acm.hdu.edu.cn/userloginex.php?cid=' + contestid }
	form = 'login=Sign%20In&username=' + username + '&userpass=' + password
	http.post('http://acm.hdu.edu.cn/userloginex.php?action=login&cid=' + contestid + '&notice=0', data=form, headers=head)
	return http

def my_parse_team(teamname):
	# should return id, "team name"
	# team137   普通高校 <br> TEAM NAME <br> SCHOOL
	secs = teamname.split('<br>')
	teamidd = secs[0].strip().split(' ')[0]
	if not teamidd.startswith('team'):
		return -1, ''
	teamid = int(teamidd.replace('team', ''))-1
	school = secs[2].strip()
	name = secs[1].strip()
	isStar = '' if secs[0].find('打星') < 0 else '*'
	#teamid = int(secs[0].strip().replace('team', ''))-1
	#school = secs[2].strip()
	#name = secs[1].replace('正式', '').replace('* ', '').strip()
	#isStar = '' if secs[1].endswith('正式 ') else '*'
	return teamid, name + isStar + ' ' + school

def parse_team(line):
	# get the team name
	return my_parse_team(line.split('"')[1])

def parse_teams(content):
	teams = content.split('pr(')
	teams = teams[2:]
	val = dict()
	for t in teams:
		id, name = parse_team(t)
		if id >= 0:
			val[id] = name
	return ['@t ' + str(k) + ',0,1,' + val[k] for k in sorted(val.keys())]

def parse_probs(content):
	l = content.split('<td><a href="/contests/contest_showproblem.php?')[1:]
	return ['@p ' + chr(ord('A')+k) + ',TITLE,20,0' for k in range(len(l))]

def parse_verdict(content):
	if content.find("Accepted") >= 0:
		return "OK"
	elif content.find("Wrong Answer") >= 0:
		return "WA"
	elif content.find("Time Limit Exceeded") >= 0:
		return "TL"
	elif content.find("Memory Limit Exceeded") >= 0:
		return "ML"
	elif content.find("Output Limit Exceeded") >= 0:
		return "IL"
	elif content.find("Presentation Error") >= 0:
		return "PE"
	elif content.find("Runtime Error") >= 0:
		return "RT"
	elif content.find("Compilation Error") >= 0:
		return "CE"
	else:
		return "RJ"

used_teams = dict()
def parse_runs(runs, page_content):
	page_content = page_content.split('<div align="center" class="FOOTER_LINK">')[0]
	items = page_content.split('<td height=22>')[1:]
	for item in items:
		cols = item.split('</td><td')
		stat = dict()
		stat['id'] = int(cols[0])
		stat['verdict'] = parse_verdict(cols[2])
		stat['prob'] = str(chr(int(cols[3].split('&pid=')[1].split('" title=')[0])-1001+ord('A')))
		stat['time'] = (dateutil.parser.parse(cols[1].split('>')[1]) - start_time).seconds
		stat['team'] = int(cols[7].split('team')[1][0:3])-1
		used_teams[stat['team']] = True
		runs[stat['id']] = stat

lss = dict()
def last_submit(prob, team):
	key = prob + str(team)
	res = 1
	if key in lss:
		res = lss[key] + 1
	lss[key] = res
	return res

http = login()
print('@contest "CONTEST NAME"')
print('@contlen 300')

fake = http.get('http://acm.hdu.edu.cn/contests/client_ranklist.php?cid=' + contestid).text

probs = parse_probs(fake)
print('@problems ' + str(len(probs)))
teams = parse_teams(fake)
print('@teams ' + str(len(teams)))

res = dict()
page = 1
while True:
	what = http.get('http://acm.hdu.edu.cn/contests/contest_status.php?cid=' + contestid + '&pid=&user=&lang=&status=&page=' + str(page))
	parse_runs(res, what.text)
	if (1 in res):
		break
	page = page + 1

for i in range(0, len(teams)):
	if not i in used_teams:
		stat = dict()
		stat['id'] = len(res) + 1
		stat['verdict'] = 'CE'
		stat['prob'] = 'A'
		stat['time'] = 99999
		stat['team'] = i
		res[stat['id']] = stat

print('@submissions ' + str(len(res)))

for p in probs:
	print(p)
for t in teams:
	print(t)
for r in sorted(res.keys()):
	res[r]['last'] = last_submit(res[r]['prob'], res[r]['team'])
	print('@s ' + str(res[r]['team']) + ',' + str(res[r]['prob']) + ',' + str(res[r]['last']) + ',' + str(res[r]['time']) + ',' + res[r]['verdict'])
