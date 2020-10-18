'''
Created on Feb 7, 2011

@author: jehan
'''
from photosharingserver import LOCK, NewPhotos
import lockfile
import sys
from config import Config
import traceback
import os
import datetime

DEBUG = False



if __name__ == '__main__':
    print("------------------------------------------------")
    print(datetime.datetime.now(),"Starting photosharing import processing...")

    uid = os.getuid()
    if 0 != uid and False == DEBUG:
        print("You are not root.")
        sys.exit(0)

    fl = lockfile.FileLock(LOCK)
    print("trying to lock")
    while not fl.i_am_locking():
        try:
            fl.acquire(timeout=60)    # wait up to 60 seconds
        except lockfile.LockTimeout:
            print("ERROR: unable to acquire lock on ",LOCK)
            sys.exit()

    print("got lock")

    if len(sys.argv) == 2:
        configFile = sys.argv[1]
    else:
        configFile = 'config.yml'

    print("using ",os.path.abspath(configFile))
    conf = Config(configFile)

    try:
        np = NewPhotos(conf,DEBUG)
        np.process()
    except Exception as e:
        print(traceback.format_exc())
        print("We stop because of an exception.")

    print("releasing lock")
    fl.release()
    print("released. Exiting.")
    print(datetime.datetime.now(),"the end.")
    print("------------------------------------------------")
