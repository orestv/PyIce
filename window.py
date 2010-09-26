#!/usr/bin/python2
#coding: utf-8
import sys
import gtk, pygtk
import shout
import time
from mutagen.easyid3 import EasyID3
import source

S = source.Source(u'/media/d/Music')

try:
    while 1:
        time.sleep(1)
except:
    S.stop()
