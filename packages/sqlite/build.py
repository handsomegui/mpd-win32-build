fetch('http://www.sqlite.org/sqlite-autoconf-3071401.tar.gz')

build(shared_lib=True, options='--disable-dynamic-extensions')

collect_binaries('libsqlite3-*.dll')
