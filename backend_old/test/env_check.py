if __name__ == "__main__":
    import sys
    sys.path.insert(0, '..')
    from stable_baselines.common.env_checker import check_env
    import webotsgym.environment as environment
    import webotsgym.automate as automate
    ctr = automate.ExtCtrl()
    ctr.init()
    env = environment.webotsgym(request_start_data=False)
    check_env(env)
    ctr.close()
    print("========== END OF TEST ==========")
