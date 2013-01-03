fetch('git://git.xiph.org/flac.git', 'f20164e41ed')
patch('Makefile.am')
patch('configure.ac')
patch('src/share/utf8/utf8.c')

build(static_lib=True)

collect_licenses('AUTHORS COPYING.Xiph')
