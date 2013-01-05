import os, glob, shutil

from os import path

def _strip_include(line):
    items = line.split(None, 1)
    if len(items) != 2:
        raise ValueError('Invalid include directive: ' + line)
    return items[1].lstrip()

def resolve_include(src, file):
    ext = path.splitext(src)[1]
    result = path.normpath(path.join(path.dirname(src), file + ext))
    if not path.exists(result):
        raise ValueError('Included file is not found: ' + result)
    return result

def make_dir(d):
    if not path.exists(d):
        os.makedirs(d)

def safe_remove(file):
    if path.exists(file):
        os.remove(file)

def safe_remove_dir(dir):
    if path.exists(dir):
        shutil.rmtree(dir)

def glob_remove(pattern):
    for item in glob.iglob(pattern):
        os.remove(item)

def write_stamp(file):
    with open(file, 'w') as f:
        f.write('stamp file for buildtool')

def read_file(file):
    with open(file, 'r') as f:
        return f.read()

def read_lines(file):
    result = []
    with open(file, 'r') as f:
        for line in f:
            sline = line.strip()
            if sline.startswith('!include'):
                inc_file = resolve_include(file, _strip_include(sline))
                result.extend(read_lines(inc_file))
            elif sline and not sline.startswith('#'):
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
