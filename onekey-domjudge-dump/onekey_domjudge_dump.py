#!/usr/bin/env python3
import base64
import os
import json
from time import time, sleep
import logging
import requests
import shutil

cid = 1
base_url = 'http://127.0.0.1/domjudge'
userpwd = 'admin:password'

dump_runs = True
dump_source_code = True
api_version = 'v4'
saved_dir = './data'

headers = {'Authorization': 'Basic ' +
           base64.encodebytes(userpwd.encode('utf-8')).decode('utf-8').strip()}
base_url = os.path.join(base_url, 'api', api_version, 'contests')
submissions_dir = os.path.join(saved_dir, 'submissions')


def ensure_dir(_path):
    if not os.path.exists(_path):
        os.makedirs(_path)

def urlJoin(url, *args):
    url = url.rstrip('/')

    for arg in args:
        arg = arg.strip('/')
        url = "{}/{}".format(url, arg)

    return url


def initLogging():
    global logger

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)


def requestJson(endpoint):
    url = urlJoin(base_url, str(cid))

    if len(endpoint) > 0:
        url = urlJoin(url, endpoint)

    logger.info('GET {}'.format(url))
    res = requests.get(url=url, headers=headers)
    logger.info('Result Code: {}'.format(res.status_code))

    if res.status_code != 200:
        logger.error('An error occurred during request.')
        exit()

    return res.content.decode('unicode-escape')


def requestJsonAndSave(endpoint, filename):
    text = requestJson(endpoint)

    with open(os.path.join(saved_dir, filename), 'w') as f:
        f.write(text)

    return text


def downloadSourceCodeFiles(sid):
    url = urlJoin(base_url, str(cid), 'submissions', str(sid), 'files')
    res = requests.get(url=url, headers=headers)

    if res.status_code != 200:
        logger.error('An error occurred during request GET {}'.format(url))
        exit()

    with open(os.path.join(submissions_dir, str(sid), 'files.zip'), 'wb') as f:
        f.write(res.content)


def getSourceCodeJson(sid):
    text = requestJson(urlJoin('submissions', str(sid), 'source-code'))

    with open(os.path.join(submissions_dir, str(sid), 'source-code.json'), 'w') as f:
        f.write(text)

    return text


def main():
    initLogging()

    if os.path.exists(saved_dir):
        shutil.rmtree(saved_dir)

    ensure_dir(saved_dir)

    requestJsonAndSave('', 'contest.json')
    requestJsonAndSave('awards', 'awards.json')
    requestJsonAndSave('scoreboard', 'scoreboard.json')
    requestJsonAndSave('clarifications', 'clarifications.json')
    # requestJsonAndSave('event-feed', 'event-feed.json')
    requestJsonAndSave('groups', 'groups.json')
    requestJsonAndSave('judgements', 'judgements.json')
    requestJsonAndSave('judgement-types', 'judgement-types.json')
    requestJsonAndSave('languages', 'languages.json')
    requestJsonAndSave('organizations', 'organizations.json')
    requestJsonAndSave('problems', 'problems.json')
    requestJsonAndSave('teams', 'teams.json')

    subs = json.loads(requestJsonAndSave('submissions', 'submissions.json'))

    if dump_runs:
        r = json.loads(requestJsonAndSave('runs?limit=10000', 'runs.1.json'))

        i = 2
        saved_filename = ''
        while len(r) != 0:
            endpoint = 'runs?limit=10000&first_id={}'.format(
                str(int(r[-1]['id'])+1))
            saved_filename = 'runs.{}.json'.format(str(i))

            r = json.loads(requestJsonAndSave(endpoint, saved_filename))
            i = i + 1

        os.remove(os.path.join(saved_dir, saved_filename))

    if dump_source_code:
        total = len(subs)
        i = 0

        ensure_dir(submissions_dir)

        for sub in subs:
            submission_id = sub['id']
            ensure_dir(os.path.join(submissions_dir, submission_id))

            downloadSourceCodeFiles(submission_id)
            getSourceCodeJson(submission_id)

            i = i + 1
            if i % 50 == 0:
                logging.info('Submissions {}/{}'.format(str(i), str(total)))


main()
