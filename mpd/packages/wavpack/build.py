from package import *

package('wavpack')

fetch('http://www.wavpack.com/wavpack-4.60.1.tar.bz2')
patch('Makefile.in')
build(shared_lib=True)

collect_binaries('libwavpack-*.dll')
collect_docs('license.txt')
