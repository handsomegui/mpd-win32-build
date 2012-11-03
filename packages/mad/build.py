fetch('git://gitorious.org/mad/libmad.git', '637baad')

build(static_lib=True)

collect_licenses('COPYRIGHT COPYING CREDITS')
