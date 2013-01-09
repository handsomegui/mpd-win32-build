patch('configure.ac')
options = '--enable-openal --enable-mikmod'
libs = '-lz -lole32 -static-libgcc -static-libstdc++'
build(options=options, libs=libs)
collect_binaries('mpd.exe')
collect_licenses('AUTHORS COPYING')
collect_docs('doc/mpdconf.example NEWS README')
