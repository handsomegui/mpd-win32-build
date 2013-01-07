fetch('http://www.mega-nerd.com/SRC/libsamplerate-0.1.8.tar.gz')

# Remove Make.bat because it gets executed instead of make.exe from PATH
remove('Make.bat')

build(static_lib=True, options='--disable-sndfile')

collect_licenses('COPYING AUTHORS')
