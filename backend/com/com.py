import socket

IP = "127.0.0.1"
CONTROL_PORT = 6969
BACKEND_PORT = 6970

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((IP, BACKEND_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data
    data = data + "tsetset"
    sock.sendto(data, (IP, CONTROL_PORT))
