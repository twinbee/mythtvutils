#!/usr/bin/python3

from MythTV import MythDB, MythBE, Recorded, MythError
from socket import timeout
import os
import sys

def human_size(s):
    s = float(s)
    o = 0
    while s > 1000:
        s /= 1000
        o += 1
    return str(round(s, 1)) + ('B ', 'KB', 'MB', 'GB', 'TB')[o]

class File(str):
    def __new__(self, host, group, path, name, size):
        return str.__new__(self, name)
    def __init__(self, host, group, path, name, size):
        self.host = host
        self.group = group
        self.path = path
        self.size = int(size)
    def pprint(self):
        name = '%s: %s' % (self.host, os.path.join(self.path, self))
        print('  {0:<90}{1:>8}'.format(name, human_size(self.size)))
    def delete(self):
        be = MythBE(self.host, db=DB)
        be.deleteFile(self, self.group)

class MyRecorded(Recorded):
    _table = 'recorded'
    def pprint(self):
        name = '{0.hostname}: {0.title}'.format(self)
        if self.subtitle:
            name += ' - ' + self.subtitle
        print('  {0:<70}{1:>28}'.format(name, self.basename))

def printrecs(title, recs):
    print(title)
    for rec in sorted(recs, key=lambda x: x.title):
        rec.pprint()
    print('{0:>88}{1:>12}'.format('Count:', len(recs)))

def printfiles(title, files):
    print(title)
    for f in sorted(files, key=lambda x: x.path):
        f.pprint()
    size = sum([f.size for f in files])
    print('{0:>88}{1:>12}'.format('Total:', human_size(size)))

def populate(host=None):
    unfiltered = []
    kwargs = {'livetv': True}
    
    if host:
        with DB as c:
            c.execute("""SELECT count(1) FROM settings
                         WHERE hostname=%s AND value=%s""",
                      (host, 'BackendServerAddr'))
            if c.fetchone()[0] == 0:
                raise Exception('Invalid hostname specified on command line.')
        hosts = [host]
        kwargs['hostname'] = host
    else:
        with DB as c:
            c.execute("""SELECT hostname FROM settings
                         WHERE value='BackendServerAddr'""")
            hosts = [r[0] for r in c.fetchall()]
    
    # Collect all files in storage groups
    for host in hosts:
        for sg in DB.getStorageGroup():
            if sg.groupname in ('Videos', 'Banners', 'Coverart',
                                'Fanart', 'Screenshots', 'Trailers'):
                continue
            try:
                dirs, files, sizes = BE.getSGList(host, sg.groupname, sg.dirname)
                for f, s in zip(files, sizes):
                    newfile = File(host, sg.groupname, sg.dirname, f, s)
                    if newfile not in unfiltered:
                        unfiltered.append(newfile)
            except:
                pass

    recs = list(DB.searchRecorded(**kwargs))

    # Identify zero-byte recordings and orphaned videos
    zerorecs = []
    orphvids = []
    
    for rec in recs:
        if rec.basename not in unfiltered:
            orphvids.append(rec)
        else:
            i = unfiltered.index(rec.basename)
            f = unfiltered.pop(i)
            if f.size < 1024:
                zerorecs.append(rec)
    
    return (orphvids, zerorecs)

def delete_recs(recs):
    printrecs('The following recordings will be deleted', recs)
    print('Are you sure you want to continue?')
    try:
        res = input('> ')
        while True:
            if res == 'yes':
                failed_deletions = []
                batch_size = 50  # Number of recordings to delete per batch
                
                for i in range(0, len(recs), batch_size):
                    batch = recs[i:i + batch_size]
                    try:
                        BE = MythBE(db=DB)  # Reconnect to the backend for each batch
                        for rec in batch:
                            try:
                                rec.delete(True, True)
                            except MythError as e:
                                failed_deletions.append(rec)
                                print(f"Warning: Failed to delete recording '{rec.title}': {e}")
                    except MythError as e:
                        print(f"Error: Backend connection failed: {e}")
                    finally:
                        del BE  # Ensure the connection is closed after each batch
                
                print(f"Deletion complete. Failed deletions: {len(failed_deletions)}")
                break
            elif res == 'no':
                break
            else:
                res = input("'yes' or 'no' > ")
    except KeyboardInterrupt:
        pass
    except EOFError:
        sys.exit(0)



def delete_files(files):
    printfiles('The following files will be deleted', files)
    print('Are you sure you want to continue?')
    try:
        res = input('> ')
        while True:
            if res == 'yes':
                for f in files:
                    f.delete()
                break
            elif res == 'no':
                break
            else:
                res = input("'yes' or 'no' > ")
    except KeyboardInterrupt:
        pass
    except EOFError:
        sys.exit(0)

def main(host=None):
    # Populate orphaned recordings once
    orphvids, zerorecs = populate(host)

    if len(orphvids):
        printrecs("Recordings with missing files", orphvids)
    if len(zerorecs):
        printrecs("Zero byte recordings", zerorecs)

    opts = []
    if len(orphvids):
        opts.append(['Delete orphaned recording entries', delete_recs, orphvids])
    if len(zerorecs):
        opts.append(['Delete zero byte recordings', delete_recs, zerorecs])
    opts.append(['Exit', None, None])
    
    print('Please select from the following:')
    for i, opt in enumerate(opts):
        print(' {0}. {1}'.format(i + 1, opt[0]))

    try:
        inner = True
        while inner:
            res = input('> ')
            try:
                res = int(res)
            except:
                res = input('Input number. Ctrl-C to exit > ')
                continue
            if (res <= 0) or (res > len(opts)):
                res = input('Input number within range > ')
                continue
            opt = opts[res - 1]
            if opt[1] is None:
                print("Exiting...")
                break
            else:
                opt[1](opt[2])  # Call the selected delete function
                inner = False  # Exit after deletion
    except KeyboardInterrupt:
        pass
    except EOFError:
        sys.exit(0)
        
DB = MythDB()
BE = MythBE(db=DB)
DB.searchRecorded.handler = MyRecorded
DB.searchRecorded.dbclass = MyRecorded

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()

