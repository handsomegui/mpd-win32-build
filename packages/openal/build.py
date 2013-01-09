patch('CMakeLists.txt')
patch('Alc/alcConfig.c')
build_cmake(options='-DMMDEVAPI=OFF -DEXAMPLES=OFF')
collect_binaries('OpenAL32.dll')
collect_binaries('openal-info.exe')
collect_licenses('COPYING README')
collect_docs('alsoftrc.sample')
