import sys, platform
import config, cmdutil

from os import path

target_linux   = 'linux'
target_windows = 'windows'

def _guess_target():
    global target
    global target_arch
    global target_os
    global target_os_cmake
    global target_dist_suffix

    if sys.platform.startswith('win32'):
        target = target_windows
        target_arch = 'i686'
        target_os = 'mingw32'
        target_os_cmake = 'Windows'
        target_dist_suffix = 'win32'
        return

    if sys.platform.startswith('linux'):
        target = target_linux
        target_arch = platform.machine()
        target_os = 'linux'
        target_os_cmake = 'Linux'
        target_dist_suffix = platform.machine()
        return

    raise ValueError('Unsupported target platform: ' + sys.platform)

def _set_target_from_triplet(t):
    global target
    global target_arch
    global target_os
    global target_os_cmake
    global target_dist_suffix

    items = t.split('-', 3)
    if len(items) != 3:
        raise ValueError('Invalid triplet: ' + t)

    target_arch = items[0]

    if items[1] == 'linux':
        target = target_linux
        target_os = 'linux'
        target_os_cmake = 'Linux'
        target_dist_suffix = target_arch
        return

    if items[2] == 'mingw32':
        target = target_windows
        target_os = 'mingw32'
        target_os_cmake = 'Windows'
        if target_arch == 'x86_64':
            target_dist_suffix = 'win64'
        else:
            target_dist_suffix = 'win32'
        return

    raise ValueError('Unknown target platform: ' + t)

def _get_sysroot():
    config_value = config.get('sysroot', '')
    if config_value:
        return config_value
    gcc_path = cmdutil.which(tool_name('gcc'))
    base_dir = path.dirname(path.dirname(gcc_path))
    guessed_value = path.join(base_dir, host_triplet)
    if not path.exists(guessed_value):
        raise ValueError('Unable to guess sysroot, try specifying \'sysroot\' option')
    return guessed_value

def tool_name(name):
    if crossbuild:
        return host_triplet + '-' + name
    else:
        return name

def init():
    global crossbuild
    global build_triplet
    global host_triplet
    global sysroot

    build_triplet = config.get('build')
    host_triplet = config.get('host')

    crossbuild = build_triplet or host_triplet
    if crossbuild:
        if not build_triplet:
            raise ValueError('Cross-compiling but build triplet is not set')
        if not host_triplet:
            raise ValueError('Cross-compiling but host triplet is not set')
        _set_target_from_triplet(host_triplet)
        sysroot = _get_sysroot()
    else:
        _guess_target()
