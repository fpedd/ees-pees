import time
import automate
import subprocess

from james import RndWebotAgent

print("start webot")
w = automate.WebotCtrl()
w.init()

print("start external")
e = automate.ExtCtrl()
e.init()

print("start environment")
w.start_env()

print("print data")
w.print()

print("random actions")
timmy = RndWebotAgent()
for _ in range(1000):
    timmy.action()

print("sleeping")
time.sleep(500.0)

print("kill")
w.close()
e.close()
