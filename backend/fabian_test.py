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

w = automate.WebotCtrl()
w.init()

# e = automate.ExtCtrl()
# e.compile()
# e.start()
# time.sleep(5)
# e.close()
