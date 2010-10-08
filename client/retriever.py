import socket
import sys
sys.path.append('..')
from pyice.util import pack
from pyice.util import net

BUFFER_SIZE = 8192

class Retriever:
    def __init__(self, host='localhost', port=50000):
        self._host = host
        self._port = int(port)
        s = open_socket(self._host, self._port)
        net.send(s, ('exit',))

    def _socket(self):
        return open_socket(self._host, self._port)

    def get_playlist(self, fStopped=None):
        s = self._socket()
        pl = net.command(s, ('playlist',), fStopped)
        return pl

    def get_collection(self, fStopped=None):
        s = self._socket()
        pl = net.command(s, ('collection',), fStopped)
        return pl

    def get_buffer_size(self):
        s = self._socket()
        b = net.command(s, ('get_buffer_size',))
        return b

    def get_current_song(self, fStopped=None):
        s = self._socket()
        song = net.command(s, ('get_current_song',), fStopped)
        return song

    def set_next_song(self, path):
        s = self._socket()
        net.send(s, ('set_next_song', path))
        return

    def set_buffer_size(self, buffer_size):
        s = self._socket()
        #ret = net.command(s, 'set_buffer_size:' )
        ret = net.command(s, 'set_buffer_size:%i' % (buffer_size,))
        ret = pack.unpack(ret)
        return ret

def open_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s
