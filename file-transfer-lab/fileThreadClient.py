#! /usr/bin/env python3

# File client program
import socket, sys, re, os
import params
from framedSock import FramedStreamSock
from threading import Thread, Lock

CHUNK_SIZE = 100

if len(sys.argv) < 1:
    print("Usage: fileClient <filename>")
    exit()

filename = sys.argv[0]
print(sys.argv)
del sys.argv[0]

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


def put(fs, filename):
    if not os.path.exists(filename):
    	print ("File input %s doesn't exist! Exiting" % filename)
    	return

    if os.path.getsize(filename) > 0:
        fs.sendmsg(bytes(filename, 'utf-8'))		# send the files name
        with open(filename, 'rb') as file:
            payload = file.read(CHUNK_SIZE)
            while payload:
                fs.sendmsg(payload)
                payload = file.read(CHUNK_SIZE)
        return
    else:
    	print ("File input %s is empty! Exiting" % filename)


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

lock = Lock()
class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug, filename):
        Thread.__init__(self, daemon=False)

        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()


    def run(self):
        s = None
        for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_INET, socket.SOCK_STREAM, 0, 0):
           af, socktype, proto, canonname, sa = res
           try:
                print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
                s = socket.socket(af, socktype, proto)
           except socket.error as msg:
                print(msg)
                s = None
                continue
           try:
                print(" attempting to connect to %s" % repr(sa))
                s.connect(sa)
           except socket.error as msg:
                print(msg)
                s.close()
                s = None
                continue
           break

        if s is None:
           print('could not open socket')
           lock.release()
           sys.exit(1)

        fs = FramedStreamSock(s, debug=debug)

        # critical section
        lock.acquire()
        print("\nput ", filename)
        put(fs, filename)
        print("Transfer complete\n")
        lock.release()

for i in range(10):
    ClientThread(serverHost, serverPort, debug, filename)
