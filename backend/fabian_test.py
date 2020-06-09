import time
import automate
import subprocess

w = automate.WebotCtrl()
print("init")
w.init()
time.sleep(1)
print("send data")
time.sleep(1)
e = automate.ExtCtrl()
e.init()
w.start_env()
print("recv data")
w.get_metadata()
print("print data")
w.print()
print("sleeping")
time.sleep(3.0)
print("kill")
w.close()
e.close()
