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

def requestJson(endpoint):
	with open(endpoint + '.json', 'r') as f:
		return json.loads(f.read())

endpoints_to_read = ['judgement-types','languages','groups','organizations','problems','teams']
endpoints_to_read_2 = ['clarifications','judgements','submissions']

lines = []
eventid = 0
def appendEvent(type, op, data):
	global eventid
	eventid = eventid + 1
	lines.append(json.dumps({"id":str(eventid),"type":type,"op":op,"data":data}))

contest = requestJson("contest")
appendEvent("contests", "create", contest)
for ep in endpoints_to_read:
	entries = requestJson(ep)
	for entry in entries:
		appendEvent(ep, "create", entry)

timed_events = []
for ep in endpoints_to_read_2:
	entries = requestJson(ep)
	for entry in entries:
		timed_events.append({"type":ep,"op":"create","data":entry,"time":dateutil.parser.parse(entry['time' if ep != 'judgements' else 'end_time'])})

state = {
	"started": None,
	"frozen": None,
	"ended": None,
	"thawed": None,
	"finalized": None,
	"end_of_updates": None
}

state_time = dateutil.parser.parse(contest['start_time'])
state['started'] = state_time.isoformat(timespec='milliseconds')
timed_events.append({"type":"state","op":"update","data":state.copy(),"time":state_time})

state_time = state_time + (dateutil.parser.parse(contest['duration']) - dateutil.parser.parse(contest['scoreboard_freeze_duration']))
state['frozen'] = state_time.isoformat(timespec='milliseconds')
timed_events.append({"type":"state","op":"update","data":state.copy(),"time":state_time})

state_time = state_time + (dateutil.parser.parse(contest['scoreboard_freeze_duration']) - dateutil.parser.parse('0:00:00.000'))
state['ended'] = state_time.isoformat(timespec='milliseconds')
timed_events.append({"type":"state","op":"update","data":state.copy(),"time":state_time})

state_time = state_time + (dateutil.parser.parse('1:00:00.000') - dateutil.parser.parse('0:00:00.000'))
state['thawed'] = state_time.isoformat(timespec='milliseconds')
timed_events.append({"type":"state","op":"update","data":state.copy(),"time":state_time})

state_time = state_time + (dateutil.parser.parse('1:00:00.000') - dateutil.parser.parse('0:00:00.000'))
state['finalized'] = state_time.isoformat(timespec='milliseconds')
timed_events.append({"type":"state","op":"update","data":state.copy(),"time":state_time})

for timed_event in sorted(timed_events, key=lambda x: x['time']):
	appendEvent(timed_event['type'], timed_event['op'], timed_event['data'])

with open('event-feed.json', 'w') as f:
	for line in lines:
		f.write(line + '\n')
