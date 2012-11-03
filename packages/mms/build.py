fetch('http://sourceforge.net/projects/libmms/files/libmms/0.6.2/libmms-0.6.2.tar.gz/download')

build(static_lib=True)

collect_licenses('COPYING.LIB README AUTHORS')
