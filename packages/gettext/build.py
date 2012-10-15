from package import *

package('gettext')

fetch('http://ftp.gnu.org/pub/gnu/gettext/gettext-0.18.1.1.tar.gz')
options='--with-included-gettext --enable-threads=win32 --disable-libasprintf --disable-java'
build(shared_lib=True, options=options, subdir='gettext-runtime')

collect_binaries('libintl-*.dll')
collect_docs('AUTHORS intl/COPYING.LIB-2.1', source_dir='gettext-runtime')
