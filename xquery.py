# -*- coding: UTF-8 -*-
import sys, os, re, time, urllib, urllib2, lxml, shutil, logging, sqlite3
from pyquery import PyQuery
from errorinfo import *


XIAMI = 'http://www.xiami.com/'
XIAMI_IDPATTERN = \
'http://www.xiami.com/+(song|album|artist|artist/album/id)/(\d+)'

class TagQuery(object):

    def __init__(self, argv=u'1770141660', level=3, dbfile='test.db'):
        self.qr1 = DataBase(argv, dbfile)
        self.qr2 = WebSite(argv, level)
        self.qr1.setSuccesor(self.qr2)
        self.qr2.setPrecursor(self.qr1)

    def gettags(self):
        return self.qr1.gettags()

    def expandInfo(self):
        return self.qr1.expandInfo()


class Query(object):

    def setSuccesor(self, nextOne):
        self.nextOne = nextOne

    def setPrecursor(self, formerOne):
        self.formerOne = formerOne
    
    def expandInfo(self):
        return self.nextOne.expandInfo()
    
    def gettags(self):
        return self.nextOne.gettags()

    def getid(self, s):
        return re.match(XIAMI_IDPATTERN, s).group(2)


class DataBase(Query):

    def __init__(self, argv=u'1770141660', dbfile=''):
        self.dbfile = dbfile
        self.sid = argv
        self.tags = {}
        self.cxn = sqlite3.connect(self.dbfile)
        self.cxn.row_factory = sqlite3.Row
        self.cur = self.cxn.cursor()
        self.ensureDatabase()

    def expandInfo(self):
        if self.setSongTag():
            if self.setAlbumTag():
                if self.setAritstTag():
                    retstr =  u'Database: %d - %s [%s][%s]' % \
                           (int(self.tags['TRCK']),self.tags['TIT2'],
                            self.tags['TALB'], self.tags['TPE1'])
                    return retstr
        return self.nextOne.expandInfo()


    def insertTags(self, tags):
        sql_song = \
        u"INSERT INTO 'song' VALUES (%d, %d, %d, '%s', '%s', '%s')" % \
        (int(self.nextOne.songinfo['id']),
         int(self.nextOne.albuminfo['id']),
         int(self.nextOne.artistinfo['id']),
         tags['TIT2'], tags['TRCK'], tags['TPE1'] )

        sql_album = \
        u"INSERT INTO 'album' VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s', '%s')"\
        % (int(self.nextOne.albuminfo['id']),
           int(self.nextOne.artistinfo['id']),
           tags['TALB'], tags['TYER'], tags['TLAN'], tags['TPUB'],
           tags['COMM'], tags['cov_data'] )

        sql_artist = \
        u"INSERT INTO 'artist' VALUES (%d, '%s', '%s')" % \
        (int(self.nextOne.artistinfo['id']), tags['TPE0'], tags['art_data'])

        sql = sql_song + u';' + sql_album + u';' +sql_artist
        self.insertSql(sql_song, sql_album, sql_artist)
        self.tags = tags

    def insertSql(self, *arg):
        for sql in arg:
            try:
                self.cur.execute(sql)
            except sqlite3.IntegrityError, e:
                if e.message.startswith('PRIMARY KEY must be unique'):
                    pass
            except sqlite3.OperationalError, e:
                XqueryWarning(sql)
        self.cxn.commit()

    
    def setSongTag(self):
        self.cur.execute('SELECT * FROM song WHERE id = %d' % int(self.sid))
        self.songinfo = self.cur.fetchone()
        if self.songinfo and self.songinfo['alb_id']:
            self.tags['TIT2'] = self.songinfo['tit2']
            self.tags['TRCK'] = self.songinfo['trck']
            self.tags['TPE1'] = self.songinfo['TPE1']
            return True


    def setAlbumTag(self):
        self.cur.execute('SELECT * FROM album WHERE id = %d' % \
                             int(self.songinfo['alb_id']) )
        self.albuminfo = self.cur.fetchone()
        if self.albuminfo and self.albuminfo['art_id']:
            self.tags['TALB'] = self.albuminfo['talb']
            self.tags['TYER'] = self.albuminfo['tyer']
            self.tags['TLAN'] = self.albuminfo['tlan']
            self.tags['TPUB'] = self.albuminfo['tpub']
            self.tags['COMM'] = self.albuminfo['comm']
            self.tags['cov_data'] = self.albuminfo['cov_data']
            return True

    def setAritstTag(self):
        self.cur.execute('SELECT * FROM artist WHERE id = %d' % \
                             int(self.albuminfo['art_id']) )
        self.artistinfo = self.cur.fetchone()
        if self.artistinfo and self.artistinfo['tpe0']:
            self.tags['TPE0'] = self.artistinfo['tpe0']
            self.tags['art_data'] = self.artistinfo['art_data']
            return True


    def ensureDatabase(self):
        try:
            self.cur.execute("SELECT * FROM song")
            self.cur.execute("SELECT * FROM album")
            self.cur.execute("SELECT * FROM artist")
        except sqlite3.OperationalError, e:
            if e.message.startswith('no such table'):
                try:
                    self.cur.executescript('''
                                CREATE TABLE song (
                                id INTEGER PRIMARY KEY,
                                alb_id INTEGER,
                                art_id INTEGER,
                                tit2 TEXT,
                                trck TEXT,
                                tpe1 TEXT);
                                
                                CREATE TABLE album (
                                id INTEGER PRIMARY KEY,
                                art_id INTEGER,
                                talb TEXT,
                                tyer TEXT,
                                tlan TEXT,
                                tpub TEXT,
                                comm TEXT,
                                cov_data TEXT);
                                
                                CREATE TABLE artist (
                                id INTEGER PRIMARY KEY,
                                tpe0 TEXT,
                                art_data TEXT);
                                
                    ''')
                    self.cxn.commit()
                except sqlite3.OperationalError: pass          
      
    def gettags(self):
        if self.tags:
            return self.tags
        else:
            return self.nextOne.gettags()
                    

class WebSite(Query):

    def __init__(self, argv=u'1770141660', level=3):
        super(WebSite, self).__init__()
        self.level = level
        m = re.match(XIAMI_IDPATTERN, argv)
        if m:#传入URL (注意，不会自动获得Info)
            self.url = argv
        elif re.match('\d+', argv): #传入ID
            self.url = XIAMI + 'song/' + argv
        else:
            XqueryWarning('WebSite: argv not correct')
        #self.expandInfo()

    def gettags(self):
        art = trck = tyer = tlan = tpub = None
        if self.level > 1:
            for sn in self.albuminfo['song_lst']:
                for sn_name in sn['title_lst']:
                    if sn_name == self.songinfo['title']:
                        alb_sn = sn
                        break
            trck = alb_sn['trackno']
            try:
                tyer = self.albuminfo['year'][:4]
            except:
                tyer = '2013'       #debug
            tlan = self.albuminfo['lang']
            tpub = self.albuminfo['company']
        
        if self.level > 2:
            art = self.artistinfo['cov_ref']
        
        tit2 = self.songinfo['title']
        talb = self.songinfo['album']
        tpe = self.albuminfo['artist']
        tpe1 = ';'.join( self.songinfo['artist_lst'] )
        cov  = self.songinfo['cov_ref']
        comm = unicode(self.songinfo['id'])
        
        tags = {'TIT2': tit2,
                'TALB': talb,
                'TPE1': tpe1,
                'TRCK': trck,
                'TYER': tyer,
                'TLAN': tlan,
                'TPUB': tpub,
                'COMM': comm,
                'art_data' : art,
                'cov_data' : cov,
                'TPE0' : tpe}
        self.formerOne.insertTags(tags)
        return tags
        


    def expandInfo(self):
        self.songinfo = UrlPage(self.url).parseUrl()
        
        alb_url = self.songinfo['alb_ref']
        self.albuminfo = UrlPage(alb_url).parseUrl()
         
        art_url = self.albuminfo['art_ref']
        self.artistinfo = UrlPage(art_url).parseUrl()
        if self.level >= 4:
            alblst_ref = XIAMI + '/artist/album/id/' + self.artistinfo['id']
            album_lst = UrlPage(alblst_ref).parseUrl()
            self.artistinfo['album_lst'] = album_lst
        if self.songinfo and self.albuminfo and self.artistinfo:
            return u'WebSite: %s - [%s][%s]' % \
                   (self.songinfo['title'], self.albuminfo['title'],
                    self.artistinfo['name'])
        else:
            return u'Failed to ExpandInfo!'
        


class UrlPage(object):
    
    def __init__(self, argv='',  argtype=u'song'):
        
        m = re.match(XIAMI_IDPATTERN, argv)
        if m:#传入URL 
            self.url = argv
        elif re.match('\d+', argv) and \
                argtype in ['song',  'album',  'artist', 'artist/album/id']: #传入ID
            self.url = XIAMI + argtype + '/' + argv
            
        self.html = None
        self.info = None

    def _getResponse(self, url):
        '''
        (v1.1)input a url and output response. Typically its an html document
        '''
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; \
        Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.5.30729; \
        .NET CLR 3.0.4506.2152; .NET4.0C; .NET4.0E; Zune 4.7) LBBROWSER')
        time_retry = 0
        try:
            response = urllib2.urlopen(request)
            return response
        except:
            raise XqueryError('UrlPage._getResponse: urlopen error %s' % url)


    def _winfold(self, s):
        if s is not None:
            try:
                s = unicode(s).encode('latin1').decode('UTF-8')
                for old, new in zip(unicode(u'/\\:*?"<>|\''),
                                    unicode(u'／﹨﹕﹡？＂〈〉︳ˊ')):
                    s = s.replace(old, new)
                return s.strip()
            except:
                try:
                    return s.strip()
                except:
                    return s
                


    def parseUrl(self):
        m = re.match(XIAMI_IDPATTERN, self.url)
        self.html = self._getResponse(self.url).read()
        
        if m: #url是合法的xiami链接 m.group(1) :      type, m.group(2): id
            if m.group(1) == u'song':
                self.info = SongPage(self.html).parsePage()
                self.info['id'] = m.group(2)
            elif m.group(1) == u'album':
                self.info = AlbumPage(self.html).parsePage()
                self.info['id'] = m.group(2)
            elif m.group(1) == u'artist':
                self.info = ArtistPage(self.html).parsePage()
                self.info['id'] = m.group(2)
            elif m.group(1) == u'artist/album/id':
                album_lst = []
                ret_lst, next_ref = AlbLstPage(self.html).parsePage()
                album_lst.extend(ret_lst)
                while next_ref:
                    html = self._getResponse(next_ref).read()
                    ret_lst, next_ref = AlbLstPage(html).parsePage()
                    album_lst.extend(ret_lst)
                self.info = album_lst
            return self.info

class SongPage(UrlPage):

    def __init__(self, html):
        super(SongPage, self).__init__()
        self.html = html

    def parsePage(self):
        hq = PyQuery(self.html)

        title2 = hq('#title h1 span').html()
       
        title1 = hq('#title h1').remove('span').html()
        album = hq('#albums_info tr a').html()
        alb_ref = XIAMI + hq('#albums_info tr a').attr.href
        
        artist_lst = [];art_ref_lst = []
        for a in hq('#albums_info tr+tr td+td a').items():
            if not a.children():
                artist_lst.append(self._winfold(a.html()))
                art_ref_lst.append(XIAMI + a.attr.href)

        cov_ref = hq('#song_block .album_relation img').attr.src

        return {'title': self._winfold(title1),
                    'subtitle':self._winfold(title2),
                    'album':self._winfold(album),
                    'alb_ref':alb_ref,
                    'artist_lst':artist_lst,
                    'art_ref_lst':art_ref_lst,
                    'cov_ref':cov_ref}

class AlbumPage(UrlPage):
    
    def __init__(self,  html):
        super(AlbumPage,  self).__init__()
        self.html = html
        
    def parsePage(self):
        hq = PyQuery(self.html)

        title2 = hq('#title h1 span').html()
        title1 = hq('#title h1').remove('span').html()
        artist = hq('#album_info table tr td+td a').html()
        art_ref = XIAMI + hq('#album_info table tr td+td a').attr.href
        lang = hq('#album_info table tr+tr td+td').html()
        company = hq('#album_info table tr+tr+tr td+td a').html()
        year = hq('#album_info table tr+tr+tr+tr td+td').html()
        albtype = hq('#album_info table tr+tr+tr+tr+tr td+td').html() 
        genre = hq('#album_info table tr+tr+tr+tr+tr+tr td+td a').html()
        cov_ref = hq('#cover_lightbox img').attr.src
        song_lst = []
        for tab in hq('#track .chapter table').items():
            for no, tr in enumerate(tab('tr').items()):
                trackno = no + 1
                
                title_lst = [];title_ref_lst = [];songartist_lst = []
                for i, sa in enumerate(
                    PyQuery(tr('.song_name').html()).contents() ):
                    songartist_lst.append( self._winfold(sa) )
                else:
                    if not songartist_lst:
                        songartist_lst.append( self._winfold(artist) )

                for t in tr('.song_name a').items():
                    title_lst.append( self._winfold(t.html()) )
                    title_ref_lst.append( XIAMI + t.attr.href )

                song = {'trackno': int(trackno),
                        'title_lst': title_lst,
                        'title_ref_lst':title_ref_lst,
                        'songartist_lst':songartist_lst}

                song_lst.append(song)

        return {'title': self._winfold( title1 ),
                    'subtitle':self._winfold( title2 ),
                    'artist': self._winfold( artist ),
                    'art_ref': art_ref,
                    'lang': self._winfold( lang ),
                    'company': self._winfold( company ),
                    'year':self._winfold( year ),
                    'albtype':self._winfold( albtype ),
                    'genre': self._winfold( genre ),
                    'cov_ref': cov_ref,
                    'song_lst': song_lst}

class ArtistPage(UrlPage):
    
    def __init__(self, html):
        super(ArtistPage,  self).__init__()
        self.html = html
    
    def parsePage(self):
        hq = PyQuery(self.html)

        try:
            title2 = hq('#title h1 span').html().split(';')
        except: title2 = None
        title1 = hq('#title h1').remove('span').html()

        style = u'';zone = u'';profile = u''
        for a in hq('#artist_info table tr').items():
            s = PyQuery(a)
            left = s('td').eq(0).text()
            right = s('td').eq(1).text()
            if left == u'地区：':
                zone = right
            elif left == u'档案：':
                profile = right
            elif left == u'风格：':
                style = right

        cov_ref = hq('#cover_lightbox img').attr.src

        return {'name': self._winfold( title1 ),
                    'alias_lst': title2,
                    'zone': self._winfold( zone ),
                    'style': self._winfold( style ),
                    'profile': self._winfold( profile ),
                    'cov_ref': cov_ref}

class AlbLstPage(UrlPage):
    
    def __init__(self,  html):
        super(AlbLstPage,  self).__init__()
        self.html = html
        
    def parsePage(self):
        hq = PyQuery(self.html)

        album_lst = []
        for h in hq('#artist_albums .albumThread_list ul li').items():
            d = PyQuery(h)
            cov_ref = d('.cover a img').attr.src
            title = d('.detail .name a').attr.title
            alb_ref = XIAMI + d('.detail .name a').attr.href       
            
            
            album = {'cov_ref':cov_ref,
                     'title': title,
                     'alb_ref':alb_ref}
            album_lst.append(album)
        try:
            next_ref = XIAMI + \
                       hq('#artist_albums .all_page .p_redirect_l').attr.href
        except:
            next_ref = None
        return album_lst, next_ref

if __name__ == '__main__':
 
    a = UrlPage('1772184919', 'song')
    b = UrlPage('1772184929', 'song')
    c = UrlPage('1772190619', 'song')

    print "****Module testing... xiami page parse result will be display below****"
    
    e = TagQuery('1772454813')
    e.expandInfo()
    ret = e.gettags()
    for i in ret.items():
        print i
    
    
    
    
    
    
