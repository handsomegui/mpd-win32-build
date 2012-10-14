from package import *

package('audiofile')

fetch('http://audiofile.68k.org/audiofile-0.3.4.tar.gz')
build(shared_lib=True)

collect_system_libs(libgcc=True, libstdcxx=True)
collect_binaries('libaudiofile-*.dll')
collect_docs('ACKNOWLEDGEMENTS AUTHORS COPYING README')
