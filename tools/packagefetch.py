import urllib
import cmdutil, fsutil

from os import path

def fetch(info, force):
    if not info.source:
        raise ValueError('Package source is not specified')
    if info.source.startswith('git://') or info.source.endswith('.git'):
        return _fetch_git(info, force)
    else:
        return _fetch_archive(info, force)

def _fetch_archive(info, force):
    source_file = info.source_file
    if not source_file:
        source_file = _guess_name(info.source)
    file_path = path.join(info.cache_dir, source_file)
    downloaded = _download_once(info.source, file_path)
    if downloaded or force:
        _untar_to_build_dir(info, file_path, strip_root_dir=True)
        return True
    return False

def _guess_name(url):
    download_suffix = '/download'
    if url.startswith('http://sourceforge.net') and url.endswith(download_suffix):
        url = url[0:-len(download_suffix)]
    pos = url.rfind('/')
    if pos < 0 or pos == len(url) - 1:
        raise ValueError('Unable to extract file name from url: ' + url)
    return urllib.unquote(url[pos + 1:])

def _download_once(url, file):
    if path.exists(file):
        return False
    cmdutil.wget(url, file)
    return True

def _fetch_git(info, force):
    if not info.source_rev:
        raise ValueError('Revision to fetch should be specified')
    repo_dir = path.join(info.cache_dir, 'mirror.git')
    if cmdutil.git_check(repo_dir):
        cmdutil.git('fetch', ['--all'], work_dir=repo_dir)
    else:
        cmdutil.git('clone', ['--mirror', info.source, repo_dir])

    info.source_rev = cmdutil.git_short_rev(repo_dir, info.source_rev)
    tar_file = path.join(info.cache_dir, 'rev-%s.tar' % info.source_rev)
    tar_glob = path.join(info.cache_dir, 'rev-*.tar')
    exported = False

    if not path.exists(tar_file):
        fsutil.glob_remove(tar_glob)
        cmdutil.git('archive', ['-o', tar_file, info.source_rev], work_dir=repo_dir)
        exported = True

    if exported or force:
        _untar_to_build_dir(info, tar_file)
        return True
    return False

def _untar_to_build_dir(info, tar_file, strip_root_dir = False):
    info.reset_dirs()
    cmdutil.untar(tar_file, target_dir=info.build_dir, strip_root_dir=strip_root_dir)
