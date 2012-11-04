#fetch('http://sourceforge.net/projects/musicpd/files/mpd/0.17.2/mpd-0.17.2.tar.bz2/download')
fetch('git://git.musicpd.org/master/mpd.git', 'release-0.17.2')

include('common/build')
