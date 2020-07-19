if __name__ == "__main__":
    """Function to check if the environment is compatible with openai gym."""
    import sys
    sys.path.insert(0, '../../backend')
    from stable_baselines.common.env_checker import check_env
    import webotsgym as wg

    ctr = wg.com.automate.ExtCtrl()
    ctr.init()
    env = wg.WbtGym(request_start_data=False)
    check_env(env)
    ctr.close()
    print("========== END OF TEST ==========")
