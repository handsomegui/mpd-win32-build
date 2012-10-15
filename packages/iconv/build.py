fetch('http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz')

build(shared_lib=True, options='--disable-nls')

collect_binaries('libiconv-*.dll')
collect_docs('AUTHORS README COPYING.LIB')
