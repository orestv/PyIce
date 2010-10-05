#coding: utf-8
import os
import mutagen
import mad
from mutagen.easyid3 import EasyID3
import random
import shout
import server
import threading
import time
import random


class Source:
    def __init__(self, path='.', mount='/pyrockHQ', port=50000):
        print 'Starting server: mount = %s' % (mount,)
        self.s = Server(path, mount, port)
        self.s.start()

    def stop(self):
        self.s.stop()



class Server(threading.Thread):
    _playlist_size = 10
    _current_song = {'path': None, 'duration': None, 'metadata': None,
                     'startTime': None, 'endTime': None}


    def __init__(self, path, mount, port=50000, bufsize=32768):
        threading.Thread.__init__(self)
        self.set_buffer_size(bufsize)
        self._mount = mount
        self._listener = server.Listener(self, port)
        self._listener.start()
        path = unicode(path)
        self._songs = find_all_music_files(path)
        n = time.time()
        def f():
            print 'Generating collection...'
            self._collection = generate_collection(self._songs)
            print 'Collection generated, %f seconds spent' % (time.time()-n,)
        threading.Thread(target=f).start()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        self._last_artists = []
        self._playlist = []
        song = random.choice(self._songs)
        self._playlist.append(song)
        self._next_song()
        for i in range(self._playlist_size):
            self._playlist.append(self._pick_new_song())
        self.play()

    def play(self):
        s = shout.Shout()
        s.host = 'localhost'
        s.format = 'mp3'
        s.password = 'ma$tercard'
        s.mount = self._mount
        s.name = 'Radio Seth'
        s.genre = 'Rock'
        s.url = 'http://213.130.28.169:8000/rock'
        s.open()


        while 1:
            print '---------------------------------------------'
            print 'Now playing: ', self._current_song['path']
            artist = get_tag(self._current_song['path'], 'artist')
            if artist:
                artist = artist.encode('utf-8')
            title = get_tag(self._current_song['path'], 'title')
            if title:
                title = title.encode('utf-8')
            meta = artist + ' - ' + title
            f = open(self._current_song['path'])

            mf = mad.MadFile(f)
            self._current_song['duration']  = mf.total_time() / 1000
            self._current_song['endTime'] = time.time() + self._current_song['duration']
            print self._current_song['endTime']
            print self._current_song['duration']/60, ':', self._current_song['duration']%60
            t = self._current_song['endTime']
            print t
            t = time.localtime(t)
            print t
            t = time.strftime('%H:%M:%S', t)
            print t

            s.set_metadata({'song' : meta})
            nbuf = f.read(self.get_buffer_size())
            while 1:
                if self.stopped():
                    print 'Server stopped!'
                    f.close()
                    s.close()
                    self._listener.stop()
                    return
                buf = nbuf
                nbuf = f.read(self.get_buffer_size())
                if not buf:
                    break
                s.send(buf)
                delay = s.delay()/1000.0
                delay = delay * 0.3
                if delay > 0.2:
                    time.sleep(delay)
            f.close()
            self._next_song()

        s.close()

    def set_buffer_size(self, bufsize):
        self._bufsize = bufsize

    def get_buffer_size(self):
        return self._bufsize

    def set_next_song(self, path):
        self._playlist = [path] + self._playlist

    def _next_song(self):
        self._current_song['path'] = self._playlist[0]
        artist = get_tag(self._current_song['path'], 'artist')
        if artist:
            self._last_artists.append(artist)
            if self._last_artists and len(self._last_artists) > self._playlist_size:
                self._last_artists.pop(0)
        self._playlist.pop(0)
        def f():
            self._playlist.append(self._pick_new_song())
        threading.Thread(target=f).start()

    def _pick_new_song(self):
        artists = [get_tag(f, 'artist') for f in self._playlist]
        artists.extend(self._last_artists)
        choice = None
        while not choice:
            choice = random.choice(self._songs)
            artist = get_tag(choice, 'artist')
            if not artist or artist in artists:
                choice = None
        return choice

    def get_playlist(self):
        return generate_collection(self._playlist)

    def get_collection(self):
        return self._collection

def get_tag(path, tagname):
   try:
       tags = EasyID3(path)
   except mutagen.id3.ID3NoHeaderError:
       return None
   if tags.has_key(tagname):
       tag = tags[tagname]
       if tag:
           return tag[0]
       else:
           return ''
   else:
       return ''

def get_tags(path, lstTags):
    try:
        tags = EasyID3(path)
    except mutagen.id3.ID3NoHeaderError:
        return {}
    result = {}
    for tagname in lstTags:
        if tags.has_key(tagname):
            tag = tags[tagname]
            if tag:
                result[tagname] = tag[0]
            else:
                result[tagname] = ('')
        else:
            result[tagname] = ('')
    return result

def find_all_music_files(top, type = 'mp3'):
    list = [(p, f) for (p, _, f) in os.walk(top) if f]

    result = []
    for (path, files) in list:
        for file in files:
            if file.endswith(type):
                result.append(os.path.join(path, file))
    return result

def generate_collection(lstFiles):
    def f(x, y):
        return x + ' - ' + y
    result = []
    for item in lstFiles:
        result.append({'path': item, 
                       'tags': get_tags(item, ['artist', 'album', 'title'])})
    return result

#    print (parent, dirs, files)

