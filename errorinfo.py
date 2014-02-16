# encoding: utf-8
import logging
from config import *
logging.basicConfig(filename=LOG_PATH, level=logging.INFO)


class PxmException(Exception):
           
    def ahk_display(self):
        print self.message
        return self


class PxmWarning(PxmException):

    def __init__(self, *args):
        super(PxmWarning, self).__init__(*args)
        logging.info(str(self.__class__) + ': ' + self.message)

class PxmError(PxmException):

    def __init__(self, *args):
        super(PxmError, self).__init__(*args)
        logging.warning(str(self.__class__) + ': ' + self.message)
        print self.message


class CreatorWarning(PxmWarning):pass
class CreatorError(PxmError):pass

class XqueryWarning(PxmWarning):pass
class XqueryError(PxmError):pass

class ListeningWarning(PxmWarning):pass
class ListeningError(PxmError):pass

class ControllerWarning(PxmWarning):pass
class ControllerError(PxmError):pass



if __name__ == '__main__':

    print "****Module Testing...error message will be display below****"
    CreatorWarning('fd;askfj;sadlfadfasdfasd').ahk_display()
    CreatorError('fd;askfj;sadlfadfasdfasd').ahk_display()
    XqueryWarning('fd;askfj;sadlfadfasdfasd').ahk_display()
    XqueryError('fd;askfj;sadlfadfasdfasd').ahk_display()
    ListeningWarning('fd;askfj;sadlfadfasdfasd').ahk_display()
    ControllerError('fd;askfj;sadlfadfasdfasd').ahk_display()
    
