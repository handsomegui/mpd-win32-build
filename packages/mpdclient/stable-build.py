fetch('git://git.musicpd.org/master/libmpdclient.git', 'master')

build(static_lib=True)

collect_licenses('AUTHORS COPYING NEWS README')
