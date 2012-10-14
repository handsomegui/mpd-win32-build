import os, glob

from os import path

def make_dir(d):
    if not path.exists(d):
        os.makedirs(d)

def safe_remove(file):
    if path.exists(file):
        os.remove(file)

def glob_remove(pattern):
    for item in glob.iglob(pattern):
        os.remove(item)

def write_marker(file):
    with open(file, 'w') as f:
        f.write('marker file for buildtool')

def read_file(file):
    with open(file, 'r') as f:
        return f.read()

def read_lines(file):
    result = []
    with open(file, 'r') as f:
        for line in f:
            sline = line.strip()
            if sline and not sline.startswith('#'):
                result.append(sline)
    return result

def read_pairs(file, separator):
    result = []
    for line in read_lines(file):
        items = line.split(separator, 2)
        if len(items) != 2:
            raise ValueError('Unable to parse pair: ' + line)
        pair = (items[0].rstrip(), items[1].lstrip())
        result.append(pair)
    return result
