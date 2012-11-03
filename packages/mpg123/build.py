fetch('http://sourceforge.net/projects/mpg123/files/mpg123/1.14.4/mpg123-1.14.4.tar.bz2/download')
patch('src/libmpg123/lfs_wrap.c')

build(static_lib=True)

collect_licenses('COPYING AUTHORS')
