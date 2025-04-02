#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# ---------------------------
# Name: delete_recordings.py
# Python Script
# Author: Raymond Wagner (Updated for Python 3 by Matthew Bee)
# Purpose:
#   This python script provides a command line tool to search and
#   delete recordings.
# ---------------------------

from MythTV import MythDB, MythLog
import sys

def list_recs(recs):
    print('Below is a list of matching recordings:')
    recs = dict(enumerate(recs.values()))
    for i, rec in recs.items():
        print('  {}. [{}] {} - {}'.format(
            i, rec.starttime.isoformat(), rec.title, rec.subtitle))
    return recs

param = {}

temp = list(sys.argv[1:])
while len(temp):
    a = temp.pop(0)
    if a[:2] == '--':
        a = a[2:]
        if '=' in a:
            a = a.split('=', 1)
            param[a[0]] = a[1]
        else:
            if len(temp):
                b = temp.pop(0)
                if (b[:2] == '--') or (b[:1] == '-'):
                    temp.insert(0, b)
                    param[a] = ''
                else:
                    param[a] = b
            else:
                param[a] = ''

MythLog._setlevel(param.get('verbose', 'none'))
param.pop('verbose', None)

force = False
if 'force' in param:
    force = True
    param.pop('force')

if not param:
    sys.exit(0)

recs = list(MythDB().searchRecorded(**param))
if len(recs) == 0:
    print('No matching recordings found')
    sys.exit(0)

if force:
    for rec in recs:
        # Uncomment the next line for logging deleted recordings
        # print('Deleting', str(rec))
        rec.delete()
    sys.exit(0)

recs = dict(enumerate(recs))

try:
    list_recs(recs)
    while len(recs) > 0:
        inp = input("> ")
        if inp == 'help':
            print("'ok' or 'yes' to confirm, and delete all")
            print("     recordings in the current list.")
            print("'list' to reprint the list.")
            print("<int> to remove that recording from the list.")
        elif inp in ('yes', 'ok'):
            for rec in recs.values():
                # Uncomment the next line for logging deleted recordings
                # print('Deleting', str(rec))
                rec.delete()
            break
        elif inp in ('list', ''):
            recs = list_recs(recs)
        else:
            try:
                recs.pop(int(inp))
            except:
                print('Invalid input')
except KeyboardInterrupt:
    pass
except EOFError:
    pass
