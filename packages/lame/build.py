fetch('http://sourceforge.net/projects/lame/files/lame/3.99/lame-3.99.5.tar.gz/download')

build(shared_lib=True)

collect_binaries('libmp3lame-*.dll')
collect_docs('README COPYING')
