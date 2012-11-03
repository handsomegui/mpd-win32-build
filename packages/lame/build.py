fetch('http://sourceforge.net/projects/lame/files/lame/3.99/lame-3.99.5.tar.gz/download')

build(static_lib=True)

collect_docs('README COPYING')
