#!/usr/bin/python2
#coding: utf-8
import os, sys
sys.path.append('..')
import socket
import pickle
import StringIO
import threading
from pyice.util import net
import re
import time

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
        self._clients = []

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.settimeout(1)
        s.listen(backlog)

        while 1:
            try:
                client, address = s.accept()
                c = Connector(client, self._server, self.client_closed)
                c.start()
                self._clients.append(c)
            except:
                if self.stopped():
                    print 'Listener stopped'
                    self.kill_clients()
                    s.shutdown(1)
                    s = None
                    print 'Clients killed, stream closed'
                    return

    def client_closed(self, client):
        print 'Client called self-destruct func'
        while client in self._clients:
            print 'Removing client - self-destruction!'
            self._clients.remove(client)

    def kill_clients(self):
        for c in self._clients:
            print 'Client...'
            c.stop()


class Connector(threading.Thread):
    def __init__(self, client, server, onClose=None):
        threading.Thread.__init__(self)
        self._onClose = onClose
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
        try:
            data = net.receive(self._client, fStopped=self.stopped, bClose=False)
            if not data:
                self._client.close()
            if data[0] == 'exit':
                print 'Exit message received'
                self._client.close()

            elif data[0] == 'get_buffer_size':
                print 'Buffer size requested...'
                bufsize = self._server.get_buffer_size()
                net.send(self._client, bufsize, self.stopped, True)

            elif data[0] == 'set_buffer_size':
                print 'Setting buffer size!'
                buf = data[1]
                self._server.set_buffer_size(buf)
                net.send(self._client, True, self.stopped, True)

            elif data[0] == 'collection':
                print 'Collection requested...'
                col = self._server.get_collection()
                net.send(self._client, col, self.stopped, True)

            elif data[0] == 'playlist':
                pl = self._server.get_playlist()
                net.send(self._client, pl, self.stopped, True)
            else:
                print 'Invalid command received: ' + data
                self._client.close()

        except AttributeError, e:
            print e
            if self.stopped():
                print 'Client stopped!'
                self._client.close()
        if self._onClose:
            self._onClose(self)

