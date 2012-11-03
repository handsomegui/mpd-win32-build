fetch('http://ftp.gnome.org/pub/gnome/sources/glib/2.28/glib-2.28.8.tar.xz')
patch('Makefile.in')
patch('glib/Makefile.in', patch_file='glib_Makefile.in.patch')
patch('gthread/Makefile.in', patch_file='gthread_Makefile.in.patch')

build(static_lib=True)

collect_licenses('COPYING README')
