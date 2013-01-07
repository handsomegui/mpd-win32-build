import inspect, os, sys, shutil, zipfile
import packagebuild, packageinfo, packagefetch, cmdutil, config, fsutil

from os import path
from textwrap import TextWrapper

def join(items):
    return ' '.join(items)

def wrap(prefix, items):
    line = prefix + join(sorted(items))
    wrapper = TextWrapper()
    wrapper.break_on_hyphens = False
    wrapper.subsequent_indent = ' ' * len(prefix)
    return wrapper.fill(line)

def add_prefix(prefix, items):
    return map(lambda s: prefix + s, items)

def run_make(target):
    cmdutil.native_make(['-f', _make_file, target], None)

def check_stamp(info):
    if not path.exists(info.stamp_file):
        return False
    stamp_mtime = path.getmtime(info.stamp_file)
    max_mtime = 0
    for dep_name in info.dependency_map().iterkeys():
        dep_info = packageinfo.get(dep_name)
        for f in [dep_info.stamp_file, dep_info.package_file, dep_info.build_file]:
            if not path.exists(dep_info.stamp_file):
                return False
            max_mtime = max(max_mtime, path.getmtime(f))
    return stamp_mtime >= max_mtime

def log(info, message):
    print "buildtool: %s %s" % (info.name.ljust(16), message)

def do_build(info):
    log(info, 'checking')
    if packagefetch.fetch(info, not check_stamp(info)):
        log(info, 'building')
        packagebuild.run(info)
        fsutil.write_stamp(info.stamp_file)
        log(info, 'done')
    else:
        log(info, 'up to date')

def do_clean(info):
    fsutil.safe_remove_dir(info.work_dir)

def do_clean_cache(info):
    fsutil.safe_remove_dir(info.cache_dir)

def do_rebuild(info):
    do_clean(info)
    do_build(info)

def do_build_all(info):
    do_generate_makefile()
    run_make(info.name)

def do_build_dist(info):
    version = info.version()
    artifacts = info.artifacts()
    dist_name = '%s-%s-%s' % (info.short_name, version, info.dist_host)
    dist_file = path.join(info.dist_dir, dist_name + '.zip')

    with zipfile.ZipFile(dist_file, mode='w', compression=zipfile.ZIP_DEFLATED) as z:
        for source, target in artifacts.iteritems():
            z.write(source, path.join(dist_name, target))
    cmdutil.sha1sum(dist_file)

def do_generate_makefile():
    dependency_map = {}
    for name in packageinfo.get_packages():
        info = packageinfo.get(name)
        dependency_map.update(info.dependency_map())
    names = sorted(dependency_map.iterkeys())
    build_targets = names
    clean_targets = add_prefix('clean-', names)

    with open(_make_file, 'w') as f:
        f.write('export BUILDTOOL_PROFILE  := %s\n' % _config_profile)
        f.write('export BUILDTOOL_BASE_DIR := %s\n\n' % _base_dir)

        f.write('buildtool := %s %s\n\n' % (sys.executable, path.abspath(__file__)))

        f.write('build := $(buildtool) build\n')
        f.write('clean := $(buildtool) clean\n\n')

        f.write('_default:\n')
        f.write('\t@echo No defaults. Please, specify target to build.\n\n')

        f.write('refresh:\n')
        f.write('\t@$(buildtool) generate-makefile\n\n')

        f.write('clean: %s\n\n' % join(clean_targets))

        for name, target in zip(names, build_targets):
            f.write('%s: %s\n' % (target, join(dependency_map[name])))
            f.write('\t@$(build) %s\n\n' % name)

        for name, target in zip(names, clean_targets):
            f.write('%s:\n' % target)
            f.write('\t@$(clean) %s\n\n' % name)

        f.write('.PHONY: _default refresh clean\n')
        f.write('.PHONY: %s\n' % join(build_targets))
        f.write('.PHONY: %s\n' % join(clean_targets))

def build_action_map():
    prefix = 'do_'
    result = {}
    for name, symbol in globals().iteritems():
        if name.startswith(prefix):
            user_name = name[len(prefix):].replace('_', '-')
            result[user_name] = symbol
    return result

def get_action_func(action):
    action_map = build_action_map()
    if not action in action_map:
        raise ValueError('Unknown action: ' + action)
    return action_map[action]

def show_usage():
    print 'buildtool -- perform build action on specified target'
    print
    print 'Usage:   buildtool action [target]'
    print
    print wrap('Actions: ', build_action_map().keys())
    print
    print wrap('Targets: ', packageinfo.get_packages())
    print
    print 'See supplied README file for more details'

def init():
    global _config_profile
    global _base_dir
    global _make_file

    _config_profile = os.environ.get('BUILDTOOL_PROFILE', '')
    if _config_profile and (not packageinfo.valid_name(_config_profile)):
        raise ValueError('Invalid profile name: ' + _config_profile)
    
    _base_dir = os.environ.get('BUILDTOOL_BASE_DIR', os.getcwd())

    config.init(_config_profile)
    packageinfo.init(_base_dir, _config_profile)
    
    _make_file = path.join(packageinfo.get_work_dir(), 'Makefile')

def run(action, targets):
    action_func = get_action_func(action)

    if inspect.getargspec(action_func).args:
        if not targets:
            raise ValueError('No target specified')
        for t in targets:
            action_func(packageinfo.get(t))
    else:
        action_func()

if __name__=='__main__':
    init()
    if len(sys.argv) <= 1:
        show_usage()
        sys.exit(1)
    run(sys.argv[1], sys.argv[2:])
