fetch('http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.14.tar.gz')

build(static_lib=True, options='--disable-nls')

collect_docs('AUTHORS README COPYING.LIB')
