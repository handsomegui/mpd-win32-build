import os, sys, shutil, inspect, zipfile
import package, packageinfo, cmdutil, config, fsutil

from os import path
from textwrap import TextWrapper

def join(strings):
    return ' '.join(strings)

def add_prefix(prefix, items):
    return map(lambda s: prefix + s, items)

def get_action_func(action):
    action_map = build_action_map()
    if not action in action_map:
        raise ValueError('Unknown action: ' + action)
    return action_map[action]

def wipe_dir(dir):
    if not path.exists(dir):
        return
    if cmdutil.git_check(dir):
        cmdutil.git('clean', ['-q', '-f', '-x', '-d'], work_dir=dir)
    else:
        shutil.rmtree(dir)

def git_fetch_mirror(info):
    cached_repo = path.join(info.cache_dir, 'mirror.git')
    if cmdutil.git_check(cached_repo):
        cmdutil.git('fetch', ['--all'], work_dir=cached_repo)

def git_in_build_dir(info, action):
    if cmdutil.git_check(info.build_dir):
        cmdutil.git(action, work_dir=info.build_dir)

def run_make(target, info):
    cmdutil.native_make(['-f', info.make_file, target], None)

def visible_to_builder(obj):
    return (inspect.isfunction(obj)
      and (not obj.func_name.startswith('_'))
      and obj.func_name!='init')

def do_build(info):
    package.init(info)
    symbols = dict(inspect.getmembers(package, visible_to_builder))
    symbols['info'] = info
    execfile(info.build_file, symbols)

def do_pull_source(info):
    git_fetch_mirror(info)
    git_in_build_dir(info, 'pull')

def do_fetch_source(info):
    git_fetch_mirror(info)
    git_in_build_dir(info, 'fetch')

def do_clean(info):
    wipe_dir(info.build_dir)
    wipe_dir(info.install_dir)
    fsutil.safe_remove(info.log_file)

def do_clean_cache(info):
    wipe_dir(info.cache_dir)

def do_rebuild(info):
    do_clean(info)
    do_build(info)

def do_pack_zip(info):
    version = info.version()
    artifacts = info.artifacts()
    dist_name = '%s-%s-%s' % (info.dist_name, version, info.dist_host)
    dist_file = path.join(info.dist_dir, dist_name + '.zip')

    with zipfile.ZipFile(dist_file, mode='w', compression=zipfile.ZIP_DEFLATED) as z:
        for source, target in artifacts.iteritems():
            z.write(source, path.join(dist_name, target))

def do_pack_nsis(info):
    version = info.version()
    artifacts = info.artifacts()

    inst_dirs = {}
    for source, target in artifacts.iteritems():
        inst_dirs.setdefault(path.dirname(target), []).append(source)

    core_script = path.join(path.dirname(path.abspath(__file__)), 'core.nsh')
    installer_script = path.join(info.dist_dir, info.name + '.nsi')

    with open(installer_script, 'w') as f:
        f.write('!define AppId      "%s"\n' % info.dist_name)
        f.write('!define AppName    "%s"\n' % info.name)
        f.write('!define AppVersion "%s"\n\n' % version)

        f.write('!macro INSTALL_FILES\n')
        for dir, files in inst_dirs.iteritems():
            f.write('SetOutPath "$INSTDIR\\%s"\n' % dir)
            for file in files:
                f.write('File "%s"\n' % file)
        f.write('!macroend\n\n')

        f.write('!macro UNINSTALL_FILES\n')
        for file in artifacts.itervalues():
            f.write('Delete "$INSTDIR\\%s"\n' % file)
        for dir in inst_dirs.iterkeys():
            f.write('RMDir "$INSTDIR\\%s"\n' % dir)
        f.write('!macroend\n\n')

        f.write('!include "%s"\n' % core_script)
    cmdutil.native_exec('makensis', ['-V2', installer_script])

def do_build_all(info):
    do_generate_makefile(info)
    run_make('build', info)

def do_clean_all(info):
    do_generate_makefile(info)
    run_make('clean', info)

def do_rebuild_all(info):
    do_generate_makefile(info)
    run_make('clean', info)
    run_make('build', info)

def do_generate_makefile(info):
    dependency_map = info.dependency_map()
    names = sorted(dependency_map.iterkeys())
    build_targets = add_prefix('build-', names)
    clean_targets = add_prefix('clean-', names)

    with open(info.make_file, 'w') as f:
        f.write('export BUILDTOOL_PROFILE  := %s\n' % config_profile)
        f.write('export BUILDTOOL_BASE_DIR := %s\n\n' % base_dir)
        f.write('buildtool := %s %s\n\n' % (sys.executable, path.abspath(__file__)))
        f.write('build := $(buildtool) build\n')
        f.write('clean := $(buildtool) clean\n\n')

        f.write('build: build-%s\n\n' % info.name)
        f.write('clean: %s\n\n' % join(clean_targets))

        for name, target in zip(names, build_targets):
            dependencies = add_prefix('build-', dependency_map[name])
            f.write('%s: %s\n' % (target, join(dependencies)))
            f.write('\t@$(build) %s\n\n' % name)

        for name, target in zip(names, clean_targets):
            f.write('%s:\n' % target)
            f.write('\t@$(clean) %s\n\n' % name)

        f.write('.PHONY: build clean\n')
        f.write('.PHONY: %s\n' % join(build_targets))
        f.write('.PHONY: %s\n' % join(clean_targets))

def build_action_map():
    result = {}
    for name, symbol in globals().items():
        if name.startswith('do_'):
            real_name = name[3:].replace('_', '-')
            result[real_name] = symbol
    return result

def fancy_list(prefix, items):
    line = prefix + join(sorted(items))
    wrapper = TextWrapper()
    wrapper.break_on_hyphens = False
    wrapper.subsequent_indent = ' ' * len(prefix)
    return wrapper.fill(line)

def show_usage():
    print 'buildtool -- perform build action on specified target'
    print
    print 'Usage:   buildtool [action] [target]'
    print
    print fancy_list('Actions: ', build_action_map().keys())
    print
    print fancy_list('Targets: ', packageinfo.get_packages())

def init():
    global config_profile
    global base_dir

    config_profile = os.environ.get('BUILDTOOL_PROFILE', '')
    if config_profile and (not packageinfo.valid_name(config_profile)):
        raise ValueError('Invalid profile name: ' + config_profile)
    
    base_dir = os.environ.get('BUILDTOOL_BASE_DIR', os.getcwd())

    config.init(config_profile)
    packageinfo.init(base_dir, config_profile)

def run(action, target):
    action_func = get_action_func(action)
    info = packageinfo.get(target)
    action_func(info)

if __name__=='__main__':
    init()
    if len(sys.argv) == 3:
        run(sys.argv[1], sys.argv[2])
    else:
        show_usage()
        sys.exit(1)
