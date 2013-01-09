patch('gme/CMakeLists.txt')
build_cmake()
generate_pkg_config()
collect_licenses('license.txt readme.txt')
