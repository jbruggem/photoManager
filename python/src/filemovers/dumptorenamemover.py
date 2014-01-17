'''
Created on Feb 6, 2011

@author: jehan
'''


import pyexiv2
import mimetypes
from filemovers import mover
from filemovers.mover import Mover
import os, re
import datetime



class DumpToRenameMover(Mover):
    _config = None
    def __init__(self,config):
        self._config = config
        mimetypes.init()
    

    def handleFile(self,handledFilePath):
        print "handleFile", handledFilePath
        
        # extract the date of the file
        imgDatetime = self.getImageDate(handledFilePath)
        
        # no date? Ignore the file.
        if None != imgDatetime:
            print "Handling",os.path.basename(handledFilePath),imgDatetime
            dateFolderPath = self.makeFolder(imgDatetime, handledFilePath)
            mover.moveFile(handledFilePath,
                           os.path.join(dateFolderPath,os.path.basename(handledFilePath)))
        
        # do some trailing work
#        for root,folders,files in os.walk(self._config.dump_folder): #@UnusedVariable
#            for fold in folders:
#                if 0 == len(os.listdir(os.path.join(root,fold))):
#                    os.rmdir(os.path.join(root,fold))
                

    def makeFolder(self, imgDatetime, handledFilePath):
        print "making a new folder"
        dateFolders = mover.findDateFolders(self._config.rename_folder)
         
        if dateFolders.has_key(mover.mkDateFolderName(imgDatetime)):
            print "folder exists"
            dateFolderPath = dateFolders[mover.mkDateFolderName(imgDatetime)][1]
        else:
            print "creating new folder"
            # make dir if it does not exist
            dateFolderPath = os.path.join(self._config.rename_folder,
                                   mover.mkDateFolderName(imgDatetime))
                                   
            if self._config.use_original_folder_names:
                print "import original folder name"
                originalFolderName =  os.path.basename(os.path.dirname(handledFilePath))
                dateFolderPath += ' '+ originalFolderName
            print "make dir",dateFolderPath
            
            os.mkdir( dateFolderPath )
            
            if self._config.make_fusioned_folder_names:
                print "try to merge folders"
                self.makeRangeFolders(imgDatetime, dateFolders)
            else:
                print "I won't try merging folders"
        
        return dateFolderPath
    

    def moveFile(self,dateFolderPath,handledFilePath):
        print "moving..."
        fileName = os.path.splitext(os.path.basename(handledFilePath))
        dest  = os.path.join(dateFolderPath,fileName[0]+fileName[1])
        i = 0
        while os.path.exists(dest):
            i+=1
            dest  = os.path.join(dateFolderPath,fileName[0]+'_'+str(i)+fileName[1])
            if 100 == i:
                print "Tried renaming the file up to "+fileName[0]+'_'+str(i)+fileName[1]+" without success."
                print "Giving up since we might be in a loop. File not moved:",handledFilePath
                return
        os.rename(handledFilePath, dest)
        print "moved"
    
    def getImageDate(self,handledFilePath,useFilesystem=True):
        print "Reading metadata:",handledFilePath
        imgDatetime = None
        try:
            image = pyexiv2.ImageMetadata(unicode(handledFilePath,'utf-8'))
            image.read()
            #print image.exifKeys()
            try:
                imgDatetime = image['Exif.Photo.DateTimeOriginal']
                #print "found DateTimeOriginal"
            except KeyError:
                imgDatetime = image['Exif.Image.DateTime']
                #print "found DateTime"
            imgDatetime = imgDatetime.value
            if type(imgDatetime) != datetime.datetime:
                if type(imgDatetime) == str:
                    print "pyexif returned a string rather than a datetime object"
                    dateParse = re.match(r"^(\d{4}):(\d{2}):(\d{2}).*",imgDatetime).groups()
                    imgDatetime = datetime.datetime(int(dateParse[0]),int(dateParse[1]),int(dateParse[2]));
                else:
                    print "pyexif returned nothing worthwhile"
                    raise Exception()    
        except Exception as e:
            if type(e) == IOError or type(e) == KeyError:
                print "Probably no EXIF data :",e
                if useFilesystem:
                    print "is it an image or a video?"
                    t = mimetypes.guess_type(handledFilePath)
                    print "Mime : ",t
                    if type(t[0]) == type("") and (
                            t[0].startswith('video') or  t[0].startswith('image')
                            ):  
                        print "It's an image or a video. Trying the last modif date"
                        imgDatetime = datetime.datetime.fromtimestamp(os.path.getmtime(handledFilePath))
                        print "got:", imgDatetime
            else: raise
        print "date time is",imgDatetime    
        return imgDatetime

    def makeRangeFolders(self,imgDatetime,dateFolders):
        # append to a prevRange if dir exists for previous or next day
        # search for possible matches
        prevDay = imgDatetime-datetime.timedelta(days=1)
        #prev = os.path.join(self._config.rename_folder,mkDateFolderName(prevDay))
        
        nextDay = imgDatetime+datetime.timedelta(days=1)
        #next = os.path.join(self._config.rename_folder,mkDateFolderName(nextDay))
        
        rangeFolders = mover.findRangeFolders(self._config.rename_folder)
        
        prevRange = None
        
        if dateFolders.has_key(mover.mkDateFolderName(prevDay)):
            print "prev exists"
            if len(rangeFolders):
                for start,finish,rangeFoldCurrentPath in rangeFolders: #@UnusedVariable
                    if mover.sameDay(finish,prevDay):
                        print "prevRange with prev"
                        prevRange = rangeFoldCurrentPath
                        break 
            
            if None != prevRange:
                newPrevRange = mover.mkRangeFolderName(start, imgDatetime,self._config.rename_folder)
                print "we have a prevRange. Rename from",prevRange,"to",newPrevRange
                os.rename(prevRange,newPrevRange)
                prevRange = newPrevRange
                prevRangeStart = start
            else:
                prevRange = mover.mkRangeFolderName(prevDay,imgDatetime,self._config.rename_folder)
                print "No prevRange. We make it from ",prevDay,"and",imgDatetime,":",prevRange
                os.mkdir(prevRange)
                prevRangeStart = prevDay
                
        nextRange = None                
        if dateFolders.has_key(mover.mkDateFolderName(nextDay)):
            print "next exists"
            if len(rangeFolders):
                for start,finish,rangeFoldCurrentPath in rangeFolders: #@UnusedVariable
                    if mover.sameDay(start,nextDay):   
                        print "nextRange with next"
                        nextRange = rangeFoldCurrentPath
                        break
            
            if None != nextRange:
                print "We have a nextRange",nextRange
                if None == prevRange:
                    newNextRange = mover.mkRangeFolderName(imgDatetime,finish,self._config.rename_folder)
                    print "but no prev: rename nextRange from ",nextRange,"to",newNextRange
                    os.rename(nextRange,newNextRange)
                else:
                    mergeRange = mover.mkRangeFolderName(prevRangeStart,finish,self._config.rename_folder)
                    print "with prev: We rename from ",prevRange,"to",mergeRange
                    os.rename(prevRange,mergeRange) 
                    print "we delete",nextRange
                    os.rmdir(nextRange)  
            else:
                if None == prevRange:
                    nextRange = mover.mkRangeFolderName(imgDatetime,nextDay,self._config.rename_folder)
                    print "No nextRange. We make it:",nextRange
                    os.mkdir(nextRange)
                else:
                    print "No nextRange but we have a prevRange: we merge"
                    mergeRange = mover.mkRangeFolderName(prevRangeStart,nextDay,self._config.rename_folder)
                    print "with prev: We rename from ",prevRange,"to",mergeRange
                    os.rename(prevRange,mergeRange) 
        # link in prevRange now that we have one
        
        
    
        