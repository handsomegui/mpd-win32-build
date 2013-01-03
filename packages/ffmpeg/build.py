fetch('http://ffmpeg.org/releases/ffmpeg-1.0.1.tar.bz2')

# build options are taken from
# https://github.com/lalinsky/build-scripts/blob/master/ffmpeg/common.sh

options = """
    --disable-debug
    --disable-avdevice
    --disable-avfilter
    --disable-swscale
    --enable-ffmpeg
    --disable-ffplay
    --disable-ffserver
    --disable-network
    --disable-muxers
    --disable-demuxers
    --disable-zlib
    --enable-rdft
    --enable-demuxer=aac
    --enable-demuxer=ac3
    --enable-demuxer=aiff
    --enable-demuxer=ape
    --enable-demuxer=asf
    --enable-demuxer=au
    --enable-demuxer=flac
    --enable-demuxer=matroska_audio
    --enable-demuxer=mov
    --enable-demuxer=mp2
    --enable-demuxer=mp3
    --enable-demuxer=mp4
    --enable-demuxer=mpc
    --enable-demuxer=mpc8
    --enable-demuxer=ogg
    --enable-demuxer=shorten
    --enable-demuxer=tta
    --enable-demuxer=wav
    --enable-demuxer=wv
    --enable-demuxer=image2
    --disable-bsfs
    --disable-filters
    --disable-parsers
    --enable-parser=aac
    --enable-parser=ac3
    --enable-parser=mpegaudio
    --disable-protocols
    --enable-protocol=file
    --disable-indevs
    --disable-outdevs
    --disable-encoders
    --disable-decoders
    --enable-decoder=aac
    --enable-decoder=aac_latm
    --enable-decoder=ac3
    --enable-decoder=ac3_fixed
    --enable-decoder=alac
    --enable-decoder=ape
    --enable-decoder=atrac1
    --enable-decoder=atrac3
    --enable-decoder=flac
    --enable-decoder=mp1
    --enable-decoder=mp2
    --enable-decoder=mp3
    --enable-decoder=mp3on4
    --enable-decoder=mpc7
    --enable-decoder=mpc8
    --enable-decoder=shorten
    --enable-decoder=tta
    --enable-decoder=vorbis
    --enable-decoder=wavpack
    --enable-decoder=wmalossless
    --enable-decoder=wmapro
    --enable-decoder=wmav1
    --enable-decoder=wmav2
    --enable-decoder=wmavoice
    --enable-decoder=pcm_alaw
    --enable-decoder=pcm_dvd
    --enable-decoder=pcm_f32be
    --enable-decoder=pcm_f32le
    --enable-decoder=pcm_f64be
    --enable-decoder=pcm_f64le
    --enable-decoder=pcm_s16be
    --enable-decoder=pcm_s16le
    --enable-decoder=pcm_s16le_planar
    --enable-decoder=pcm_s24be
    --enable-decoder=pcm_daud
    --enable-decoder=pcm_s24le
    --enable-decoder=pcm_s32be
    --enable-decoder=pcm_s32le
    --enable-decoder=pcm_s8
    --enable-decoder=pcm_u16be
    --enable-decoder=pcm_u16le
    --enable-decoder=pcm_u24be
    --enable-decoder=pcm_u24le
    --enable-decoder=rawvideo
    --enable-memalign-hack
"""

if info.crossbuild:
    options += ' --enable-cross-compile --arch=x86 --target-os=mingw32 --cross-prefix=' + info.crossbuild_host + '-'

build(static_lib=True, options=options, crossbuild_options=False)

collect_licenses('LICENSE COPYING.LGPLv2.1')
