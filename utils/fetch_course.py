import json

import time
import requests
import urllib.parse
from utils.logger import *

session = requests.Session()
session.headers = {'Accept': 'application/json'}

async def fetch_course_datas(serials):
    hostname = r'https://api.simon.chummydns.com/api/search?dept='
    data = []

    all_start = time.time()
    for dept in serials.keys():
        start = time.time()
        print('Fetching {}...'.format(dept), end='\t')

        query = str(dept)

        query = urllib.parse.quote(query, safe=',')

        url = hostname + query

        while True:
            try:
                r = session.get(url)
            except requests.exceptions.ConnectTimeout:
                print('Connection timed out!')
                return {}
            except requests.exceptions.ConnectionError:
                print('Connection Error')
                return {}

            try:
                r_json = r.json()
            except requests.exceptions.JSONDecodeError:
                print('Requests got non-json file')
                return {}
                
            if r_json['success'] is True:
                break
            else:
                print('Failed to fetch data, retrying...')

        try:
            data += r.json()['data']
        except Exception as err:
            print('Failed to load JSON ' + str(err))
            return {}

        end = time.time()
        print('in {:.3f} secs'.format(end - start))
    all_end = time.time()
    print('{:.3f} secs in total\n'.format(all_end - all_start))

    ret = {}
    for course in data:
        sn = course['sn']
        if sn is None:
            continue
        ret[sn] = {
            'cn': course['cn'],
            'i': course['i'],
            't': course['t'],
            'a': course['a'],
        }
    return ret


async def update(old_data, serials):
    new_data = await fetch_course_datas(serials)
    updated_courses = []
    for sn in new_data.keys():
        if sn not in old_data:
            continue

        if old_data[sn]['a'] != new_data[sn]['a']:
            updated_courses.append(sn)
    return new_data, updated_courses
