fetch('http://sourceforge.net/projects/mpg123/files/mpg123/1.14.4/mpg123-1.14.4.tar.bz2/download')
patch('src/libmpg123/lfs_wrap.c')

build(shared_lib=True)

collect_binaries('libmpg123-*.dll')
collect_docs('COPYING AUTHORS')
