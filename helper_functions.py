import numpy as np
import os


def get_point_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))


def try_make_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
