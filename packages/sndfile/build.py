fetch('http://www.mega-nerd.com/libsndfile/files/libsndfile-1.0.25.tar.gz')

build(static_lib=True, options='--disable-external-libs --disable-alsa --disable-sqlite')

collect_docs('COPYING AUTHORS')
