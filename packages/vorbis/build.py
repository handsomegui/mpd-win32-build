fetch('http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.3.tar.xz')

build(static_lib=True)

collect_docs('COPYING AUTHORS')
