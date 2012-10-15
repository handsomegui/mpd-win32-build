fetch('http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.3.tar.xz')

build(shared_lib=True)

collect_binaries('libvorbis-*.dll libvorbisfile-*.dll libvorbisenc-*.dll')
collect_docs('COPYING AUTHORS')
