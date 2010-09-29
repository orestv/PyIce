#coding: utf-8
import os
import mutagen
from mutagen.easyid3 import EasyID3
import random
import shout
import server
import threading
import time


class Source:
    def __init__(self, path='.', mount='/pyrockHQ', port=50000):
        print 'Starting server: mount = %s' % (mount,)
        self.s = Server(path, mount, port)
        self.s.start()

    def stop(self):
        self.s.stop()



class Server(threading.Thread):
    _playlist_size = 15
    _current_song = None

    def __init__(self, path, mount, port=50000):
        threading.Thread.__init__(self)
        self._mount = mount
        self._listener = server.Listener(self, port)
        self._listener.start()
        path = unicode(path)
        self._songs = find_all_music_files(path)
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

        bufsize = 8192

        while 1:
            print '---------------------------------------------'
            print 'Now playing: ', self._current_song
            print '--------playlist:'
            for song in self._playlist:
                print song
            f = open(self._current_song)
            artist = get_tag(self._current_song, 'artist')
            if artist:
                artist = artist.encode('utf-8')
            title = get_tag(self._current_song, 'title')
            if title:
                title = title.encode('utf-8')
            meta = artist + ' - ' + title
            s.set_metadata({'song' : meta})
            nbuf = f.read(bufsize)
            while 1:
                if self.stopped():
                    print 'Server stopped!'
                    f.close()
                    s.close()
                    self._listener.stop()
                    return
                buf = nbuf
                nbuf = f.read(bufsize)
                if not buf:
                    break
                s.send(buf)
                delay = s.delay()/1000.0
                delay = delay * 0.5
                if delay > 0.5:
                    time.sleep(delay)
            f.close()
            self._next_song()

        s.close()

    def _next_song(self):
        self._current_song = self._playlist[0]
        artist = get_tag(self._current_song, 'artist')
        if artist:
            self._last_artists.append(artist)
            if self._last_artists and len(self._last_artists) > self._playlist_size:
                self._last_artists.pop(0)
        self._playlist.pop(0)
        self._playlist.append(self._pick_new_song())

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
        return self._playlist

def get_tag(path, tagname):
   try:
       tags = EasyID3(path)
   except mutagen.id3.ID3NoHeaderError:
       return None
   if tags.has_key(tagname):
       artists = tags[tagname]
       if artists:
           return artists[0]
       else:
           return None
   else:
       return None

def find_all_music_files(top, type = 'mp3'):
    list = [(p, f) for (p, _, f) in os.walk(top) if f]

    result = []
    for (path, files) in list:
        for file in files:
            if file.endswith(type):
                result.append(os.path.join(path, file))
    return result
#    print (parent, dirs, files)

