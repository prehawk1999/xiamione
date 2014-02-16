# encoding: utf-8

import sys, logging
from errorinfo import *
from xquery import TagQuery
from listening import ListeningProbe
from creator import Creator
from config import *

logging.basicConfig(filename=LOG_PATH, level=logging.INFO)





class XController(object):

    def __init__(self, typecode):
        self.started = False
        self.probe = ListeningProbe(typecode)
        if not self.probe.noplaying:
            self.xiaquery = TagQuery(self.probe.lid, dbfile=DB_FILE)
            self.crt = Creator(TEMP_DIR, self.probe.lpath)
        else:
            raise ControllerError('no current listening')

    def start(self):
        self.started = True
        self.pr1 = self.xiaquery.expandInfo()
        self.pr2 = self.crt.ensureEnv( self.xiaquery.gettags() )
        self.pr3 = self.crt.move()
        

    def ahk_display(self):
        print u'Xiami_controller'
        if self.started:
            print self.pr1
            print self.pr2
            print self.pr3
        else:
            print u'Not Yet Started!'
        
        
class DIRController(object):

    def __init__(self):
        self.started = False
        self.probe = ListeningProbe('dir')



    def start(self):
        self.started = True
        for n in range(len(self.probe.playing.lpath) ):
            lpath = self.probe.playing.lpath[n]
            lid = self.probe.playing.lid[n]
            print n, lid
            q = TagQuery(lid, dbfile=DB_FILE)
            c = Creator(TEMP_DIR, lpath)
            q.expandInfo()
            tags = q.gettags()
            c.ensureEnv(tags)
            c.move()
            c.clear()

class FlashGotController(object):

    def __init__(self):
        pass

    

if __name__ == '__main__':
    d = DIRController()
    d.start()
    

