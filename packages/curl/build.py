options = """
    --enable-http
    --enable-file
    --disable-ftp
    --disable-ldap
    --disable-ldaps
    --disable-dict
    --disable-proxy
    --disable-telnet
    --disable-tftp
    --disable-pop3
    --disable-imap
    --disable-smtp
    --disable-gopher
    --disable-manual
    --disable-sspi
    --disable-crypto-auth
    --without-ssl
    --without-winssl
"""

fetch('http://curl.haxx.se/download/curl-7.27.0.tar.lzma')
build(shared_lib=True, options=options)

collect_binaries('libcurl-*.dll')
collect_docs('COPYING README')
