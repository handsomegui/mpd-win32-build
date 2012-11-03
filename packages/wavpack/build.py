fetch('http://www.wavpack.com/wavpack-4.60.1.tar.bz2')
patch('Makefile.in')

build(static_lib=True)

collect_docs('license.txt')
