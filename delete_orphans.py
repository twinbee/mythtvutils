#!/usr/bin/python3

from MythTV import MythDB, MythBE, MythError
import sys
import logging
import time

# Configure logging
logging.basicConfig(filename='delete_orphans.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def collect_orphans():
    """Collect all orphaned recordings."""
    DB = MythDB()
    BE = MythBE(db=DB)
    
    unfiltered = []
    kwargs = {'livetv': True}

    # Collect all files in storage groups
    cursor = DB.cursor()
    cursor.execute("""SELECT hostname FROM settings WHERE value='BackendServerAddr'""")
    hosts = [r[0] for r in cursor.fetchall()]

    for host in hosts:
        for sg in DB.getStorageGroup():
            if sg.groupname in ('Videos', 'Banners', 'Coverart', 'Fanart', 'Screenshots', 'Trailers'):
                continue
            try:
                result = BE.getSGList(host, sg.groupname, sg.dirname)
                if isinstance(result, tuple) and len(result) == 3:
                    dirs, files, sizes = result
                    for f in files:
                        unfiltered.append(f)
                else:
                    logging.warning(f"Failed to retrieve files from storage group '{sg.groupname}' on host '{host}'.")
            except MythError as e:
                logging.warning(f"Error retrieving storage group files for host '{host}': {e}")

    recs = list(DB.searchRecorded(**kwargs))
    orphans = [rec for rec in recs if rec.basename not in unfiltered]

    print(f"Found {len(orphans)} orphaned recordings.")
    logging.info(f"Found {len(orphans)} orphaned recordings.")
    return orphans



def delete_orphans(orphans, max_retries=3):
    """Delete orphaned recordings one by one with retry mechanism."""
    failed_deletions = []
    
    for rec in orphans:
        retries = 0
        success = False
        while retries < max_retries and not success:
            try:
                DB = MythDB()
                BE = MythBE(db=DB)
                rec.delete(force=True, rerecord=True)
                print(f"Deleted: {rec.title}")
                logging.info(f"Deleted: {rec.title}")
                success = True
            except MythError as e:
                retries += 1
                logging.warning(f"Failed to delete recording '{rec.title}' (Attempt {retries}): {e}")
                if retries < max_retries:
                    time.sleep(2)  # Wait briefly before retrying
                else:
                    failed_deletions.append(rec)
                    print(f"Warning: Failed to delete recording '{rec.title}' after {max_retries} attempts.")
                    logging.error(f"Failed to delete recording '{rec.title}' after {max_retries} attempts.")
            finally:
                del BE  # Ensure the backend connection is closed
                time.sleep(0.5)  # Add a short delay between deletions

    print(f"Deletion complete. Failed deletions: {len(failed_deletions)}")
    logging.info(f"Deletion complete. Failed deletions: {len(failed_deletions)}")
    
    if failed_deletions:
        print("The following recordings could not be deleted:")
        logging.error("The following recordings could not be deleted:")
        for rec in failed_deletions:
            print(f"  - {rec.title}")
            logging.error(f"  - {rec.title}")

def main():
    print("Collecting orphaned recordings...")
    logging.info("Starting orphaned recordings deletion process...")
    
    orphans = collect_orphans()
    
    if not orphans:
        print("No orphaned recordings found. Exiting.")
        logging.info("No orphaned recordings found. Exiting.")
        sys.exit(0)

    print("Are you sure you want to delete all orphaned recordings?")
    res = input("'yes' or 'no' > ").strip().lower()
    if res == 'yes':
        delete_orphans(orphans)
    else:
        print("Aborted by user.")
        logging.info("Process aborted by user.")
        sys.exit(0)

if __name__ == '__main__':
    main()

