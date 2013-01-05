import sys, os, glob, shutil, urllib, re, inspect
import packageinfo, cmdutil, config, fsutil

from os import path

def run(info):
    global _info

    _info = info

    fsutil.make_dir(_info.build_dir)
    fsutil.make_dir(_info.install_dir)

    fsutil.safe_remove(_info.artifacts_file)
    fsutil.safe_remove(_info.version_file)
    fsutil.safe_remove(_info.log_file)

    cmdutil.redirect_output(_info.log_file)
    execfile(_info.build_file, _get_builder_symbols())

def include(script):
    file = fsutil.resolve_include(_info.build_file, script)
    execfile(file, _get_builder_symbols())

def build_cmake(options = '', subdir = ''):
    build_dir = _add_subpath(_info.build_dir, subdir)
    cmake_dir = path.join(build_dir, 'cmake.build')
    cmake_ok = path.join(build_dir, 'cmake.ok')

    if not path.exists(cmake_ok):
        _log('configuring')
        fsutil.safe_remove_dir(cmake_dir)
        fsutil.make_dir(cmake_dir)
        options = _build_cmake_args() + options.split()
        cmdutil.native_exec('cmake', options, work_dir=cmake_dir)
        fsutil.write_marker(cmake_ok)

    (rebuild, stamp) = _get_make_status(build_dir)
    if rebuild:
        _log('making')
        cmdutil.native_make([], work_dir=cmake_dir)
        _log('installing')
        cmdutil.native_make(['install'], work_dir=cmake_dir)
        fsutil.write_marker(stamp)
    else:
        _log('up to date')

def build(static_lib = False, shared_lib = False, options = '', crossbuild_options=True, libs = '', cflags = '', subdir = ''):
    if static_lib and shared_lib:
        raise ValueError('Both static_lib and shared_lib options are specified')

    build_dir = _add_subpath(_info.build_dir, subdir)
    configure_ok = path.join(build_dir, 'configure.ok')

    if not path.exists(configure_ok):
        _log('configuring')
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
        fsutil.write_marker(configure_ok)

    (rebuild, stamp) = _get_make_status(build_dir)
    if rebuild:
        _log('making')
        cmdutil.unix_make([], work_dir=build_dir)
        _log('installing')
        cmdutil.unix_make(['install'], work_dir=build_dir)
        fsutil.write_marker(stamp)
    else:
        _log('up to date')

def make(args):
    build_dir = _info.build_dir
    (rebuild, stamp) = _get_make_status(build_dir)
    if rebuild:
        _log('making and installing')
        cmdutil.unix_make(args.split(), work_dir=build_dir)
        fsutil.write_marker(stamp)
    else:
        _log('up to date')

def remove(file):
    target = path.join(_info.build_dir, file)
    marker = target + '.removed'
    if path.exists(target) and not path.exists(marker):
        os.remove(target)
        fsutil.write_marker(marker)

def patch(target_file, patch_file = None):
    if patch_file is None:
        patch_file = path.basename(target_file) + '.patch'
    target_file_abs = path.join(_info.build_dir, target_file)
    patch_file_abs = path.join(_info.script_dir, patch_file)
    marker_file = target_file_abs + '.patched'
    if path.exists(marker_file):
        return
    cmdutil.patch(target_file_abs, patch_file_abs)
    fsutil.write_marker(marker_file)

def fetch(url, rev = None, file = None):
    fsutil.make_dir(_info.cache_dir)
    if url.startswith('git://') or url.endswith('.git'):
        if rev is None:
            raise ValueError('Revision to fetch should be specified')
        rebuild = _fetch_git(url, rev)
    else:
        rebuild = _fetch_archive(url, file)

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

def _get_make_status(build_dir):
    stamp = path.join(build_dir, 'make.ok')
    if path.exists(stamp):
        rebuild = fsutil.max_mtime(build_dir) > path.getmtime(stamp)
    else:
        rebuild = True
    return (rebuild, stamp)

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
    if path.exists(_info.build_dir):
        shutil.rmtree(_info.build_dir)
    os.makedirs(_info.build_dir)
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
