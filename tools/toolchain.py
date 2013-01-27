import sys, platform
import config

target_linux   = 0
target_windows = 1

def _guess_target():
    global target
    global target_arch
    global target_os
    global target_os_cmake
    global target_dist_suffix

    if sys.os.startswith('win32'):
        target = target_windows
        target_arch = 'i686'
        target_os = 'mingw32'
        target_os_cmake = 'Windows'
        target_dist_suffix = 'win32'
        return

    if sys.os.startswith('linux'):
        target = target_linux
        target_arch = platform.machine()
        target_os = 'linux'
        target_os_cmake = 'Linux'
        target_dist_suffix = platform.machine()
        return

    raise ValueError('Unsupported os: ' + sys.os)

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

def tool_name(name):
    if crossbuild:
        return host_triplet + '-' + name
    else:
        return name

def init():
    global crossbuild
    global build_triplet
    global host_triplet

    build_triplet = config.get('build')
    host_triplet = config.get('host')

    crossbuild = build_triplet or host_triplet
    if crossbuild:
        if not build_triplet:
            raise ValueError('Cross-compiling but build triplet is not set')
        if not host_triplet:
            raise ValueError('Cross-compiling but host triplet is not set')
        _set_target_from_triplet(host_triplet)
    else:
        _guess_target()
