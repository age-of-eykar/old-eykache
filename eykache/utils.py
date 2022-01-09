import os
import json
import collections.abc


def get_path(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
