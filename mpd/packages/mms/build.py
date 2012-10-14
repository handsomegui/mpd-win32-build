from package import *

package('mms')

fetch('http://sourceforge.net/projects/libmms/files/libmms/0.6.2/libmms-0.6.2.tar.gz/download')
build(shared_lib=True)

collect_binaries('libmms-*.dll')
collect_docs('COPYING.LIB README AUTHORS')
