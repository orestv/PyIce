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
    _current_song = {}

    def __init__(self, path, mount, port, bufsize=32768, playlist_size = 10,
                 song_list_size = 80):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.set_buffer_size(bufsize)
        self._mount = mount
        self._listener = server.Listener(self, port)
        self._listener.start()
        self._playlist_size = playlist_size
        self._song_list_size = song_list_size
        path = unicode(path)
        self._songs = find_all_music_files(path)
        n = time.time()
        def f():
            print 'Generating collection...'
            self._collection = generate_collection(self._songs, self.stopped)
            if self._collection:
                print 'Collection generated, %f seconds spent' % (time.time()-n,)
            else:
                print 'Collection generation failed'
        threading.Thread(target=f).start()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        self._last_artists = []
        self._playlist = []
        self._song_list = []
        self._playlist_lock = threading.Lock()
        song = random.choice(self._songs)
        self._playlist.append(song)
        self._next_song()
        threading.Thread(target=self.fill_playlist).start()
        self.play()

    def fill_playlist(self):
        with self._playlist_lock:
            while len(self._playlist) < self._playlist_size:
                if self.stopped():
                    return
                self._playlist.append(self._pick_new_song())


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
            t0 = time.time()
            artist = get_tag(self._current_song['path'], 'artist')
            if artist:
                artist = artist.encode('utf-8')
            title = get_tag(self._current_song['path'], 'title')
            if title:
                title = title.encode('utf-8')
            meta = artist + ' - ' + title
            self._current_song['artist'] = artist
            self._current_song['title'] = title
            f = open(self._current_song['path'])

            nbuf = f.read(self.get_buffer_size())
            s.send(nbuf)

            self._current_song['end_time'] = time.time() + self._current_song['duration']
            t = self._current_song['end_time']
            t = time.localtime(t)
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
                if not buf:
                    break
                if t0:
                    print 'Time spent for setting data: ', time.time()-t0
                    t0 = None
                s.send(buf)
                nbuf = f.read(self.get_buffer_size())
                delay = s.delay()/1000.0
                delay = delay * 0.3
                if delay > 0.2:
                    time.sleep(delay)
            f.close()
            self._next_song()
            while not os.path.exists(self._current_song['path']):
                self._next_song()

        s.close()

    def set_buffer_size(self, bufsize):
        self._bufsize = bufsize

    def get_buffer_size(self):
        return self._bufsize

    def set_next_song(self, path):
        if os.path.exists(path):
            print 'Setting next song'
            with self._playlist_lock:
                print 'Playlist lock acquired for next song'
                self._playlist = [path] + self._playlist

    def _next_song(self):
        print 'Auto-setting next song at ', time.time()
        t0 = time.time()
        if self._current_song:
            self._song_list.insert(0, self._current_song['path'])
        del self._song_list[self._song_list_size:]
        self._current_song['path'] = self._playlist[0]
        self._current_song['start_time'] = time.time()
        artist = get_tag(self._current_song['path'], 'artist')
        f = open(self._current_song['path'])
        mf = mad.MadFile(f)
        self._current_song['duration'] = mf.total_time()/1000
        f.close()
        if artist:
            self._last_artists.append(artist)
            if self._last_artists and len(self._last_artists) > self._playlist_size:
                self._last_artists.pop(0)
        with self._playlist_lock:
            print 'Playlist lock acquired for auto-setting next song'
            self._playlist.pop(0)
        def f():
            with self._playlist_lock:
                self._playlist.append(self._pick_new_song())
        threading.Thread(target=f).start()
        print 'Next song set at ', time.time()
        print 'We spent ', time.time()-t0, ' seconds setting the next song'

    def _pick_new_song(self):
        artists = [get_tag(f, 'artist') for f in self._playlist]
        artists.extend(self._last_artists)
        choice = None
        while not choice:
            choice = random.choice(self._songs)
            artist = get_tag(choice, 'artist')
            if (not artist) or (artist in artists) or (
                choice in self._song_list):
                choice = None
        return choice

    def get_playlist(self):
        print 'Playlist requested'
        with self._playlist_lock:
            print 'Playlist lock acquired for playlist request'
            return generate_playlist(self._playlist)

    def insert_songs_into_playlist(self, index, songs):
        with self._playlist_lock:
            self._playlist[index:index] = songs

    def delete_songs_from_playlist(self, indices): 
        indices.sort(reverse=True)
        try:
            with self._playlist_lock:
                for n in indices:
                    del self._playlist[n]
        except TypeError, e:
            print e

    def set_playlist(self, playlist):
        with self._playlist_lock:
            self._playlist = playlist

    def get_collection(self):
        return self._collection

    def get_current_song(self):
        return self._current_song

    def get_time_to_end(self):
        return self._current_song['end_time'] - time.time()

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

def generate_playlist(lstFiles):
    result = []
    for filename in lstFiles:
        tags = get_tags(filename, ['artist', 'album', 'title'])
        file = open(filename)
        mf = mad.MadFile(file)
        length = mf.total_time() / 1000
        file.close()
        result.append({'path': filename, 'tags': tags, 'length': length})
    return result


def generate_collection(lstFiles, fStopped=None):
    result = {}
    for filename in lstFiles:
        if fStopped and fStopped():
            return None
        tags = get_tags(filename, ['artist', 'album', 'title'])
        file = open(filename)
        mf = mad.MadFile(file)
        length = mf.total_time() / 1000
        file.close()
        artist, album, title = tags['artist'], tags['album'], tags['title']
        if not result.has_key(artist):
            result[artist] = {}
        if not result[artist].has_key(album):
            result[artist][album] = []
        result[artist][album].append({'path': filename, 'title': title,
                                      'length': length})
    return result

#    print (parent, dirs, files)

