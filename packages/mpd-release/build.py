fetch('http://sourceforge.net/projects/musicpd/files/mpd/0.17.2/mpd-0.17.2.tar.bz2/download')

build(options='--enable-openal', libs='-lz -lole32 -static-libgcc')

collect_binaries('mpd.exe')
collect_docs('AUTHORS COPYING NEWS README')
collect_files('doc/mpdconf.example', target_dir='conf')
collect_version()
