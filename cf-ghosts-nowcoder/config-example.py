#!/usr/bin/env python3
import dateutil.parser

contestid = '9925'

# Your cookie (copy from HTTP Request header)
cookie = ''

start_time = dateutil.parser.parse('2020-12-13T11:00:00+08:00')
end_time = dateutil.parser.parse('2020-12-13T16:00:00+08:00')

# Used to store some intermediate data
cache_dir = './cache'

# Used to store the final product
data_dir = './data'