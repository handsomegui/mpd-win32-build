patch('CMakeLists.txt')
patch('libmpcdec/CMakeLists.txt', patch_file='libmpcdec_CMakeLists.txt.patch')
build_cmake(options='-DSHARED=OFF')
collect_licenses('AUTHORS COPYING', source_dir='libmpcdec')
