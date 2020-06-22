#!/usr/bin/env python
import sqlite3 as sql
import time
import os
import shutil

HOME = os.environ['HOME']
firefox_profiles_dir = '.mozilla/firefox/'
profile_name = 'default'

def parse_thefreedictionary(url):
    if len(url.split('/')) == 4:
        word = url.split('/')[-1]
        return word
    pass

hosts = [
    ('cambridge us',
     'http://dictionary.cambridge.org/us/dictionary/english/%',
     lambda url: url.split('/')[-1].split('?')[0]),
    ('cambridge',
     'http://dictionary.cambridge.org/dictionary/english/%',
     lambda url: url.split('/')[-1].split('?')[0]),
    ('thefreedictionary',
     'http://%.thefreedictionary.com/%',
     parse_thefreedictionary),
    ('dictionary',
     'http://www.dictionary.com/browse/%',
     lambda url: url.split('/')[-1].split('?')[0]),
    ('cambridge us',
     'https://dictionary.cambridge.org/us/dictionary/english/%',
     lambda url: url.split('/')[-1].split('?')[0]),
    ('cambridge',
     'https://dictionary.cambridge.org/dictionary/english/%',
     lambda url: url.split('/')[-1].split('?')[0]),
    ('thefreedictionary',
     'https://%.thefreedictionary.com/%',
     parse_thefreedictionary),
    ('dictionary',
     'https://www.dictionary.com/browse/%',
     lambda url: url.split('/')[-1].split('?')[0])]

def find_firefox_profile_path(profile_name):
    import ConfigParser
    prof_config_path = os.path.join(HOME, firefox_profiles_dir, 'profiles.ini')
    config = ConfigParser.RawConfigParser()
    config.read(prof_config_path)
    profile_path = None
    for section in config.sections():
        if not config.has_option(section, 'Name'):
            continue
    
        name = config.get(section, 'Name')
        if name == profile_name:
            sub_path = config.get(section, 'Path')
            profile_path = os.path.join(HOME, firefox_profiles_dir, sub_path)
            break
        pass
    return profile_path

profile_path = find_firefox_profile_path(profile_name)

dbpath = os.path.join(profile_path, 'places.sqlite')
now = time.time()

shutil.copyfile(dbpath, dbpath + '.tmp')

fn = dbpath + '.tmp'
conn = sql.connect(fn)
c = conn.cursor()
def do_statistic_words(c, pattern, parser):
    c.execute('select url, last_visit_date from moz_places where url like \'%s\' order by last_visit_date desc' % pattern)
    result = []
    for row in c.fetchall():
        url = row[0]
        tm = row[1]
        word = parser(url)
        if not word:
            continue
        days = (now - float(row[1]) / (10**6)) / 86400.0
        result.append((word, url, days))
        pass
    return result

result = []
for host, pattern, parser in hosts:
    host_result = do_statistic_words(c, pattern, parser)
    result.extend(host_result)
    pass
result.sort(key=lambda x: x[-1])
result = dict(reversed([(row[0], row) for row in result])).values()
result.sort(key=lambda x: x[-1])

import sys
if len(sys.argv) == 1 or sys.argv[1] == '-html':
    print '<table>'
    for word, url, days in result:
        print '  <tr><td><a href="%s">%s</a></td><td>%f</td></tr>' % (url, word, days)
        pass
    print '</table>'
    pass
elif sys.argv[1] == '-s3':
    r = ''
    for word, url, days in result:
        r = r + word.replace('-', ' ') + '\n'
        pass
    import boto3
    from botocore.exceptions import ClientError
    s3_client = boto3.client('s3')
    response = s3_client.upload_file('newwords.txt', bucket, 'newwords.txt')
    pass
else:
    for word, url, days in result:
        print '%s' % (word.replace('-', ' '))
        pass
    pass
conn.close()
os.remove(fn)
