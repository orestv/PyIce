import socket
import threading
import re
import time
import pack

SOCKET_TIMEOUT = 1

def receive(s, fStopped=None, bClose=True, bufsize=2048, fPercentUpdate=None):
    if fStopped:
        s.settimeout(SOCKET_TIMEOUT)
    result = ''
    data = None
    nToReceive = None
    nMetadataLength = 0

    while 1:
        try:
            data = s.recv(bufsize)
        except:
            if fStopped and fStopped():
                if bClose:
                    s.close()
                return None
        if fStopped and fStopped():
            if bClose:
                s.close()
            return None
        if data:
            if not nToReceive:
                match = re.search('[0-9]*', data)
                if not match:
                    return None
                tmp = match.group(0)
                nMetadataLength = len(tmp)+1
                nToReceive = float(int(tmp) + nMetadataLength)
            result += data
            data = None
            if fPercentUpdate:
                fPercentUpdate(len(result)/nToReceive)
            if len(result) >= nToReceive:
                result = result[nMetadataLength:]
                break
        else:
            time.sleep(SOCKET_TIMEOUT)
            continue
    return pack.unpack(result)

def send(socket, data, fStopped=None, bClose=True, fPercentUpdate=None):
    if fStopped:
        socket.settimeout(SOCKET_TIMEOUT)
    total = 0
    data = pack.pack(data)
    size = len(data)
    data = str(size) + ';' + data
    size = float(len(data))
    while 1:
        try:
            sent = socket.sendall(data[total:])
            total += sent
            if fPercentUpdate:
                fPercentUpdate(total/size)
            if total >= size:
                if bClose:
                    socket.close()
                return True
        except AttributeError, e:
            if fStopped and fStopped():
                if bClose:
                    socket.close()
                return False

def command(socket, command, fStop=None, fUpdate=None):
    send(socket, command, fStop, False, fPercentUpdate=fUpdate)
    return receive(socket, fStopped=fStop, fPercentUpdate=fUpdate)
