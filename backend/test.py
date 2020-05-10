import environment

wenv = environment.WebotsEnv()
for i in range(1000):
    wenv.step()
