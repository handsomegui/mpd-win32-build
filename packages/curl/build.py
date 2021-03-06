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

build(static_lib=True, options=options)
collect_licenses('COPYING README')
