import os, glob
import config, cmdutil, fsutil

from os import path

class PackageInfo:
    def _read_dependencies(self):
        deps_file = self._resolve_script('depends.txt')
        if not deps_file:
            return []
        return fsutil.read_lines(deps_file)

    def _read_artifacts(self):
        if not path.exists(self.artifacts_file):
            return []
        return fsutil.read_pairs(self.artifacts_file, '->')

    def _resolve_script(self, name):
        if self.variant_name:
            name = self.variant_name + '-' + name
        file = path.join(self.script_dir, name)
        if path.exists(file):
            return file
        return None

    def dependency_map(self):
        if self.dep_map:
            return self.dep_map
        result = {}
        next = [self.name]
        while next:
            name = next.pop()
            if name in result:
                continue
            deps = get(name)._read_dependencies()
            result[name] = deps
            next.extend(deps)
        self.dep_map = result
        return result

    def artifacts(self):
        result = {}
        for name in self.dependency_map().iterkeys():
            for source, target in get(name)._read_artifacts():
                result[source] = target
        return result

    def version(self):
        if not path.exists(self.version_file):
            raise ValueError('Version file \'%s\' is not found' % self.version_file)
        return fsutil.read_file(self.version_file).strip()

    def __init__(self, name):
        if not valid_name(name):
            raise ValueError('Invalid package name: ' + name)

        self.name = name
        self.short_name, self.variant_name, self.dist_name = _decode_name(name)
        self.dist_host = _dist_host

        self.script_dir = path.join(_package_dir, self.short_name)
        self.build_dir  = path.join(_build_dir, name)
        self.install_dir = path.join(_install_dir, name)
        self.cache_dir  = path.join(_cache_dir, name)
        self.dist_dir = _dist_dir

        if not path.exists(self.script_dir):
            raise ValueError('Directory is not found for package ' + name)

        self.build_file = self._resolve_script('build.py')
        self.log_file = path.join(_log_dir, name + '.log')
        self.artifacts_file = path.join(self.install_dir, 'artifacts.txt')
        self.version_file = path.join(self.install_dir, 'version.txt')

        if not self.build_file:
            raise ValueError('Builder is not found for package ' + name)

        self.crossbuild = _crossbuild
        self.crossbuild_build = _crossbuild_build
        self.crossbuild_host = _crossbuild_host
        
        self.dep_map = None

_info_cache = {}

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

    _cache_dir = _resolve_dir('cache_dir', 'cache')
    _work_dir = _resolve_dir('work_dir', work)

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

def _resolve_dir(var_name, fallback):
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
    
def _decode_name(name):
    items = name.split('-', 1)
    short_name = items[0]
    if len(items) > 1:
        variant_name = items[1]
    else:
        variant_name = ''
    if variant_name != 'release':
        dist_name = name
    else:
        dist_name = short_name
    return short_name, variant_name, dist_name

def _get_package_variants(name):
    suffix = '-build.py'
    result = []
    package_dir = path.join(_package_dir, name)
    if path.exists(path.join(package_dir, name)):
        return [name]
    for builder in glob.iglob(path.join(package_dir, '*' + suffix)):
        builder_base = path.basename(builder)
        variant = builder_base[0:-len(suffix)]
        result.append(name + '-' + variant)
    return result

def valid_name(name):
    if name == '':
        return False
    for ch in name:
        if (not ch.isalnum()) and ch!='-' and ch!='_':
            return False
    return True

def get(name):
    global _info_cache
    if name in _info_cache:
        return _info_cache[name]
    result = PackageInfo(name)
    _info_cache[name] = result
    return result

def get_work_dir():
    return _work_dir

def get_packages():
    result = []
    for name in os.listdir(_package_dir):
        result.extend(_get_package_variants(name))
    return result
