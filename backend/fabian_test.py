import time
import automate
import subprocess

w = automate.WebotCtrl()
e = automate.ExtCtrl()
print("init")
e.init()
w.init()
time.sleep(5)
print("send data")
time.sleep(3)
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
