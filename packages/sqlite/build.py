fetch('http://www.sqlite.org/sqlite-autoconf-3071501.tar.gz')

build(static_lib=True, options='--disable-dynamic-extensions')
