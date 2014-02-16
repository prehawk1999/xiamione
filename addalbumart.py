import os, sys, urllib, json, re
from urllib import quote, urlopen, urlretrieve
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1, TRCK, error
from config import *

def getAlbumArt(artist, album):
    '''Usage: getAlbumArt(artist, album)
    
    artist and album are keywords'''
    
    keyword = str(artist)+' '+str(album)
    quote_key = quote(keyword)
    url = u'https://api.douban.com/v2/music/search?q="%s"&count=20' % quote_key
    try:
        res = urlopen(url)
    except: return
    if res.code == 200:
        text = res.read()
    else:
        print 'Response Not Common: %d' % res.code

    old_m_dg = 100
    if len(text) > 43: #返回结果非空
        content = json.loads(text)
        for m in content['musics']:
            ttl_douban = m['title']
            ttl_argu = unicode(album)
            
            if ttl_douban.startswith(ttl_argu):
                m_dg = len(ttl_douban) - len(ttl_argu)
                if m_dg < old_m_dg:
                    old_m_dg = m_dg
                    img = m['image']
    try:
        return img
    except Exception: pass


def generateSonglist(target):
    '''Usage: generateSonglist(dir)

return a list, (filepath, album, artist), only for mp3
and rename jpg files in every not root dirs 
'''
    song_list = []
    for root, dirs, files in os.walk(target):
        for fn in files:
            if fn.endswith('.mp3'):
                t1, album = os.path.split(root)
                t2, artist = os.path.split(t1)
                st = (os.path.join(root, fn), album, artist)
                song_list.append(st)
            elif fn.endswith('.jpg') and root != target:
                albname = os.path.basename(root)
                old_pic = os.path.join(root, fn)
                new_pic = os.path.join(root, albname) + '.jpg'
                try:
                    os.rename(old_pic, new_pic)
                except WindowsError, e:
                    if e.winerror == 183: pass
    return song_list

def findApic(filepath, album, artist):
    alb_dir, songname = os.path.split(filepath)
    alb_name = os.path.basename(alb_dir)
    local_cover = os.path.join(alb_dir, alb_name) + '.jpg'
    global_cover = os.path.join(COVER_DIR, alb_name) + '.jpg'
        
    data = None
    if os.path.exists(local_cover):
        data = open(local_cover, 'rb').read()
    elif os.path.exists(global_cover):
        data = open(global_cover, 'rb').read()
        os.rename(global_cover, local_cover)
    else:
        img = getAlbumArt(artist, album)
        if img:
            urlretrieve(img, local_cover)
            data = open(local_cover, 'rb').read()
    return data


def completeTags(filepath, album, artist):
    '''Usage: completeTags(filepath=, album=, artist=, picdata=)

'''
    try:
        audio = ID3(filepath)
    except:
        audio = ID3()

    fname = os.path.basename(filepath)
    m = re.match('\s*(\d+)\.?\s+(.+)', fname)
    if m:
        trck = m.group(1)
        tit2 = m.group(2)
    else:
        tit2 = fname
        trck = None
    if 'TRCK' not in audio.keys() and trck is not None:
        audio.add(TRCK(encoding=3, text=[trck] ) )
    if 'TIT2' not in audio.keys():
        audio.add(TIT2(encoding=3, text=[tit2] ) )
    if 'TALB' not in audio.keys():
        audio.add(TALB(encoding=3, text=[album] ) )
    if 'TPE1' not in audio.keys():
        audio.add(TPE1(encoding=3, text=[artist] ) )
    

    if 'APIC:Cover' not in audio.keys():
        data = findApic(filepath, album, artist)
        if data is not None:
            audio.add( APIC(
            encoding = 3,
            mime = 'image/jpg',
            type = 3,
            desc = u'Cover',
            data = data + '\x00'*(len(data)*3) ))
            print 'adding album art ... '
        else:
            print 'dont find album art %s - %s' % (album, artist)
            
    audio.save(filepath)


def main():
    snglst = generateSonglist(SC_DIR)
    for s in snglst:
        completeTags(*s)
        
if __name__ == '__main__':

    main()
    
