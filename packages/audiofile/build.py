fetch('http://audiofile.68k.org/audiofile-0.3.4.tar.gz')

build(static_lib=True)
collect_licenses('ACKNOWLEDGEMENTS AUTHORS COPYING README')
