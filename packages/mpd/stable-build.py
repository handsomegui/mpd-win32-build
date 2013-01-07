fetch('git://git.musicpd.org/master/mpd.git', 'v0.17.x')
include('common/build')
collect_version(include_rev=True)
