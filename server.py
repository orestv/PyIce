#!/usr/bin/python2
#coding: utf-8
import socket
import pickle
import StringIO
import threading

BUFFER_SIZE = 65536

def pack(obj):
    buf = StringIO.StriogIO()
    pickle.dump(obj, buf)
    buf.seek(0)
    result = buf.getvalue()
    buf.close()
    return result


class Listener(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self._server = server
        self._kill = False
        self._stop = threading.Event()

    def stop(self):
        print 'Listener stop called'
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        print 'Listener started'
        host = ''
        port = 50001
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
                    s.close()
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
        self._server = server
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        print 'client connected'
        print self._client
        self._client.send('Password:\r\n')
        self._client.settimeout(1)
        while 1:
            try:
                data = self._client.recv(BUFFER_SIZE)
                data = data[:len(data)-2]
                print data, len(data), data=='asdf'
                if data == 'exit':
                    self._client.close()
                    return
                elif data == 'playlist':
                    pl = self._server.get_playlist()
                    for s in pl:
                        self._client.send(s + '\r\n')
                    #self._client.send(str(self._server.get_playlist()))
            except:
                if self.stopped():
                    print 'Client stopped!'
                    self._client.close()
                    return
