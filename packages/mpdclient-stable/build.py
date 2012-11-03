clone('git://git.musicpd.org/master/libmpdclient.git')

build(static_lib=True)

collect_licenses('AUTHORS COPYING NEWS README')
