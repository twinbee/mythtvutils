#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#---------------------------
# Name: delete_recordings_alt.py
# Python Script
# Author: Raymond Wagner, revised by D. Hugh Redelmeier
# Modernized for Python 3 by <Your Name>
# Purpose:
#   This script provides a command-line tool to search and
#   delete recordings in MythTV.
#---------------------------

from MythTV import MythDB, MythLog
import sys

def list_recs(recs):
    print('Below is a list of matching recordings:')
    recs = dict(enumerate(recs.values()))
    for i, rec in recs.items():
        print('   %d. [%s] %s - %s' % (i, rec.starttime.isoformat(), rec.title, rec.subtitle))
    return recs

keywords = {
    'force', 'rerecord', 'yes', 'verbose',
    'title', 'subtitle', 'chanid', 'starttime', 'progstart',
    'category', 'hostname', 'autoexpire', 'commflagged',
    'stars', 'recgroup', 'playgroup', 'duplicate', 'transcoded',
    'watched', 'storagegroup', 'category', 'type',
    'airdate', 'stereo', 'subtitled', 'hdtv', 'closecaptioned',
    'partnumber', 'parttotal', 'seriesid', 'showtype', 'programid',
    'manualid', 'generic', 'cast', 'livetv', 'basename',
    'syndicatedepisodenumber', 'olderthan', 'newerthan'
}

temp = list(sys.argv[1:])
param = {}
while len(temp):
    a = temp.pop(0)
    if a[:2] != '--':
        print('not-an-option:', a)
        sys.exit(2)

    key = a[2:]

    if '=' in key:
        t = key.split('=', 1)
        key = t[0]
        value = t[1]
    elif len(temp) and temp[0][:2] != '--':
        value = temp.pop(0)
    else:
        value = ''

    if key not in keywords:
        print('unknown option:', key)
        sys.exit(3)

    if key in param:
        print('duplicated option:', key)
        sys.exit(4)

    param[key] = value

MythLog._setlevel(param.get('verbose', 'none'))
try:
    param.pop('verbose')
except KeyError:
    pass

force = False
if 'force' in param:
    force = True
    param.pop('force')

rerecord = False
if 'rerecord' in param:
    rerecord = True
    param.pop('rerecord')

yes = False
if 'yes' in param:
    yes = True
    param.pop('yes')

if not param:
    print('no selectors specified')
    sys.exit(5)

recs = list(MythDB().searchRecorded(**param))
if len(recs) == 0:
    print('no matching recordings found')
    sys.exit(6)

recs = dict(enumerate(recs))

try:
    list_recs(recs)
    while len(recs) > 0:
        if yes:
            inp = 'yes'
        else:
            inp = input("> ")

        if inp in ('help', '?'):
            print("'no' or 'n' to stop")
            print("'yes' or 'y' to confirm, and delete all")
            print("   recordings in the current list.")
            print("'list' or 'l' to reprint the list.")
            print("<int> to remove that recording from the list.")
        elif inp in ('no', 'n'):
            break
        elif inp in ('ok', 'yes', 'y'):
            for rec in recs.values():
                print('deleting', str(rec))
                rec.delete(force=force, rerecord=rerecord)
            break
        elif inp in ('list', 'l', ''):
            recs = list_recs(recs)
        else:
            try:
                recs.pop(int(inp))
            except (ValueError, KeyError):
                print('invalid input')
except KeyboardInterrupt:
    pass
except EOFError:
    pass
