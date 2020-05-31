import time
import automate
import subprocess

w = automate.WebotCtrl()
print("init")
w.init()
print("send data")
w.start_env()
time.sleep(1)
print("recv data")
w.get_metadata()
print("print data")
w.print()
print("sleeping")
time.sleep(3.0)
print("kill")
w.close_program()
