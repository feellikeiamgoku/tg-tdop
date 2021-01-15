import os


def get_env(env_name):
    env = os.environ[env_name]
    return env
