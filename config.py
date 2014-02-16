
import os

DB_FILE = 'xiami.db'
TEMP_DIR = u'/home/prehawk/Music'
SC_DIR = u'~/Music'
LOG_PATH = u'controller.log'
COVER_DIR = u'~/Pictures'
TEST_DIR = u'Exp'

APPDATA_XP = 'D:/Documents and Settings/Prehawk/Local Settings/Application Data'
APPDATA_WIN7 = 'C:/Users'
I_CACHE = '/liebao/User Data/kswl673172648/iecache/Content.IE5'
C_CACHE = '/liebao/User Data/kswl673172648/Cache'
X_CACHE = 'F:/XMusic/Temp/song'
if os.path.exists(APPDATA_WIN7):
    I_CACHE = 'D:\ProgramData\liebaoCache\kswl673172648\iecache\Content.IE5'
else:
    I_CACHE = APPDATA_XP + I_CACHE
    C_CACHE = APPDATA_XP + C_CACHE