import os

def pre_dir(filename):
    # get the previous directory
    return os.path.dirname(filename)


print(pre_dir('src/importsearch/test.py')) # src/importsearch