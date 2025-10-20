import numpy as np


def determine_fs(data):
    fs = 1 / np.median(np.diff(data))
    print("fs - ", fs)
    return fs
