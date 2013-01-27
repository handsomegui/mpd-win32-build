import toolchain

options = '--enable-openal --enable-mikmod'
libs = '-static-libgcc -static-libstdc++ -lz'

if toolchain.target == toolchain.target_windows:
    libs += ' -lole32'

build(options=options, libs=libs)
collect_binaries('mpd.exe')
collect_licenses('AUTHORS COPYING')
collect_docs('doc/mpdconf.example NEWS README')
