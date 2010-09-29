import socket

class Retriever:
    def __init__(self, host='localhost', port='50000'):
        self._host = host
        self._port = port

    def connect(self):
        self._s = connect(self._host, self._port)

    def disconnect(self):
        self._s.close()

def connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s
