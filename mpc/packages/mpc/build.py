from package import *

package('mpc')

clone('git://git.musicpd.org/master/mpc.git')
build(libs='-lws2_32')

collect_binaries('mpc.exe')
collect_docs('AUTHORS COPYING NEWS README')
collect_version()
