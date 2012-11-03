fetch('http://downloads.xiph.org/releases/ogg/libogg-1.3.0.tar.xz')

build(static_lib=True)

collect_docs('COPYING AUTHORS')
