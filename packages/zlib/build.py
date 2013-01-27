import cmdutil, toolchain

install_dir = cmdutil.to_unix_path(info.install_dir)

make_args = ('install -fwin32/Makefile.gcc SHARED_MODE=0' +
     ' INCLUDE_PATH=' + install_dir + '/include' +
     ' BINARY_PATH='  + install_dir + '/bin' +
     ' LIBRARY_PATH=' + install_dir + '/lib' +
     ' prefix=' + install_dir)

if toolchain.crossbuild:
    make_args += ' PREFIX=' + toolchain.host_triplet + '-'

make(make_args)
collect_licenses('README')
