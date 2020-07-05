import time

from james import James
from timmy import Timmy
import webotsgym.automate as automate

print("start webot")
w = automate.WebotCtrl()
w.init()

print("start environment")
w.start_env()


james = James()
for _ in range(200):
    james.action()

print("wating for reset")
time.sleep(3.0)

w.reset_environment()

# print("random actions")
# timmy = Timmy()
# for _ in range(20):
#     timmy.action()

time.sleep(500.0)

print("kill")
w.close()
# e.close()
