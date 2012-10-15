fetch('http://kcat.strangesoft.net/openal-releases/openal-soft-1.14.tar.bz2')
patch('CMakeLists.txt')
patch('Alc/alcConfig.c')

build_cmake(options='-DMMDEVAPI=OFF')

collect_binaries('OpenAL32.dll')
collect_docs('COPYING README')
collect_files('alsoftrc.sample', target_dir='conf')
