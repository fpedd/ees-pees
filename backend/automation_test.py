import time
import subprocess

from james import James
import webotsgym.automate as automate

print("start webot")
w = automate.WebotCtrl()
w.init()

# print("start external")
# e = automate.ExtCtrl()
# e.init()

print("start environment")
w.start_env()

print("random actions")
timmy = Timmy()
for _ in range(20):
    timmy.action()

print("wating for reset")
time.sleep(3.0)

w.reset_environment()

print("random actions")
timmy = Timmy()
for _ in range(20):
    timmy.action()

time.sleep(500.0)

print("kill")
w.close()
# e.close()
