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
import urllib.parse
import shutil
from config import *

teamid_offset = 1030000000
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'
http = requests.Session()

if len(cookie) > 0:
	for co in cookie.split('; '):
		idx = co.index('=')
		http.cookies.set(co[:idx], co[idx+1:])

def req(url):
	headers = { 'Accept': 'application/json', 'User-Agent': useragent, 'Referer': 'https://ac.nowcoder.com/acm/contest/' + contestid }
	return http.get('https://ac.nowcoder.com/' + url, headers=headers).text

verdicts = {
	"答案正确": "OK",
	"正在判题": "CE",
	"运行错误": "RT",
	"答案错误": "WA",
	"运行超时": "TL",
	"内存超限": "ML",
	"输出超限": "IL",
	"编译错误": "CE",
	"格式错误": "WA",
	"内部错误": "RJ",
	"浮点错误": "RT",
	"段错误": "RT",
	"代码太长": "CE",
	"返回非零": "RT",
	"执行出错": "RT",
}

def ensure_dir(_path):
	if not os.path.exists(_path):
		os.makedirs(_path)
