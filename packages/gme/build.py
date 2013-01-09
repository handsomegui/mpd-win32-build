patch('gme/CMakeLists.txt')
build_cmake()
generate_pkg_config('libgme')
collect_licenses('license.txt readme.txt')
