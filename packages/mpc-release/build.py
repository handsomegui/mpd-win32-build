fetch('http://sourceforge.net/projects/musicpd/files/mpc/0.22/mpc-0.22.tar.bz2/download')

build(libs='-lws2_32')

collect_binaries('mpc.exe')
collect_docs('AUTHORS COPYING NEWS README')
collect_version()
