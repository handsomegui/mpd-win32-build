patch('gme/CMakeLists.txt')
build_cmake()
generate_pkg_config('libgme', version='0.5.5')
collect_licenses('license.txt readme.txt')
