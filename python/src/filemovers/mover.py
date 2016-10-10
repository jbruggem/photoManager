'''
Created on Feb 7, 2011

@author: jehan
'''
import os.path
import datetime
import errno


class Mover():
    pass


def symlink(target,linkname,renameIfExists=True):
    fileName = os.path.splitext(os.path.basename(linkname))
    destFolder = os.path.dirname(linkname)
    dest  = linkname
	# make sure dest exists
    makeDirs(destFolder,False)

    for i in range(1,99):
        try:
            print "#symlink"
            print "#target",os.path.relpath(target,destFolder)
            print "#linkname",dest
            cdir = os.curdir
            os.chdir(destFolder)
            os.symlink(os.path.relpath(target,destFolder),dest)
            os.chdir(cdir)
            print "#done"
            return dest
        except OSError as exc:
            print '#exception'
            if exc.errno == errno.EEXIST:
                if renameIfExists:
                    print "#exists. renaming"
                    dest = os.path.join(destFolder,fileName[0]+'_'+str(i)+fileName[1])
                else:
                    print "#exists. Not symlinking."
                    return dest
            else: raise

    print "Tried symlinking to",target,"with",linkname," without success. Giving up since we might be in a loop."
    return

def makeDirs(path,renameIfExists=True):
    dest=path
    destFolder = os.path.dirname(path)
    destName = os.path.basename(path)
    for i in range(1,99):
        try:
            print "making",dest
            os.makedirs(dest)
            return dest
        except OSError as exc:
            print "making dir exception",exc
            if exc.errno == errno.EEXIST:
                print "path exists"
                if renameIfExists:
                    dest = os.path.join(destFolder,destName+'_'+str(i))
                else:
                    return dest
            else: raise

    print "Tried making dir ",path," without success. Giving up since we might be in a loop."
    return


def moveFile(srcPath,destPath):
    print "moving",srcPath,destPath
    fileName = os.path.splitext(os.path.basename(destPath))
    destFolder = os.path.dirname(destPath)
    dest  = destPath

    for i in range(1,99):
        try:
            os.rename(srcPath,dest)
            return dest
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                dest = os.path.join(destFolder,fileName[0]+'_'+str(i)+fileName[1])
            else: raise

    print "Tried renaming from",srcPath,"to",destPath," without success. Giving up since we might be in a loop."
    return



def sameDay(day1,day2):
    print "compare",day1, day2
    return day1.year == day2.year and day1.month == day2.month and day1.day == day2.day

def mkDateFolderName(dt):
    return dt.strftime('%Y-%m-%d')

def mkRangeFolderName(dtStart,dtFinish,parent):
    print type(dtStart), type(dtFinish), dtStart, dtFinish

    n = dtStart.strftime('%Y-%m-%d')

    n2 = ''
    if dtFinish.year != dtStart.year:
        n2 +=  dtFinish.strftime('%Y')+'-'
    if dtFinish.month != dtStart.month:
        n2 +=   dtFinish.strftime('%m')+'-'
    if dtFinish.day != dtStart.day:
        n2 +=   dtFinish.strftime('%d')

    if len(n2) >0:
        n += '--' + n2

    return os.path.join(parent,n)

def findDateFolders(path):
    res = {}
    for f in os.listdir(path):
        if '-' in f and not '--' in f:
            dt = parseDateFolderName(f)
            #print "parsing",f
            if dt:
                res[mkDateFolderName(dt)] = (dt,os.path.join(path,f))

    return res

def parseDateFolderName(name):
    #print "parsing",f
    try:
        y = int(name[0:4])
        try:
            m = int(name[5:7])
        except ValueError as e:
            m = 1
        try:
            d = int(name[8:10])
        except ValueError as e:
            d = 1

        #print "date value:",y,m,d
        dt = datetime.datetime(y,m,d)
        #print "date:",dt
        return dt
    except ValueError as e:
        print "error parsing",name," | ",e
    except TypeError as e:
        print "error parsing",name," | ",e
    return None


def findRangeFolders(path):
    res = []
    for f in os.listdir(path):
        if '--' in f:
            #print "parsing",f
            try:
                ys = int(f[0:4])
                ms = int(f[5:7])
                ds = int(f[8:10])
                if len(f[12:]) == 2:
                    #print "only day"
                    yf = ys
                    mf = ms
                    df = int(f[12:14])
                elif len(f[12:]) == 5:
                    #print "day & month"
                    yf = ys
                    mf = int(f[12:14])
                    df = int(f[15:17])
                elif len(f[12:]) == 10:
                    #print "complete"
                    yf = int(f[12:16])
                    mf = int(f[17:19])
                    df = int(f[20:22])
                else:
                    #print "None"
                    yf = None
                    mf = None
                    df = None
                #print "start:",ys,ms,ds
                #print "end:",yf,mf,df
                res.append((datetime.datetime(ys,ms,ds),datetime.datetime(yf,mf,df),os.path.join(path,f)))

            except ValueError as e:
                print "error parsing",path," | ",e
            except TypeError as e:
                print "error parsing",path," | ",e


    return res
