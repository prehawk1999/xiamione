# encoding:utf-8

import os, re, sys, urllib, urllib2, datetime, cookielib, logging, time

LOG_PATH = 'E:/My Stuff/Pyscript/Xiami/xiami_checkin.log'
EMAIL = 'prehawk@gmail.com'
PASSWORD = 'despicable-2011'

def installOpener():
    # Init
    cookie_jar = cookielib.CookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookie_handler)
    opener = urllib2.build_opener(cookie_handler)
    urllib2.install_opener(opener)
    



def login(EMAIL,PASSWORD):
    login_url = 'https://login.xiami.com/member/login'
    login_data = urllib.urlencode({
        'done': '/',
        'email':EMAIL,
        'password':PASSWORD,
        'submit':'{+U',
        'autologin':'1'
    })
    login_headers = {
        'Referer':'http://www.xiami.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
        'Connection':'keep-alive'
    }
    login_request = urllib2.Request(login_url, login_data, login_headers)
    login_response = urllib2.urlopen(login_request).read()
    with open('1.html', 'w') as f:
        f.write(login_response)
    return login_response


def checkin(EMAIL, PASSWORD, login_response):
    checkin_pattern = re.compile(r'<a.*>(.*?)天\s*?<span>已连续签到</span>')
    checkin_result = checkin_pattern.search(login_response)
    if checkin_result:
        logging.info('%s, %s, %s天已连续签到' % \
                     (datetime.datetime.now(), EMAIL, checkin_result.group(1)))

        return

    checkin_url = 'http://www.xiami.com/task/signin'
    checkin_headers = {'Referer':'http://www.xiami.com/',
                       'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64; \
                       rv:25.0) Gecko/20100101 Firefox/25.0',
                       'Host':'www.xiami.com',
                       'Accept':'*/*',
                       'X-Requested-With':'XMLHttpRequest',
                       'Connection':'keep-alive',
                       'Pragma':'no-cache',
                       'content-Length':'0'}
    checkin_request = urllib2.Request(checkin_url, None, checkin_headers)
    checkin_response = urllib2.urlopen(checkin_request).read()

    return checkin_response







def main():
    '''
    # Get email and password
    if len(sys.argv) != 3:
        print >>f, '[Error] Please input EMAIL & password as sys.argv!'
        print >>f, datetime.datetime.now()
        return
    email = sys.argv[1]
    password = sys.argv[2]
    '''
    #logging setup
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO)
    
    installOpener()
    
    login_response = login(EMAIL, PASSWORD)
    logging.info('开始签到')

    checkin_response = checkin(EMAIL, PASSWORD, login_response)
    logging.info('%s, %s天连续签到' % (EMAIL, checkin_response) )



def waitfornetwork():
    msg = 'socket error'
    while not msg == 'ok':
        try:
            urllib.urlopen('http://www.baidu.com')
            msg = 'ok'
        except (IOError, urllib2.URLError), e:
            print e.errno
        time.sleep(1)
    
if __name__ == '__main__':
    
    main()
    

