import sys, os, glob, shutil, urllib, re, inspect
import packageinfo, cmdutil, config, fsutil

from os import path

class UpToDateException(Exception):
    pass

def run(info):
    global _info

    _info = info

    fsutil.make_dir(_info.cache_dir)
    fsutil.make_dir(_info.build_dir)
    fsutil.make_dir(_info.install_dir)

    fsutil.safe_remove(_info.log_file)
    cmdutil.redirect_output(_info.log_file)

    try:
        execfile(_info.build_file, _get_builder_symbols())
        updated = True
    except UpToDateException:
        updated = False

    if updated:
        fsutil.write_stamp(_info.stamp_file)

def include(script):
    file = fsutil.resolve_include(_info.build_file, script)
    execfile(file, _get_builder_symbols())

def build_cmake(options = '', subdir = ''):
    build_dir = _add_subpath(_info.build_dir, subdir)
    cmake_dir = path.join(build_dir, 'cmake.build')
    options = _build_cmake_args() + options.split()

    fsutil.make_dir(cmake_dir)

    cmdutil.native_exec('cmake', options, work_dir=cmake_dir)
    cmdutil.native_make([], work_dir=cmake_dir)
    cmdutil.native_make(['install'], work_dir=cmake_dir)

def build(static_lib = False, shared_lib = False, options = '', crossbuild_options=True, libs = '', cflags = '', subdir = ''):
    if static_lib and shared_lib:
        raise ValueError('Both static_lib and shared_lib options are specified')

    build_dir = _add_subpath(_info.build_dir, subdir)
    all_options = [_find_configure(build_dir), '--prefix=' + cmdutil.to_unix_path(_info.install_dir)]
    if _info.crossbuild and crossbuild_options:
        all_options.extend(['--build=' + _info.crossbuild_build, '--host=' + _info.crossbuild_host])
    if static_lib:
        all_options.extend(['--enable-static', '--disable-shared'])
    if shared_lib:
        all_options.extend(['--enable-shared', '--disable-static'])
    all_options.extend(options.split())
    all_options.extend(config.get_list('options'))
    all_options.extend(config.get_list(_info.name + '-options'))
    env = _build_configure_env(libs.split(), cflags.split())

    cmdutil.unix_exec('sh', all_options, work_dir=build_dir, extra_env=env)
    cmdutil.unix_make([], work_dir=build_dir)
    cmdutil.unix_make(['install'], work_dir=build_dir)

def make(args):
    build_dir = _info.build_dir
    cmdutil.unix_make(args.split(), work_dir=build_dir)

def remove(file):
    fsutil.safe_remove(file)

def patch(target_file, patch_file = None):
    if patch_file is None:
        patch_file = path.basename(target_file) + '.patch'
    target_file_abs = path.join(_info.build_dir, target_file)
    patch_file_abs = path.join(_info.script_dir, patch_file)
    cmdutil.patch(target_file_abs, patch_file_abs)

def fetch(url, rev = None, file = None):
    if not _is_up_to_date():
        _reset_build_dirs()
    if url.startswith('git://') or url.endswith('.git'):
        if rev is None:
            raise ValueError('Revision to fetch should be specified')
        rebuild = _fetch_git(url, rev)
    else:
        rebuild = _fetch_archive(url, file)
    if rebuild:
        _log('building')
    else:
        _log('up to date')
        raise UpToDateException()

def collect_version(src_file = 'configure.ac'):
    src_file_full = path.join(_info.build_dir, src_file)
    if not path.exists(src_file_full):
        raise ValueError('File is not found: ' + src_file)
    text = fsutil.read_file(src_file_full)
    results = re.findall(r'AC_INIT\(.*, (.*), .*\)', text)
    if len(results) != 1:
        raise ValueError('Unable to extract version')
    version = results[0]
    if _source_rev:
        version += '-' + _source_rev
    with open(_info.version_file, 'w') as f:
        f.write(version)

def collect_system_libs(libgcc=False, libstdcxx=False):
    patterns = []
    if libgcc:
        patterns.append('libgcc_s_*.dll')
    if libstdcxx:
        patterns.append('libstdc++-*.dll')
    if not patterns:
        return

    target_dir = 'bin'
    gcc_path = _get_gcc_path()

    lib_dir = cmdutil.gcc_lib_dir(gcc_path)
    found = _collect_artifacts(patterns, lib_dir, target_dir)

    if (not found) and cmdutil.on_windows:
        # Search for bin folder of gcc too
        _collect_artifacts(patterns, path.dirname(gcc_path), target_dir)

def collect_binaries(patterns):
    _collect_artifacts(patterns.split(), path.join(_info.install_dir, 'bin'), 'bin')

def collect_docs(patterns, source_dir=''):
    collect_files(patterns, source_dir, 'doc')

def collect_licenses(patterns, source_dir=''):
    target_dir = path.join('doc/licenses', _info.short_name)
    collect_files(patterns, source_dir, target_dir)

def collect_files(patterns, source_dir = '', target_dir = ''):
    source_dir_full = _add_subpath(_info.build_dir, source_dir)
    _collect_artifacts(patterns.split(), source_dir_full, target_dir)
    
def install(patterns, source_dir = '', target_dir = ''):
    source_dir_full = _add_subpath(_info.build_dir, source_dir)
    target_dir_full = _add_subpath(_info.install_dir, target_dir)
    fsutil.make_dir(target_dir_full)
    for pattern in patterns.split():
        for source in glob.iglob(path.join(source_dir_full, pattern)):
            shutil.copy(source, target_dir_full)

def _collect_artifacts(patterns, source_dir, target_dir):
    found = False
    with open(_info.artifacts_file, 'a') as f:
        for pattern in patterns:
            for source in glob.iglob(path.join(source_dir, pattern)):
                target = path.join(target_dir, path.basename(source))
                f.write('%s -> %s\n' % (path.normpath(source), path.normpath(target)))
                found = True
    return found

def _add_subpath(base, subpath):
    if subpath:
        return path.join(base, subpath)
    else:
        return base

def _fetch_archive(url, file = None):
    if file is None:
        file = _guess_name(url)
    file_path = path.join(_info.cache_dir, file)
    downloaded = _download_once(url, file_path)
    if downloaded or _build_dir_empty():
        _untar_to_build_dir(file_path, strip_root_dir=True)
        return True
    return False

def _fetch_git(url, rev):
    global _source_rev

    repo_dir = path.join(_info.cache_dir, 'mirror.git')
    if cmdutil.git_check(repo_dir):
        _log('fetching')
        cmdutil.git('fetch', ['--all'], work_dir=repo_dir)
    else:
        _log('cloning')
        cmdutil.git('clone', ['--mirror', url, repo_dir])

    _source_rev = cmdutil.git_short_rev(repo_dir, rev)
    tar_file = path.join(_info.cache_dir, 'rev-%s.tar' % _source_rev)
    tar_glob = path.join(_info.cache_dir, 'rev-*.tar')
    exported = False

    if not path.exists(tar_file):
        fsutil.glob_remove(tar_glob)
        cmdutil.git('archive', ['-o', tar_file, _source_rev], work_dir=repo_dir)
        exported = True

    if exported or _build_dir_empty():
        _untar_to_build_dir(tar_file)
        return True
    return False

def _build_dir_empty():
    return not os.listdir(_info.build_dir)

def _build_cmake_args():
    if cmdutil.on_windows:
        generator = '"MinGW Makefiles"'
    else:
        generator = '"Unix Makefiles"'

    install_prefix = cmdutil.to_cmake_path(_info.install_dir)
    result = ['..', '-G', generator, '-DCMAKE_INSTALL_PREFIX=' + install_prefix]
    
    if _info.crossbuild_host:
        _write_crossbuild_file(path.join(_info.build_dir, 'crossbuild.cmake'))
        result.append('-DCMAKE_TOOLCHAIN_FILE=../crossbuild.cmake')

    return result

def _write_crossbuild_file(file):
    system_root_path = path.dirname(path.dirname(_get_gcc_path()))
    crossbuild_root_path = cmdutil.to_cmake_path(path.join(system_root_path, _info.crossbuild_host))

    with open(file, 'w') as f:
        f.write('# generated by buildtool\n\n')
        f.write('SET(CMAKE_SYSTEM_NAME Windows)\n\n')
        f.write('SET(CMAKE_C_COMPILER   %s-gcc)\n' % _info.crossbuild_host)
        f.write('SET(CMAKE_CXX_COMPILER %s-g++)\n' % _info.crossbuild_host)
        f.write('SET(CMAKE_RC_COMPILER  %s-windres)\n\n' % _info.crossbuild_host)
        f.write('SET(CMAKE_FIND_ROOT_PATH %s)\n' % crossbuild_root_path)
        f.write('SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)\n')
        f.write('SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)\n')
        f.write('SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)\n')

def _build_configure_env(user_libs, user_cflags):
    libs = []
    cflags = []
    pkg_config_paths = []

    for dep in _info.dependency_map().iterkeys():
        if dep==_info.name:
            continue
        p = packageinfo.get(dep).install_dir
        libs.append('-L' + cmdutil.to_unix_path(path.join(p, 'lib')))
        cflags.append('-I' + cmdutil.to_unix_path(path.join(p, 'include')))
        pkg_config_paths.append(cmdutil.to_unix_path(path.join(p, 'lib', 'pkgconfig')))

    env_libs = config.get_list('libs')
    env_cflags = config.get_list('cflags')

    lenv_libs = config.get_list(_info.name + '-libs')
    lenv_cflags = config.get_list(_info.name + '-cflags')

    result = {
        'LIBS'            : ' '.join(libs + user_libs + env_libs + lenv_libs),
        'CFLAGS'          : ' '.join(cflags + user_cflags + env_cflags + lenv_cflags),
        'PKG_CONFIG_PATH' : ':'.join(pkg_config_paths),
    }

    if _info.crossbuild_host:
        result.update({
            'AR'      : _info.crossbuild_host + '-ar',
            'AS'      : _info.crossbuild_host + '-as',
            'CC'      : _info.crossbuild_host + '-gcc',
            'CXX'     : _info.crossbuild_host + '-g++',
            'LD'      : _info.crossbuild_host + '-ld',
            'NM'      : _info.crossbuild_host + '-nm',
            'DLLTOOL' : _info.crossbuild_host + '-dlltool',
            'OBJDUMP' : _info.crossbuild_host + '-objdump',
            'RANLIB'  : _info.crossbuild_host + '-ranlib',
            'STRIP'   : _info.crossbuild_host + '-strip',
            'WINRC'   : _info.crossbuild_host + '-windres'
        })

    return result

def _untar_to_build_dir(tar_file, strip_root_dir = False):
    _reset_build_dirs()
    cmdutil.untar(tar_file, target_dir=_info.build_dir, strip_root_dir=strip_root_dir)

def _guess_name(url):
    download_suffix = '/download'
    if url.startswith('http://sourceforge.net') and url.endswith(download_suffix):
        url = url[0:-len(download_suffix)]
    pos = url.rfind('/')
    if pos < 0 or pos == len(url) - 1:
        raise ValueError('Unable to extract file name from url: ' + url)
    return urllib.unquote(url[pos + 1:])

def _download_once(url, file):
    if path.exists(file):
        return False
    _log('downloading')
    cmdutil.wget(url, file)
    return True

def _find_configure(build_dir):
    items = ['configure', 'autogen.sh']
    for i in items:
        if path.exists(path.join(build_dir, i)):
            return i
    raise ValueError('Unable to find configuration script, tried: ' + ', '.join(items))

def _get_gcc_path():
    if _info.crossbuild_host:
        gcc = _info.crossbuild_host + '-gcc'
    else:
        gcc = 'gcc'
    return cmdutil.which(gcc)

def _is_up_to_date():
    if not path.exists(_info.stamp_file):
        return False
    stamp_mtime = path.getmtime(_info.stamp_file)
    max_mtime = 0
    for dep_name in _info.dependency_map().iterkeys():
        dep_info = packageinfo.get(dep_name)
        if not path.exists(dep_info.stamp_file):
            return False
        for f in [dep_info.stamp_file, dep_info.build_file, dep_info.deps_file]:
            if f and path.exists(f):
                max_mtime = max(max_mtime, path.getmtime(f))
    return stamp_mtime >= max_mtime

def _reset_build_dirs():
    fsutil.safe_remove_dir(_info.build_dir)
    fsutil.safe_remove_dir(_info.install_dir)
    fsutil.make_dir(_info.build_dir)
    fsutil.make_dir(_info.install_dir)

def _log(message):
    print "buildtool: %s %s" % (_info.name.ljust(16), message)

def _is_builder_symbol(obj):
    return (inspect.isfunction(obj)
      and (not obj.func_name.startswith('_'))
      and (obj.func_name != 'run'))

def _get_builder_symbols():
    this_module = sys.modules[__name__]
    result = dict(inspect.getmembers(this_module, _is_builder_symbol))
    result['info'] = _info
    return result
