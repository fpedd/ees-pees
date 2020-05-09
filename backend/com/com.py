import socket
import struct
import time

############## Settings ##############
IP = "127.0.0.1"
CONTROL_PORT = 6969
BACKEND_PORT = 6970
TIME_OFFSET_ALLOWED = 1.0 # in seconds
PACKET_SIZE = 1496   # (8 + 8 + 3*4 + 3*4 + 3*4 + DIST_VECS*4 + 4)
DIST_VECS = 360

sock = None


############## Receiving ##############
buffer_in = None
msg_cnt_in = 0
time_in = None
target_gps_in = [None] * 3
actual_gps_in = [None] * 3
compass_in = [None] * 3
distance_in = [None] * DIST_VECS
touching_in = None

def getCount():
    return struct.unpack('Q', buffer_in[0:8])[0]

def getTime():
    return struct.unpack('d', buffer_in[8:16])[0]

def getTargetGPS():
    return struct.unpack('3f', buffer_in[16:28])

def getActualGPS():
    return struct.unpack('3f', buffer_in[28:40])

def getCompass():
    return struct.unpack('3f', buffer_in[40:52])

def getDistance():
    return struct.unpack("{}f".format(DIST_VECS), buffer_in[52:(52+DIST_VECS*4)])

def getTouching():
    return struct.unpack("I", buffer_in[(52+DIST_VECS*4):(56+DIST_VECS*4)])[0]

def recv():
    global buffer_in
    buffer_in, addr = sock.recvfrom(PACKET_SIZE)

    if PACKET_SIZE < len(buffer_in):
        print("ERROR: recv did not get full packet", len(buffer_in))
        return

    if IP != addr[0]:
        print("ERROR: recv did from wrong address", addr)
        return

    global msg_cnt_in
    msg_cnt_in += 2
    if getCount() != msg_cnt_in:
        print("ERROR: recv wrong msg count, is ", getCount(), " should ", msg_cnt_in)
        msg_cnt_in = getCount()
        return

    if abs(time.time() - getTime()) > TIME_OFFSET_ALLOWED:
        print("ERROR: recv time diff to big local ", time.time() ," remote ",
              getTime(), " diff ", abs(time.time() - getTime()))
        return

    return len(buffer_in)


############## Transmitting ##############
msg_cnt_out = 1
heading_out = None
speed_out = None

def setHeading(heading):
    if heading < 0 or heading > 360:
        print("ERROR: heading invalid", heading)
    else:
        global heading_out
        heading_out = heading

def setSpeed(speed):
    if speed < -100 or speed > 100:
        print("ERROR: speed invalid", speed)
    else:
        global speed_out
        speed_out = speed

def send():
    global msg_cnt_out
    global sock
    data = struct.pack('Qdff', msg_cnt_out, time.time(), heading_out, speed_out)
    ret = sock.sendto(data, (IP, CONTROL_PORT))
    if ret == len(data):
        msg_cnt_out += 2
    else:
        printf("ERROR: could not send message, is ", ret, " should ", len(data))

# def send(heading, speed):
#     setHeading(heading)
#     setSpeed(speed)
#     send()


############## General ##############
def reset():
    global buffer_in
    buffer_in = None
    global msg_cnt_in
    msg_cnt_in = 0
    global time_in
    time_in = None
    global target_gps_in
    target_gps_in = [None] * 3
    global actual_gps_in
    actual_gps_in = [None] * 3
    global compass_in
    compass_in = [None] * 3
    global distance_in
    distance_in = [None] * DIST_VECS
    global touching_in
    touching_in = None

    global msg_cnt_out
    msg_cnt_out = 1
    global heading_out
    heading_out = None
    global speed_out
    speed_out = None

def init():
    reset()
    global sock
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
    sock.bind((IP, BACKEND_PORT))
