'''
Created on Jan 31, 2011

@author: jehan
'''
import pyinotify
import os
import traceback


class Detector(pyinotify.ProcessEvent):
    _notifier = None
    _folder = None
    _watchManager = None
    _mask = pyinotify.ALL_EVENTS
    _recursive = True
    _auto_add = True

    def __init__(self,handler,folder):
        self._handler = handler
        self._folder = folder

        self._watchManager = pyinotify.WatchManager()
        self._notifier = pyinotify.Notifier(self._watchManager,self)

        print "following ",self._folder
        print "set up:", self._mask,",rec:",self._recursive,",auto_add:",self._auto_add
        self._watchManager.add_watch(self._folder, self._mask, rec=self._recursive, auto_add=self._auto_add)

    def start(self):
        print "start notifier loop"
        self._notifier.loop()
        print "done"

    def __getattribute__(self,name):
        #print "call to ",name
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if name.startswith('process_'):
                #print "process handling"
                return self. realProcess
            else:
                #print "super"
                super(Detector,self). __getattribute__(name)

    def realProcess(self,event):
        print "Event!"
        print event.mask,event.maskname,event.path,event.pathname

class RootFoldersDetector(Detector):
    _mask = pyinotify.IN_ISDIR | pyinotify.IN_ACCESS| pyinotify.IN_ATTRIB|  pyinotify.IN_MOVED_TO #@UndefinedVariable
    _recursive = False
    _auto_add = False

    def realProcess(self,event):
        print "event:",event.maskname,event.pathname
        if event.mask & pyinotify.IN_ISDIR: #@UndefinedVariable
            relpath = os.path.relpath(event.pathname,self._folder)
            if '.' != relpath:
                self._handler.handle(event.pathname)
        else:
            print "ignore not dir"

class FileCreationDetector(pyinotify.ProcessEvent):
    _notifier = None
    _handler = None
    _folder = None

    def __init__(self,handler,folder):
        self._handler = handler
        self._folder = folder

        self._watchManager = pyinotify.WatchManager()
        self._notifier = pyinotify.Notifier(self._watchManager,self)

        print "following ",self._folder
        mask = pyinotify.IN_CREATE |pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO | pyinotify.IN_CLOSE_WRITE #@UndefinedVariable  #pyinotify.IN_CREATE |pyinotify.IN_MODIFY |
        self._watchManager.add_watch(self._folder, mask, rec=True, auto_add=True)



    def start(self):
        print "start notifier loop"
        self._notifier.loop()
        print "done"

    def process_IN_CLOSE_WRITE(self,event):
        print "close write",event.pathname
        self._handler.handleFile(event.pathname)
        print "end process catch"

    def process_IN_CREATE(self,event):
        print "create",event.pathname
#        self.handle(event.pathname)
        print "end process catch"

    def process_IN_MODIFY(self,event):
        print "modify",event.pathname
#        self.handle(event.pathname)
        print "end process catch"

    def process_IN_MOVED_TO(self,event):
        print "moved",event.pathname
        self.handle(event.pathname)
        print "end process catch"

    def handle(self,path):
        print "handle",path
        if os.path.isfile(path):
            print "call handle file"
            self._handler.handleFile(path)
        else:
            print "walk"
            for dirname, dirnames, filenames in os.walk(path): #@UnusedVariable
                print "walk iteration ", dirname
                for filename in filenames:
                    try:
                        self._handler.handleFile(os.path.join(dirname, filename))
                    except Exception:
                        print "ERROR: failed to handle "+filename
                        traceback.print_exc()
        print "end handle ",path
