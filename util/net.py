import socket
import threading
import re
import time

SOCKET_TIMEOUT = 0.9

def receive(s, fStopped=None, bClose=True, bufsize=4096):
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
            print 'Exception in recv!'
            if fStopped and fStopped():
                if bClose:
                    s.close()
                return None
        print 'Looped...'
        if fStopped and fStopped():
            if bClose:
                s.close()
            return None
        if data:
            print 'Data isn''t null!'
            if not nToReceive:
                match = re.search('[0-9]*', data)
                if not match:
                    return None
                tmp = match.group(0)
                nMetadataLength = len(tmp)+1
                print 'Metadata length: %i' % (nMetadataLength,)
                print 'tmp: ', tmp
                print 'Integered tmp: %i' % (int(tmp), )
                nToReceive = int(tmp) + nMetadataLength
                print 'Declared length: %i' % (nToReceive,)
            result += data
            data = None
            if len(result) >= nToReceive:
                return result[nMetadataLength:]
        else:
            time.sleep(SOCKET_TIMEOUT)
            continue

def send(socket, data, fStopped=None, bClose=True):
    if fStopped:
        socket.settimeout(SOCKET_TIMEOUT)
    total = 0
    size = len(data)
    data = str(size) + ';' + data
    size = len(data)
    while 1:
        try:
            #TODO: remote sleep
            print 'Sleeping before sending...'
            time.sleep(0.3)
            sent = socket.send(data[total:])
            print 'Sent: %i' % (sent,)
            total += sent
            print 'Total sent: %i' % (total,)
            if total >= size:
                print 'Total >= size for sending'
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
