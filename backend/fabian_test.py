# import subprocess
# import time
# import psutil
#
# def is_program_started():
#     return "webots-bin" in (p.name() for p in psutil.process_iter())
#
#
# subprocess.Popen(["make", "clean"], cwd="../webots/controllers/internal")
# subprocess.Popen(["make", "all"], cwd="../webots/controllers/internal")
#
# print(is_program_started())
# subprocess.Popen(["webots", "../webots/worlds/testworld_prototype.wbt"])
#
# print("started")
# time.sleep(5.0)
# print("kill")
#
# print(is_program_started())
#
# subprocess.Popen(["pkill", "webots-bin"])
#
# time.sleep(3.0)
#
# print(is_program_started())

import time
import automate
import subprocess



w = automate.WebotCtrl()
print("init")
w.init()
print("send data")
w.start_env()
print("recv data")
time.sleep(1)
w.get_metadata()
print("print data")
w.print()
print("sleeping")
time.sleep(5.0)
print("exit")

# e = automate.ExtCtrl()
# e.compile()
# e.start()
# time.sleep(5)
# e.close()
