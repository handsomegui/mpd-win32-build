import sys, os, glob, shutil, urllib, re, inspect
import packageinfo, cmdutil, config, fsutil, toolchain

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

def build(static_lib = False, shared_lib = False, options = '',
          crossbuild_options=True, libs = '', cflags = '', subdir = ''):
    if static_lib and shared_lib:
        raise ValueError('Both static_lib and shared_lib options are specified')

    build_dir = _add_subpath(_info.build_dir, subdir)
    all_options = [
        _find_configure(build_dir),
        '--prefix=' + cmdutil.to_unix_path(_info.install_dir)
    ]
    if toolchain.crossbuild and crossbuild_options:
        all_options.extend([
            '--build=' + toolchain.build_triplet,
            '--host=' + toolchain.host_triplet])
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

def collect_binaries(patterns):
    source_dir = path.join(_info.install_dir, 'bin')
    binaries = _collect_artifacts(patterns.split(), source_dir, 'bin')
    _postprocess(binaries,
        config.get_bool('strip_binaries'),
        config.get_bool('extract_debug_info'))

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
    
def _postprocess(files, do_strip, do_extract_dbg):
    if not (do_strip or do_extract_dbg):
        return
    strip = toolchain.tool_name('strip')
    objcopy = toolchain.tool_name('objcopy')
    result = []
    for target in files:
        dbgfile = target + ".debug"
        if do_extract_dbg:
            cmdutil.native_exec(objcopy, ['--only-keep-debug', target, dbgfile])
            result.append(dbgfile)
        if do_strip:
            cmdutil.native_exec(strip, ['--strip-all', target])
        if do_extract_dbg:
            cmdutil.native_exec(objcopy, ['--add-gnu-debuglink=' + dbgfile, target])
    return result

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
    
    if toolchain.crossbuild:
        _write_crossbuild_file(path.join(_info.build_dir, 'crossbuild.cmake'))
        result.append('-DCMAKE_TOOLCHAIN_FILE=../crossbuild.cmake')

    return result

def _write_crossbuild_file(file):
    root_path = cmdutil.to_cmake_path(toolchain.sysroot)
    with open(file, 'w') as f:
        f.write('# generated by buildtool\n\n')
        f.write('SET(CMAKE_SYSTEM_NAME %s)\n\n' % toolchain.target_os_cmake)
        f.write('SET(CMAKE_C_COMPILER   %s)\n' % toolchain.tool_name('gcc'))
        f.write('SET(CMAKE_CXX_COMPILER %s)\n' % toolchain.tool_name('g++'))
        f.write('SET(CMAKE_RC_COMPILER  %s)\n\n' % toolchain.tool_name('windres'))
        f.write('SET(CMAKE_FIND_ROOT_PATH %s)\n' % root_path)
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
        bin_dir = path.join(p, 'bin')
        lib_dir = path.join(p, 'lib')
        include_dir = path.join(p, 'include')
        pkg_config_dir = path.join(p, 'lib', 'pkgconfig')

        if path.exists(bin_dir):
            paths.append(bin_dir)
        if path.exists(lib_dir):
            libs.append('-L' + cmdutil.to_unix_path(lib_dir))
        if path.exists(include_dir):
            cflags.append('-I' + cmdutil.to_unix_path(include_dir))
        if path.exists(pkg_config_dir):
            pkg_config_paths.append(cmdutil.to_unix_path(pkg_config_dir))

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

    if toolchain.crossbuild:
        result.update({
            'AR'      : toolchain.tool_name('ar'),
            'AS'      : toolchain.tool_name('as'),
            'CC'      : toolchain.tool_name('gcc'),
            'CXX'     : toolchain.tool_name('g++'),
            'LD'      : toolchain.tool_name('ld'),
            'NM'      : toolchain.tool_name('nm'),
            'DLLTOOL' : toolchain.tool_name('dlltool'),
            'OBJDUMP' : toolchain.tool_name('objdump'),
            'RANLIB'  : toolchain.tool_name('ranlib'),
            'STRIP'   : toolchain.tool_name('strip'),
            'WINRC'   : toolchain.tool_name('windres'),
            'PKG_CONFIG_LIBDIR' : '/nonexistent'
        })

    return result

def _find_configure(build_dir):
    items = ['configure', 'autogen.sh']
    for i in items:
        if path.exists(path.join(build_dir, i)):
            return i
    raise ValueError('Unable to find configuration script, tried: ' + ', '.join(items))

def _is_builder_symbol(obj):
    return (inspect.isfunction(obj)
      and (not obj.func_name.startswith('_'))
      and (obj.func_name != 'run'))

def _get_builder_symbols():
    this_module = sys.modules[__name__]
    result = dict(inspect.getmembers(this_module, _is_builder_symbol))
    result['info'] = _info
    return result
