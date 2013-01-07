build(options='--enable-openal', libs='-lz -lole32 -static-libgcc -static-libstdc++')
collect_binaries('mpd.exe')
collect_licenses('AUTHORS COPYING')
collect_docs('doc/mpdconf.example NEWS README')
