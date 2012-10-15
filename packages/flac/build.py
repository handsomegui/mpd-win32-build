fetch('git://git.xiph.org/flac.git', 'a2923e64c0c1')
patch('Makefile.am')
patch('configure.ac')
patch('src/share/utf8/utf8.c')

build(shared_lib=True)

collect_binaries('libFLAC-*.dll')
collect_docs('AUTHORS COPYING.Xiph')
