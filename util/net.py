import socket
import threading

def receive(socket, fStopped=None, bClose=True, bufsize=4096):
    if fStopped:
        socket.settimeout(1)
    result = ''
    data = None
    while 1:
        try:
            print 'Trying to receive...'
            data = socket.recv(bufsize)
            print 'Data received!'
            if not data:
                if bClose:
                    socket.close()
                return result
            else:
                result += data
                data = None
        except:
            if fStopped and fStopped():
                    if bClose:
                        socket.close()
                    return result
            if result:
                if data:
                    result += data
                    data = None
                    continue
                else:
                    if bClose:
                        socket.close()
                    return result

def send(socket, data, fStopped=None, bClose=True):
    if fStopped:
        socket.settimeout(1)
    total = 0
    size = len(data)
    while 1:
        try:
            sent = socket.send(data[total:])
            total += sent
            if sent == size:
                if bClose:
                    socket.close()
                return True
        except AttributeError, e:
            if fStopped and fStopped():
                if bClose:
                    socket.close()
                return False

def command(socket, command, fStop=None):
    send(socket, command, fStop, False)
    return receive(socket, fStopped=fStop)
