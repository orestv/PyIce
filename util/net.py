import socket
import threading

SOCKET_TIMEOUT = 0.5

def receive(socket, fStopped=None, bClose=True, bufsize=4096):
    if fStopped:
        socket.settimeout(SOCKET_TIMEOUT)
    result = ''
    data = None
    while 1:
        try:
            data = socket.recv(bufsize)
            if not data:
                if bClose:
                    socket.close()
                return result
            else:
                result += data
                data = None
        except:
            if fStopped:
                print 'Inside recv function, are we  stopped? ' + str(fStopped())
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
        socket.settimeout(SOCKET_TIMEOUT)
    total = 0
    size = len(data)
    while 1:
        try:
            sent = socket.send(data[total:])
            total += sent
            if total >= size:
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
