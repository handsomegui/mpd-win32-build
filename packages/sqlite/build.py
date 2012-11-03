fetch('http://www.sqlite.org/sqlite-autoconf-3071401.tar.gz')

build(static_lib=True, options='--disable-dynamic-extensions')
