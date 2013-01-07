options = '--with-included-gettext --enable-threads=win32 --disable-libasprintf --disable-java'
build(static_lib=True, options=options, subdir='gettext-runtime')
collect_licenses('AUTHORS intl/COPYING.LIB-2.1', source_dir='gettext-runtime')
