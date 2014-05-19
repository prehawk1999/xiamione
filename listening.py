# -*- coding: UTF-8 -*-
import os, re, time
from xquery import WebSite
from errorinfo import *
from config import *

class ListeningProbe(object):

    def __init__(self, typecode = 'test'):
        self.playing = self.listeningFactory(typecode)
        self.noplaying = self.playing.noplaying
        if not self.playing.noplaying:
            self.lpath = self.playing.lpath
            self.lid = self.playing.lid
        else:
            self.lpath = None
            self.lid = None
            
            

    def listeningFactory(self, typecode):
        if typecode == 'test':
            self.type = 'test'
            return FILElistening('1769948048_1879231_l.mp3')
        elif typecode == 'ie':
            self.type = 'ie'
            return IElistening()
        elif typecode == 'xiami':
            self.type = 'xiami'
            return XIAlistening()
        elif typecode == 'dir':
            self.type = 'dir'
            return DIRlistening()
        else:
            ListeningWarning('ListeningProbe: typecode illegal').ahk_display()


        

class Listening(object):
    '''
    if not self.noplaying:
        print self.lpath
        print self.lid
'''
    
    def __init__(self):
        pass
    
    def getNowplaying(self):
        pass

    def _findlatest(self, target, last=0, suffix='', delete=False):
        fl, ret = [], []
        for root, dirs, files in os.walk(target):
            for fname in files:
                if fname.endswith(suffix):
                    full_path = os.path.join(root, fname)
                    mtime = os.stat(full_path).st_ctime
                    fl.append({'name':fname,
                               'path':full_path,
                               'mtime':mtime})

        fl.sort(key=lambda x:x['mtime'], reverse=True)
        
        if last > len(fl) or last == 0:
            last = len(fl)

        for i in range(len(fl)):
            if i < last:
                ret.append(fl[i])
            else:
                if delete:
                    try:
                        os.remove(fl[i]['path'])
                    except Exception:
                        ListeningWarning('_findlatest: cant delete other file')
        return ret
    
    def parseID(self, s):
        '''
        input cache mp3 name and parse its id '

        >>> parseID('99639_33489[1].mp3')
        99639
        >>> parseID('01%201769135356_1234[1].mp3')
        1769135356
        >>> parseID('02_1758183848_1234[1].mp3')
        1758183848
        >>> parseID('1769233921_1143401_l[1].mp3')
        1769233921
        >>> parseID(u'Copenhagen_Let_Me_Go_\u867e\u5c0f\u7c73\u6253\u789f\u4e2d_1772184731_10828461_l.mp3')
        1772184731
        '''
        m = []
        m.append(re.match(r'(\d{3,})_\d+(\[\d?\])?', s))
        m.append(re.match(r'\d{2}%20(\d+)_\d+(\[\d?\])?', s))
        m.append(re.match(r'\d{2}_(\d+)_\d+(\[\d?\])?', s))
        m.append(re.match(r'(\d+)_\d+_\w(\[\d\])?', s))
        m.append(re.match(u'.+_\u867e\u5c0f\u7c73\u6253\u789f\u4e2d_(\d+)_\d+_l', s))
        m.append(re.match(r'.+_(\d+)_\d+_l', s))

        for p in m:
            if p: return p.group(1)
        else:
            return False


            
class IElistening(Listening):
    '''Get the most recent playing file in IE cache.

'''


    def __init__(self):
        super(IElistening, self).__init__()
        f = self.getNowplaying()
        if f:
            self.lpath = f['path']
            self.lid = self.parseID(f['name'])
            self.noplaying = False
        else:
            self.noplaying = True

    def getNowplaying(self):
        f = self._findlatest(I_CACHE, 1, '.mp3', True)
        if f: return f[0]
        


class XIAlistening(Listening):
    '''Get xiami music the most recent played file which is closed to getNowplaying.

'''

    def __init__(self):
        super(XIAlistening, self).__init__()
        f = self.getNowplaying()
        if f:
            self.lpath = f['path']
            self.lid = f['name']
            self.noplaying = False
        else:
            self.noplaying = True

    def getNowplaying(self):
        '''
        works if you don't pause xiami music
        '''
        f = self._findlatest(X_CACHE, last=2, delete=True)
        if len(f) == 1:
            t = time.time() - f[0]['mtime']
            if t < 600:
                return f[0]
            else:
                try:
                    os.remove(f[0]['path'])
                except:
                    ListeningWarning('XIAlistening.getNowplaying: cant delete')
        elif len(f) == 2:
            t0 = time.time() - f[0]['mtime']
            t1 = time.time() - f[1]['mtime']
            if t0 < 25 and t1 < 600:
                return f[1]
            elif 25 < t0 < 600:
                return f[0]
            else:
                try:
                    os.remove(f[0]['path'])
                    os.remove(f[1]['path'])
                except:
                    ListeningWarning('XIAlistening.getNowplaying: cant delete')

class WEBlistening(Listening):
    '''Get the most recent chrome cache file and its path .
'''

    def __init__(self):
        super(WEBlistening, self).__init__()
        f = self.getNowplaying()
        self.lpath = f['path']
        self.lid = 0
# 
#     def getNowplaying(self):
#         fl = []
#         for dirname, subdirs, files in os.walk(C_CACHE):
#             for fname in files:
#                 if fname.startswith('f_'):
#                     full_path = os.path.join(dirname, fname)
#                     while True:
#                         try:
#                             if MP3(full_path).info.sketchy == False:
#                                 mtime = os.stat(full_path).st_ctime
#                                 fl.append({'name':fname,
#                                            'path':full_path,
#                                            'mtime':mtime,
#                                            'cov' : None})
#                             break
#                         except HeaderNotFoundError, e:
#                             break
#                         except IOError, e:
#                             time.sleep(1)
#                             continue
#         fl.sort(key=lambda x:x['mtime'], reverse=True)
#         try:
#             for i in range(1, len(fl)):
#                     os.remove(fl[i]['path'])
#             return fl[0]
#         except Exception: return
#         
class FILElistening(Listening):
    '''Get specific file and parse the id from its file name.

'''

    def __init__(self, path):
        super(FILElistening, self).__init__()
        #f = self.getNowplaying()
        if os.path.exists(path) and os.path.isfile(path):
            self.lpath = path
            self.lid = self.parseID(os.path.basename(path))
            self.noplaying = False
        else:
            self.noplaying = True

class DIRlistening(Listening):

    def __init__(self):
        super(DIRlistening, self).__init__()
        self.noplaying = True
        if os.path.exists(TEMP_DIR):
            self._walk()
        else:
            ListeningError('TEMP_DIR dir not found!')
            

    def _walk(self):
        self.lpath = []
        self.lid = []
        for root, dirs, files in os.walk(TEMP_DIR):
            for fname in files:
                lid = self.parseID(fname)
                if lid:
                    self.lpath.append(os.path.join(TEMP_DIR, fname) )
                    self.lid.append(lid )
                
                
                
        

if __name__ == '__main__':
    
    #n = IElistening()
    print "****Module testing, the result will be display below****"
    n = FILElistening(u'正在播放_星をかぞえて_三谷朋世_1772602584_11456101_l')
    if not n.noplaying:
        print n.lpath, n.lid
    else:
        print u'正在播放_星をかぞえて_三谷朋世_1772602584_11456101_l'
    
    #n = FILElistening('E:/Exp/1769948048_1879231_l.mp3')
    #print n.lpath, n.lid

