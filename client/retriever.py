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

    def get_playlist(self):
        s = open_socket(self._host, self._port)
        pl = net.command(s, 'playlist')
        pl = pack.unpack(pl)
        return pl

    def get_collection(self):
        s = open_socket(self._host, self._port)
        pl = net.command(s, 'collection')
        pl = pack.unpack(pl)
        return pl

def open_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def send(host, port, command, bReply = False):
    socket = open_socket(host, port)
    socket.send(command)
    ret = None
    if bReply:
        #socket.settimeout(1)
        data = ''
        try:
            while 1:
                buf = socket.recv(BUFFER_SIZE)
                if not buf:
                    print 'EOF encountered!'
                    break
                data += buf
                print 'Received data length: %i' % (len(buf),)
        except Exception, e:
            print 'Exception!', e
            ret = data
        ret = data
    else:
        ret = None
    socket.close()
    return ret



