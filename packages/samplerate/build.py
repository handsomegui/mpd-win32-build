fetch('http://www.mega-nerd.com/SRC/libsamplerate-0.1.8.tar.gz')
remove('make.bat') # Remove make.bat because it gets executed instead of make.exe from PATH

build(static_lib=True, options='--disable-sndfile')

collect_docs('COPYING AUTHORS')
