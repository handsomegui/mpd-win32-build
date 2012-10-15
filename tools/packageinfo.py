import os
import config, cmdutil, fsutil

from os import path

class PackageInfo:
    def _read_dependencies(self):
        deps_file = path.join(self.script_dir, 'depends.txt')
        if not path.exists(deps_file):
            return []
        return fsutil.read_lines(deps_file)

    def dependency_map(self):
        result = {}
        next = [self.name]
        while next:
            name = next.pop()
            if name in result:
                continue
            deps = get(name)._read_dependencies()
            result[name] = deps
            next.extend(deps)
        return result

    def artifacts(self):
        if not path.exists(self.artifacts_file):
            return []
        return fsutil.read_pairs(self.artifacts_file, '->')

    def __init__(self, name):
        if not _check_name(name):
            raise ValueError('Invalid package name ' + name)

        self.name = name
        self.short_name = name.split('-')[0]
        self.dist_name = _get_dist_name(name)
        self.dist_host = _dist_host

        self.script_dir = path.join(_package_dir, name)
        self.build_dir  = path.join(_build_dir, name)
        self.install_dir = path.join(_install_dir, name)
        self.cache_dir  = path.join(_cache_dir, name)
        self.dist_dir = _dist_dir

        if not path.exists(self.script_dir):
            raise ValueError('Directory is not found for package ' + name)

        self.build_file = path.join(self.script_dir, 'build.py')
        self.make_file = path.join(_work_dir, name + '.mk')
        self.log_file = path.join(_log_dir, name + '.log')
        self.artifacts_file = path.join(self.install_dir, 'artifacts.txt')
        self.version_file = path.join(self.install_dir, 'version.txt')

        if not path.exists(self.build_file):
            raise ValueError('Builder is not found for package ' + name)

        self.crossbuild = _crossbuild
        self.crossbuild_build = _crossbuild_build
        self.crossbuild_host = _crossbuild_host

def init(base_dir, profile):
    _init_crossbuild()
    _init_base_dir(base_dir, profile)
    _init_work_dir()

def _init_crossbuild():
    global _crossbuild
    global _crossbuild_build
    global _crossbuild_host
    global _dist_host

    _crossbuild_build = config.get('build')
    _crossbuild_host = config.get('host')

    _crossbuild = (not cmdutil.on_windows) or _crossbuild_build or _crossbuild_host
    if _crossbuild:
        if not _crossbuild_build:
            raise ValueError('Cross-compiling but build triplet is not set')
        if not _crossbuild_host:
            raise ValueError('Cross-compiling but host triplet is not set')

    if _crossbuild and (_crossbuild_host.startswith('amd64') or _crossbuild_host.startswith('x86_64')):
        _dist_host = 'win64'
    else:
        _dist_host = 'win32'

def _init_base_dir(base_dir, profile):
    global _base_dir
    global _package_dir
    global _cache_dir
    global _work_dir

    _base_dir = _adjust_path(base_dir)
    _package_dir = path.join(_base_dir, 'packages')

    if not path.exists(_package_dir):
        raise ValueError('Packages directory is not found: ' + _package_dir)
        
    if profile:
        work = 'work-' + profile
    else:
        work = 'work'

    _cache_dir = _resolve('cache_dir', 'cache')
    _work_dir = _resolve('work_dir', work)

    fsutil.make_dir(_work_dir)
    fsutil.make_dir(_cache_dir)

def _init_work_dir():
    global _build_dir
    global _dist_dir
    global _install_dir
    global _log_dir

    _build_dir = path.join(_work_dir, 'build')
    _dist_dir = path.join(_work_dir, 'dist')
    _install_dir = path.join(_work_dir, 'install')
    _log_dir = path.join(_work_dir, 'log')

    fsutil.make_dir(_build_dir)
    fsutil.make_dir(_dist_dir)
    fsutil.make_dir(_install_dir)
    fsutil.make_dir(_log_dir)

def _resolve(var_name, fallback):
    user_dir = config.get(var_name)
    if user_dir:
        if path.isabs(user_dir):
            result = user_dir
        else:
            result = path.join(_base_dir, user_dir)
    else:
        result = path.join(_base_dir, fallback)
    return _adjust_path(result)

def _adjust_path(p):
    result = path.abspath(p)
    if result.find(' ') >= 0:
        raise ValueError('Path contains spaces, unable to continue: ' + result)
    return result

def _check_name(target):
    if target=='':
        return False
    for ch in target:
        if (not ch.isalnum()) and ch!='-' and ch!='_':
            return False
    return True
    
def _get_dist_name(name):
    release_suffix = '-release'
    if name.endswith(release_suffix):
        return name[0:-len(release_suffix)]
    return name

def get(name):
    return PackageInfo(name)

def get_packages():
    return os.listdir(_package_dir)
