#!/usr/bin/python2
#coding: utf-8

import socket, pickle, StringIO

host = 'localhost'
port = 50000
size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

data = s.recv(4096)
s.close()

buf = StringIO.StringIO(data)

dict = pickle.load(buf)

print dict
