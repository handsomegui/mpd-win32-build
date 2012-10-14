from package import *

package('mad')

fetch('git://gitorious.org/mad/libmad.git', '637baad')
build(static_lib=True)

collect_docs('COPYRIGHT COPYING CREDITS')
