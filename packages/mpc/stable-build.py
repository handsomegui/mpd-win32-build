fetch('git://git.musicpd.org/master/mpc.git', 'master')
include('common/build')
collect_version(include_rev=True)
