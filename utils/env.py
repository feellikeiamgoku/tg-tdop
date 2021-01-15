import os


def get_env(env_name):
    env = os.getenv(env_name)
    if env:
        return env
    else:
        raise KeyError(f'Please set required env variable \'{env_name}\'')
