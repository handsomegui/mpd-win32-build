fetch('http://downloads.xiph.org/releases/ogg/libogg-1.3.0.tar.xz')

build(shared_lib=True)

collect_binaries('libogg-*.dll')
collect_docs('COPYING AUTHORS')
