import socket

class Retriever:
    def __init__(self, host='localhost', port=50000):
        self._host = host
        self._port = int(port)

    def connect(self):
        self._s = open_socket(self._host, self._port)

    def disconnect(self):
        self._s.close()

    def get_playlist(self):
        pl = send(self._s, 'playlist', True)
        print pl

def open_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def send(socket, command, bReply = False):
    socket.send(command)
    if bReply:
        socket.settimeout(3)
        data = None
        i = i + 1
        try:
            data = socket.recv(BUFFER_SIZE)
        except:
            print 'Timeout'
            return data
        return data
    else:
        return None



