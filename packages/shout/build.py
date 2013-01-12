patch('include/shout/shout.h.in')
build(static_lib=True, options='--disable-thread')
collect_licenses('README COPYING')
