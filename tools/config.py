import os
import fsutil

from os import path

def get(name, fallback = ''):
    return _config_vars.get(name, fallback)

def init(profile):
    global _config_vars

    config_dir = os.environ.get('BUILDTOOL_CONFIG_DIR', '')
    config_files = ['buildtool.conf']

    if not config_dir:
        config_dir = path.join(path.expanduser('~'), '.buildtool')

    if profile:
        config_files.append('buildtool.%s.conf' % profile)

    _config_vars = {}
    for file in config_files:
        _merge_config(_config_vars, _read_config(path.join(config_dir, file)))

def _get_separator(option):
    if option.endswith('path'):
        return os.pathsep
    else:
        return ' '

def _merge_config(target, other):
    for key, value in other:
        if key.endswith('+'):
            real_key = key.rstrip('+').rstrip()
            if real_key in target:
                target[real_key] += _get_separator(real_key) + value
            else:
                target[real_key] = value
        else:
            target[key] = value

def _read_config(config_file):
    if not path.exists(config_file):
        return []
    result = []
    for key, value in fsutil.read_pairs(config_file, '='):
        entry = (key.lower(), value)
        result.append(entry)
    return result
