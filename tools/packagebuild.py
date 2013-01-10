import sys, os, glob, shutil, urllib, re, inspect
import packageinfo, cmdutil, config, fsutil

from os import path

def run(info):
    global _info
    _info = info
    fsutil.safe_remove(_info.build_log_file)
    cmdutil.redirect_output(_info.build_log_file)
    execfile(_info.build_file, _get_builder_symbols())

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
    fsutil.safe_remove(path.join(_info.build_dir, file))

def patch(target_file, patch_file = None):
    if patch_file is None:
        patch_file = path.basename(target_file) + '.patch'
    target_file_abs = path.join(_info.build_dir, target_file)
    patch_file_abs = path.join(_info.script_dir, patch_file)
    cmdutil.patch(target_file_abs, patch_file_abs)
    
def generate_pkg_config(pkgname, libname = None, version = None):
    if not libname:
        libname = _info.short_name
    if not version:
        version = '1.0.0'
    output_file = path.join(_info.install_dir, 'lib', 'pkgconfig', pkgname + '.pc')
    fsutil.make_dir(path.dirname(output_file))
    with open(output_file, 'wb') as f:
        f.write('prefix=%s\n' % cmdutil.to_unix_path(_info.install_dir))
        f.write('exec_prefix=${prefix}\n')
        f.write('libdir=${exec_prefix}/lib\n')
        f.write('includedir=${prefix}/include\n')
        f.write('\n')
        f.write('Name: %s\n' % pkgname)
        f.write('Description: %s library\n' % libname)
        f.write('Version: %s\n' % version)
        f.write('Libs: -L${libdir} -l%s\n' % libname)
        f.write('Cflags: -I${includedir}\n')

def collect_version(src_file = 'configure.ac', include_rev = False):
    src_file_full = path.join(_info.build_dir, src_file)
    if not path.exists(src_file_full):
        raise ValueError('File is not found: ' + src_file)
    text = fsutil.read_file(src_file_full)
    results = re.findall(r'AC_INIT\(.*, (.*), .*\)', text)
    if len(results) != 1:
        raise ValueError('Unable to extract version')
    version = results[0]
    if include_rev:
        if not _info.source_rev:
            raise ValueError('Unable to include source revision in version')
        version += '-' + _info.source_rev
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
    source_dir = path.join(_info.install_dir, 'bin')
    files = _collect_artifacts(patterns.split(), source_dir, 'bin')
    if config.get_bool('strip_binaries'):
        _strip(files)

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
    files = []
    with open(_info.artifacts_file, 'a') as f:
        for pattern in patterns:
            for source in glob.iglob(path.join(source_dir, pattern)):
                target = path.join(target_dir, path.basename(source))
                source_n = path.normpath(source)
                target_n = path.normpath(target)
                f.write('%s -> %s\n' % (source_n, target_n))
                files.append(source_n)
    return files
    
def _strip(files):
    if _info.crossbuild:
        strip = _info.crossbuild_host + '-strip'
    else:
        strip = 'strip'
    for f in files:
        cmdutil.native_exec(strip, ['--strip-all', f])

def _add_subpath(base, subpath):
    if subpath:
        return path.join(base, subpath)
    else:
        return base

def _build_cmake_args():
    if cmdutil.on_windows:
        generator = '"MinGW Makefiles"'
    else:
        generator = '"Unix Makefiles"'

    install_prefix = cmdutil.to_cmake_path(_info.install_dir)
    result = ['..', '-G', generator, '-DCMAKE_INSTALL_PREFIX=' + install_prefix]
    
    if _info.crossbuild:
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
    paths = []
    libs = []
    cflags = []
    pkg_config_paths = []

    for dep_name in _info.dependency_map().iterkeys():
        if dep_name == _info.name:
            continue
        p = packageinfo.get(dep_name).install_dir
        paths.append(path.join(p, 'bin'))
        libs.append('-L' + cmdutil.to_unix_path(path.join(p, 'lib')))
        cflags.append('-I' + cmdutil.to_unix_path(path.join(p, 'include')))
        pkg_config_paths.append(cmdutil.to_unix_path(path.join(p, 'lib', 'pkgconfig')))

    env_libs = config.get_list('libs') + config.get_list(_info.name + '-libs')
    env_cflags = config.get_list('cflags') + config.get_list(_info.name + '-cflags')

    result_path = os.pathsep.join(paths)
    result_libs = ' '.join(libs + user_libs + env_libs)
    result_cflags = ' '.join(cflags + user_cflags + env_cflags)
    result_pkg_config_path = ':'.join(pkg_config_paths)

    result = {
        'PATH'            : result_path,
        'LIBS'            : result_libs,
        'CFLAGS'          : result_cflags,
        'CXXFLAGS'        : result_cflags,
        'PKG_CONFIG_PATH' : result_pkg_config_path,
    }

    if _info.crossbuild:
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

def _find_configure(build_dir):
    items = ['configure', 'autogen.sh']
    for i in items:
        if path.exists(path.join(build_dir, i)):
            return i
    raise ValueError('Unable to find configuration script, tried: ' + ', '.join(items))

def _get_gcc_path():
    if _info.crossbuild:
        gcc = _info.crossbuild_host + '-gcc'
    else:
        gcc = 'gcc'
    return cmdutil.which(gcc)

def _is_builder_symbol(obj):
    return (inspect.isfunction(obj)
      and (not obj.func_name.startswith('_'))
      and (obj.func_name != 'run'))

def _get_builder_symbols():
    this_module = sys.modules[__name__]
    result = dict(inspect.getmembers(this_module, _is_builder_symbol))
    result['info'] = _info
    return result
