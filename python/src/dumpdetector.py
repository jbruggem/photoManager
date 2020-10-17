'''
Created on Feb 6, 2011

@author: jehan
'''
from __init__ import CONFIG
from config import Config
import sys
from filemovers.dumptorenamemover import DumpToRenameMover
from filemovers.detector import  FileCreationDetector

if __name__ == '__main__':
    if len(sys.argv) == 2:
        configFile = sys.argv[1]
    else:
        configFile = CONFIG
    print("using ",configFile)
    conf = Config(configFile)

    mover = DumpToRenameMover(conf)
    detector = FileCreationDetector(mover, conf.dump_folder)
    detector.start()
