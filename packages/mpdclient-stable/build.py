clone('git://git.musicpd.org/master/libmpdclient.git')

build(static_lib=True)

collect_docs('AUTHORS COPYING NEWS README')
