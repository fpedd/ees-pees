import com
import time

com.init()

# while True:
#     com.setSpeed(12.34)
#     com.setHeading(56.78)
#     com.send()
#     time.sleep(0.1)   # wait 100ms

while True:
    com.recv()
    print(com.getCount())
    print(com.getTime())
    print(com.getTargetGPS())
    print(com.getActualGPS())
    print(com.getCompass())
    print(com.getDistance()[0::100])  # only print every 100th element
    print(com.getTouching())
