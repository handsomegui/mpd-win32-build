clone('git://git.musicpd.org/master/mpd.git', 'v0.17.x')

build(options='--enable-openal', libs='-lz -lole32 -static-libgcc')

collect_binaries('mpd.exe')
collect_docs('AUTHORS COPYING NEWS README')
collect_files('doc/mpdconf.example', target_dir='conf')
collect_version()
