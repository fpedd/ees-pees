# https://www.journaldev.com/17401/python-struct-pack-unpack
# https://docs.python.org/3/library/struct.html

import socket
import struct


IP = "127.0.0.1"
CONTROL_PORT = 6969
BACKEND_PORT = 6970

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)
sock.bind((IP, BACKEND_PORT))

while True:
    data, addr = sock.recvfrom(2048)
    # print "received message:", data, len(data)
    # data = data + "tsetset"
    myit = struct.iter_unpack('f', data[8:])
    # myit = struct.iter_unpack('ff', data)
    for x in myit:
        print(x)
    sock.sendto(data, (IP, CONTROL_PORT))
