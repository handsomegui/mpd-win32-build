import os, glob
import config, cmdutil, fsutil

from os import path

class PackageInfo:
    def _read_artifacts(self):
        if path.exists(self.artifacts_file):
            return fsutil.read_pairs(self.artifacts_file, '->')
        else:
            return []

    def _resolve_script(self, name):
        if self.variant_name:
            name = self.variant_name + '-' + name
        file = path.join(self.script_dir, name)
        if path.exists(file):
            return file
        return None

    def dependency_map(self):
        if self.dep_map is not None:
            return self.dep_map
        result = {}
        next = [self.name]
        while next:
            name = next.pop()
            if name in result:
                continue
            deps = get(name).depends
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
        
    def init_dirs(self):
        fsutil.make_dir(self.work_dir)
        fsutil.make_dir(self.build_dir)
        fsutil.make_dir(self.install_dir)
        fsutil.make_dir(self.cache_dir)
        if self.enable_dist:
            fsutil.make_dir(self.dist_dir)

    def reset_dirs(self):
        fsutil.safe_remove_dir(self.work_dir)
        self.init_dirs()

    def __init__(self, name):
        if not valid_name(name):
            raise ValueError('Invalid package name: ' + name)

        self.name = name
        self.short_name, self.variant_name = _decode_name(name)

        self.work_dir = path.join(_work_dir, name)
        self.build_dir  = path.join(self.work_dir, 'build')
        self.install_dir = path.join(self.work_dir, 'install')
        self.dist_dir = path.join(self.work_dir, 'dist')
        self.script_dir = path.join(_package_dir, self.short_name)
        self.cache_dir  = path.join(_cache_dir, name)

        if not path.exists(self.script_dir):
            raise ValueError('Directory is not found for package ' + name)

        self.package_file = self._resolve_script('package.txt')
        self.build_file = self._resolve_script('build.py')

        if not self.package_file:
            raise ValueError('Package definition is not found for package ' + name)
        if not self.build_file:
            raise ValueError('Build script is not found for package ' + name)

        self.stamp_file = path.join(self.work_dir, 'stamp.txt')
        self.artifacts_file = path.join(self.work_dir, 'artifacts.txt')
        self.version_file = path.join(self.work_dir, 'version.txt')
        self.build_log_file = path.join(self.work_dir, 'build.log')
        self.fetch_log_file = path.join(self.work_dir, 'fetch.log')

        options = config.load(self.package_file)

        self.depends = options.get('depends', '').split()
        self.enable_dist = options.get('enable_dist', '')=='true'

        self.source = options.get('source', '')
        self.source_rev = options.get('source_rev', '')
        self.source_file = options.get('source_file', '')

        self.dep_map = None

_info_cache = {}

def init(base_dir, profile):
    global _base_dir
    global _package_dir
    global _cache_dir
    global _work_dir

    _base_dir = _adjust_path(base_dir)
    _package_dir = path.join(_base_dir, 'packages')

    if not path.exists(_package_dir):
        raise ValueError('Package directory is not found: ' + _package_dir)
        
    if profile != config.DEFAULT_PROFILE:
        work = 'work-' + profile
    else:
        work = 'work'

    _cache_dir = _resolve_dir('cache_dir', 'cache')
    _work_dir = _resolve_dir('work_dir', work)

    fsutil.make_dir(_cache_dir)
    fsutil.make_dir(_work_dir)

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
    return short_name, variant_name

def _get_package_variants(name):
    suffix = '-package.txt'
    result = []
    package_dir = path.join(_package_dir, name)
    if path.exists(path.join(package_dir, 'package.txt')):
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
