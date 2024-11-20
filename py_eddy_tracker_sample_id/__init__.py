from os import path


def get_remote_demo_sample(name):
    return path.join(path.dirname(__file__), name)
