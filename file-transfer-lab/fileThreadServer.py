#! /usr/bin/env python3
import os, socket, params, re, time
from threading import Thread, Lock
from framedSock import FramedStreamSock

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

# new name of file not defined and  file name in use, iterate to an unused name
def getFilename(filename):
    i = 1
    filename = filename.decode()
    if os.path.exists(filename):
        name = filename.split(".")
        match = re.match("(^[^\(]+)(\([\d+]\))", name[0]) # look for numbered file pattern
    if match:
        filename, index = match.groups()
        while os.path.exists(filename):
            filename = filename + "("+index+")" + name[1]
            index += 1
    else:
        while os.path.exists(filename):
            filename = name[0] + "("+str(i)+")." + name[1]
            i += 1
    return filename


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)


def animation():
    while True:
        for anim in ["(-)", "(\\)", "(|)", "(/)"]:
            yield anim


lock = Lock()
class ServerThread(Thread):
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()


    def run(self):
        lock.acquire()
        filename = self.fsock.receivemsg()   			# recieving the file name

        filename = getFilename(filename)
        anim = animation()
        with open(filename, 'wb') as outf:
            while True:
                payload = self.fsock.receivemsg()
                print("Receiving ", next(anim), sep=' ', end='\r', flush=True)
                time.sleep(0.01)
                if not payload:
                    break
                outf.write(payload)
        lock.release()

while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
