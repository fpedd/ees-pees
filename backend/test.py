import environment

wenv = environment.WebotsEnv()
for i in range(10000):
    wenv.step()
