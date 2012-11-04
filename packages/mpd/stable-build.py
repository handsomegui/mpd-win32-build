clone('git://git.musicpd.org/master/mpd.git', 'v0.17.x')

build(options='--enable-openal', libs='-lz -lole32 -static-libgcc')

collect_binaries('mpd.exe')
collect_licenses('AUTHORS COPYING NEWS README')
collect_docs('doc/mpdconf.example')
collect_version()
