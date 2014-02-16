# encoding: utf-8
import sys, logging
from errorinfo import *
from xquery import TagQuery
from listening import ListeningProbe
from creator import Creator
from controller import *

d = DIRController()
d.start()
