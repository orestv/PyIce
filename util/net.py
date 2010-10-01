import socket
import threading

def receive(socket, bufsize=4096, fStopped=None):
    if fStopped:
        socket.settimeout(1)
    result = ''
    while 1:
        try:
            data = socket.recv(bufsize)
            if not data:
                socket.close()
                return result
            else:
                result += data
        except AttributeError, e:
            if fStopped and fStopped():
                socket.close()
                return result+data

def send(socket, data, fStopped=None):
    if fStopped:
        socket.settimeout(1)
    total = 0
    size = len(data)
    while 1:
        try:
            sent = socket.send(data[total:])
            total += sent
            if sent == size:
                socket.close()
                return True
        except AttributeError, e:
            if fStopped and fStopped():
                socket.close()
                return False
