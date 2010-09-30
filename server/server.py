#!/usr/bin/python2
#coding: utf-8
import os, sys
sys.path.append('/home/seth/dev/py/pyice/util/')
import socket
import pickle
import StringIO
import threading
import pack

BUFFER_SIZE = 65536

class Listener(threading.Thread):
    def __init__(self, server, port=50000):
        threading.Thread.__init__(self)
        self._server = server
        self._kill = False
        self._stop = threading.Event()
        self._port = int(port)

    def stop(self):
        print 'Listener stop called'
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        print 'Listener started'
        host = ''
        port = self._port
        backlog = 5
        size = 1024
        clients = []

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.settimeout(1)
        s.listen(backlog)

        while 1:
            try:
                client, address = s.accept()
                c = Connector(client, self._server)
                c.start()
                clients.append(c)
            except:
                if self.stopped():
                    print 'Listener stopped'
                    self.kill_clients(clients)
                    s.shutdown(1)
                    s = None
                    print 'Clients killed, stream closed'
                    return

    def kill_clients(self, clients):
        for c in clients:
            print 'Client...'
            c.stop()


class Connector(threading.Thread):
    def __init__(self, client, server):
        threading.Thread.__init__(self)
        self._client = client
        self._client.setblocking(0)
        self._server = server
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        print 'client connected'
        print self._client
        self._client.settimeout(1)
        while 1:
            try:
                data = self._client.recv(BUFFER_SIZE)
                data = data.rstrip('\r\n')
                print data, len(data)
                if not data:
                    self._client.close()
                    return
                if data == 'exit':
                    print 'Exit message received'
                    self._client.close()
                    return
                elif data == 'collection':
                    print 'Collection requested...'
                    col = self._server.get_collection()
                    s = pack.pack(col)
                    print 'Collection length: %i' % (len(s),)
                    n = len(s)
                    sent = 0
                    while 1:
                        sent = sent + self._client.send(s[sent:])
                        if sent == n:
                            break
                    print 'Sent %i bytes' % (sent,)
                    self._client.close()
                    return
                elif data == 'playlist':
                    pl = self._server.get_playlist()
                    s = pack.pack(pl)
                    print 'Playlist\'s length: ', len(s)
                    n = len(s)
                    sent = 0
                    while 1:
                        sent = sent + self._client.send(s[sent:])
                        if sent == n:
                            break
                    print 'Sent %i bytes' % (sent,)
                    self._client.close()
                    return
            except AttributeError, e:
                print e
                if self.stopped():
                    print 'Client stopped!'
                    self._client.close()
                    return
