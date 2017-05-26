#!/usr/bin/env python

##
##  Copyright 2016 SRI International
##  See COPYING file distributed along with the package for the copyright and license terms
##
import os
import sys
import sibispy
from sibispy import sibislogger as slog

timeLogFile = '/tmp/test_session-time_log.csv'
if os.path.isfile(timeLogFile) : 
    os.remove(timeLogFile) 

slog.init_log(False, False,'test_session', 'test_session','/tmp')


path = os.path.join(os.path.dirname(sys.argv[0]), 'data', '.sibis-general-config.yml')

def test_session_init_path():
    # setting explicitly
    session = sibispy.Session()
    assert(session.configure(config_file=path))
    assert(session.config_file == path)

test_session_init_path()

# Test when variable is set 
os.environ.update(SIBIS_CONFIG=path)
session = sibispy.Session()
assert(session.configure())
os.environ.pop('SIBIS_CONFIG')
assert(session.config_file == path)

for project in ['xnat', 'data_entry','redcap_mysql_db'] :
    if not session.connect_server(project, True):
        print "Info: Make sure " + project + " is correctly defined in " + path 
        sys.exit(1)

print "Info: Time log writen to " + timeLogFile 


