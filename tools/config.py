import os
import fsutil

from os import path

def get(name, fallback = ''):
    return _config_vars.get(name, fallback)

def get_list(name):
    return get(name).split(_get_separator(name))

def init(profile):
    global _config_vars
    dir = os.environ.get('BUILDTOOL_CONFIG_DIR', '')
    if not dir:
        dir = path.join(path.expanduser('~'), '.buildtool')
    if not profile:
        profile = 'default'
    _config_vars = load(path.join(dir, profile + '.conf'))

def load(file):
    result = {}
    if not path.exists(file):
        return result
    for raw_key, value in fsutil.read_pairs(file, '='):
        key = raw_key.lower()
        if key.endswith('+'):
            key = key.rstrip('+').rstrip()
            if key in result:
                result[key] += _get_separator(key) + value
                continue
        result[key] = value
    return result

def _get_separator(option):
    if option.endswith('path'):
        return os.pathsep
    else:
        return ' '
