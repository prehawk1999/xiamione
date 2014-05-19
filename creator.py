# -*- coding: UTF-8 -*-

import os, time, shutil, urllib2
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, TIT2, TIT3, TALB, TPE1, TRCK, TYER, TLAN, TPUB 
from mutagen.id3 import APIC, TCON, COMM, TDAT
from xquery import TagQuery
from errorinfo import *

class Creator:

    def __init__(self, musicdir, path, tags=None):
        self.musicdir = musicdir
        self.lpath = path
        self.buffered = False
        self.cov_data = None
        self.art_data = None
        self.tags = tags
        self.done = False
        if tags is not None:
            self.ensureEnv(tags)
            

    def ensureEnv(self, tags=None):
        if not self.tags and tags == None:
            raise CreatorError(u'You dont put tags in!')
        elif tags is not None:
            self.tags = tags

        self.d_cov = os.path.join(self.musicdir,
                             self.tags['TPE0'], self.tags['TALB'])
        self.f_art = os.path.join(self.musicdir,
                             self.tags['TPE0'], self.tags['TPE0']) + '.jpg'
        self.f_cov = os.path.join(self.d_cov, self.tags['TALB']) + '.jpg'
        self.f_sng = os.path.join(self.d_cov, self.tags['TIT2']) + '.mp3'

        #ensure dir trees
        if not os.path.exists(self.d_cov):
            os.makedirs(self.d_cov)
            

        #ensure pictures
        if not os.path.exists(self.f_art) or os.path.getsize(self.f_art) < 500:
            data = self.downloadCover(self.tags['art_data'], self.f_art, 'art')
            self.art_data = data
        else:
            self.art_data = open(self.f_art, 'rb').read()

        if not os.path.exists(self.f_cov) or os.path.getsize(self.f_cov) < 500:
            data = self.downloadCover(self.tags['cov_data'], self.f_cov, 'cov')
            self.cov_data = data
        else:
            self.cov_data = open(self.f_cov, 'rb').read()

        #ensure that the file is complete
        if not self.buffered:
            self.waitCompletion()

        #return something~~~
        if os.path.exists(self.lpath) and os.path.exists(self.f_cov) \
           and os.path.exists(self.f_art):
            return u'Target: %s\nDestination: %s' % \
                   (os.path.basename(self.lpath), self.musicdir)

    def move(self):
        try:
            shutil.copy(self.lpath, self.f_sng)
            self.temp = self.lpath
            self.lpath = self.f_sng
            self.easyTags()
            self.done = True
        except Exception, e:
            return u'Failed to Move! %s' % e.message
        else:
            return u'%s -by- %s -from- %s' % (self.tags['TIT2'], self.tags['TPE1'], self.tags['TALB'])

    def clear(self):
        if self.done:
            os.remove(self.temp)
            print u'%s\t -BY- \t%s\t -FROM- \t%s <done!>' % (self.tags['TIT2'], self.tags['TPE1'], self.tags['TALB'])
        else:
            raise CreatorError('failed to transmitt! no move!')
            
        
    def downloadCover(self, url, path, mode='cov'):
        tiy = 10
        while not os.path.exists(path) or os.path.getsize(path) < 500:
            if tiy <= 0:
                raise CreatorError(
                    'downloadCover: url cant be downloaded!').ahk_display()
            tiy -= 1
            try:
                os.remove(path)
            except Exception: pass
            try:
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; \
        Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.5.30729; \
        .NET CLR 3.0.4506.2152; .NET4.0C; .NET4.0E; Zune 4.7) LBBROWSER')
                res = urllib2.urlopen(req)
                data = res.read()
            except Exception:
                CreatorWarning('Failed to download pic!')

            with open(path, 'wb') as f:
                f.write(data)
            time.sleep(0.5)

        return data
                
            

    def easyTags(self):
        if not MP3(self.lpath).info.sketchy:
            try:
                audio = ID3(self.lpath)
            except ID3NoHeaderError:
                audio = ID3()
                audio.update_to_v23()
                audio.add(TIT2(encoding=3, text=[self.tags['TIT2']] ))
                audio.add(TALB(encoding=3, text=[self.tags['TALB']] ))
                audio.add(TPE1(encoding=3, text=[self.tags['TPE1']] ))
                audio.add(TRCK(encoding=3, text=[self.tags['TRCK']] ))
                audio.add(TYER(encoding=3, text=[self.tags['TYER']] ))
                audio.add(TLAN(encoding=3, text=[self.tags['TLAN']] ))
                audio.add(TPUB(encoding=3, text=[self.tags['TPUB']] ))
                audio.add(COMM(encoding=3, text=[self.tags['COMM']] ))
                if 'APIC:Cover' not in audio.keys() and self.cov_data:
                    audio.add(APIC(
                    encoding = 3,
                    mime = 'image/jpg',
                    type = 3,
                    desc = u'Cover',
                    data = self.cov_data + \
                    '\x00'*(len(self.cov_data)*3) ))
                    
                audio.save(self.lpath)
              




    def waitCompletion(self): 
        oz= os.stat(self.lpath).st_size
        cd = 10
        while cd > 0:
            time.sleep(0.2)
            nz = os.stat(self.lpath).st_size
            if nz == oz:
                cd -= 1
            else:
                oz = nz
                cd = 10
        self.buffered = True

if __name__ == '__main__':
    x = TagQuery('1769948048')
    x.expandInfo()
    print "****Module Testing, the result will be display below***"
    c = Creator('Exp', '1769948048_1879231_l.mp3', x.gettags())
    print "---===---Testing tagging  ---===---"
    print c.ensureEnv()
    print "---===---Testing file move---===---"
    print c.move()

