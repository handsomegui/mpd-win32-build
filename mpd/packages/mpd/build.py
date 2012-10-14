from package import *

package('mpd')

clone('git://git.musicpd.org/master/mpd.git', 'v0.17.x')
build(options='--enable-openal')

collect_system_libs(libgcc=True)
collect_binaries('mpd.exe')

collect_docs('AUTHORS COPYING NEWS README')
collect_files('doc/mpdconf.example', target_dir='conf')

collect_version()
