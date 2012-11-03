fetch('http://sourceforge.net/projects/musicpd/files/libmpdclient/2.7/libmpdclient-2.7.tar.bz2/download')

build(static_lib=True)

collect_licenses('AUTHORS COPYING NEWS README')
