import cmdutil
from package import *

info = package('zlib')

fetch('http://sourceforge.net/projects/libpng/files/zlib/1.2.7/zlib-1.2.7.tar.bz2/download')

install_dir = cmdutil.to_unix_path(info.install_dir)

make_args = ('install -fwin32/Makefile.gcc SHARED_MODE=1' +
     ' INCLUDE_PATH=' + install_dir + '/include' +
     ' BINARY_PATH='  + install_dir + '/bin' +
     ' LIBRARY_PATH=' + install_dir + '/lib' +
     ' prefix=' + install_dir)

if info.crossbuild:
    make_args += ' PREFIX=' + info.crossbuild_host + '-'

make(make_args)

collect_binaries('zlib1.dll')
collect_docs('README')
