'''
Created on Feb 19, 2011

@author: jehan
'''
from filemovers.mover import Mover
import os
import mimetypes
from filemovers import mover
import errno
import traceback

RAW_TYPES = ('nef')

class ToMoveFinalMover(Mover):
    _config = None
    def __init__(self,config):
        self._config = config
        mimetypes.init()

    def handle(self,path):
        print("ToMoveFinalMover.handle",path)
        try:
            self.realHandle(path)
        except Exception:
            print("failure handling a path")
            traceback.print_exc()

        # do some trailing work
        # TODO: FOR SOME REASON, when both jpg & raw nothing is removed !!
        # are files not moved, just copied ?
        for fold in os.listdir(self._config.move_folder):
            if 0 == len(os.listdir(os.path.join(self._config.move_folder,fold))):
                os.rmdir(os.path.join(self._config.move_folder,fold))



    def realHandle(self,path):

        foldername = os.path.basename(path)
        date = mover.parseDateFolderName(foldername)

        if None == date:
            print("ignoring file (no parsable date)")
            return

        # are there jpegs ? raws ? films ?
        # returns a dictionary: extension -> file_list
        filesByType = self.analyzeFolder(path)

        canvasPath = os.path.join(str(date.year),foldername)

        folderNames = {}
        # move files
        for (typefolder,linkfolder) in (
                                ('jpeg','to_triage'),
                                ('raw','to_develop'),
                                ('film','to_triage')):

            newfolder = self.makeNewFolderName(typefolder,canvasPath)
            folderNames[typefolder] = newfolder

            if 0 < len(filesByType[typefolder]):

                if not os.path.exists(newfolder):
                    newfolder = mover.makeDirs(newfolder)

                symlink = os.path.join(self._config.root_folder,self._config.g(('paths',typefolder)),self._config.g(('paths',linkfolder)),foldername)
                print("symlink",newfolder, symlink)

                mover.symlink( newfolder , symlink )

                for (file,subfold) in filesByType[typefolder]:
                    dir = os.path.join(newfolder,subfold)
                    if not os.path.exists(dir):
                        dir = mover.makeDirs(dir)
                    renamedFile = os.path.join(dir,os.path.basename(file))
                    print("rename",file,renamedFile)
                    mover.moveFile(file,os.path.join(newfolder,renamedFile))

        if 0 < len(filesByType['raw']):
            print("there are raws, reference output jpeg")
            outputJp = self._config.g(('paths','outputJpeg'))
            ojFolder = os.path.join(folderNames['raw'],outputJp)
            if not os.path.exists(ojFolder):
                newfolder = mover.makeDirs(ojFolder)
            if 0 == len(filesByType['jpeg']):
                print("no jpeg. symlink outputJpeg")
                # symlink outputJpeg directly as the jpeg folder if it does not exist
                mover.symlink(ojFolder, folderNames['jpeg'] )
            else:
                # symlink outputJpeg as subfolder of jpeg folder if it exists
                mover.symlink(ojFolder , os.path.join(folderNames['jpeg'],outputJp) )

        #if 0 < len(filesByType['film']):
        #    mover.symlink(folderNames['film'] , os.path.join(folderNames['jpeg'],'film') )


    def makeNewFolderName(self,typefolder,canvasPath):
        return os.path.join(self._config.root_folder,
                                         self._config.g(('paths',typefolder)),
                                         self._config.g(('paths','years')),canvasPath)

    def analyzeFolder(self,path):
        ret = {
                   'jpeg': [],
                   'raw' : [],
                   'film': [],
                   'other': []
                   }
        for root, folders, filenames in os.walk(path): #@UnusedVariable
            for f in filenames:
                currSubfolder = root[len(path)+1:]
                print(currSubfolder)
                currFile = os.path.join(root,f)
                t = mimetypes.guess_type(currFile)
                if type(t[0]) == type(""):
                    if t[0].startswith('image'):
                        basename,ext = os.path.splitext(currFile) #@UnusedVariable
                        if len(ext) >1 and ext[1:].lower() in RAW_TYPES:
                            imgType = 'raw'
                        else:
                            imgType = 'jpeg'
                    elif t[0].startswith('video'):
                        imgType = 'film'
                    else:
                        imgType = 'other'

                    ret[imgType].append((currFile,currSubfolder))
        return ret
