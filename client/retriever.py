import socket
import sys
sys.path.append('/home/seth/dev/py/pyice/util/')
import pack

BUFFER_SIZE = 8192

class Retriever:
    def __init__(self, host='localhost', port=50000):
        self._host = host
        self._port = int(port)

    def get_playlist(self):
        pl = send(self._host, self._port, 'playlist', True)
        pl = pack.unpack(pl)
        return pl

    def get_collection(self):
        pl = send(self._host, self._port, 'collection', True)
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



