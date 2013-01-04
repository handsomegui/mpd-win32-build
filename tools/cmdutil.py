import os, sys, subprocess
import config

from os import path

_output_file = None

def _exec(app, args, work_dir, extra_env, save_output):
    all_args = [app]
    if args:
        all_args.extend(args)

    all_env = os.environ.copy()
    if extra_env:
        all_env.update(extra_env)

    cmd = ' '.join(all_args)

    if _output_file and (not save_output):
        with open(_output_file, 'a') as f:
            f.write('\n')
            if extra_env:
                for var in sorted(extra_env.iterkeys()):
                    f.write('%s = %s\n' % (var, extra_env[var]))
                f.write('\n')
            f.write('%s\n\n' % cmd)
        cmd = '%s >>%s 2>&1' % (cmd, _output_file)

    if save_output:
        return subprocess.check_output(cmd, cwd=work_dir, env=all_env, shell=True)
    else:
        subprocess.check_call(cmd, cwd=work_dir, env=all_env, shell=True)

def _build_exec_path(path_vars):
    paths = []
    for var in path_vars:
        value = config.get(var)
        if value:
            paths.append(value)
    paths.append(os.environ['PATH'])
    return os.pathsep.join(paths)

def _add_exec_path(env, exec_path):
    result = {}
    if env:
        result.update(env)
    result['PATH'] = exec_path
    return result

def _native_exec_path():
    return _build_exec_path(['path'])

def native_exec(app, args = None, work_dir = None, extra_env = None, save_output = False):
    extra_env = _add_exec_path(extra_env, _native_exec_path())
    return _exec(app, args, work_dir, extra_env, save_output)

if sys.platform.startswith('win32'):

    on_windows = True

    def _unix_exec_path():
        return _build_exec_path(['unix_path', 'path'])

    def unix_exec(app, args = None, work_dir = None, extra_env = None, save_output = False):
        extra_env = _add_exec_path(extra_env, _unix_exec_path())
        return _exec(app, args, work_dir, extra_env, save_output)

    def native_make(args, work_dir):
        return native_exec('mingw32-make', args, work_dir)

    def to_unix_path(p):
        if path.isabs(p):
            return '/' + p[0].lower() + p[2:].replace('\\', '/')
        else:
            return p.replace('\\', '/')

    def to_cmake_path(p):
        return p.replace('\\', '/')

else:

    on_windows = False

    def _unix_exec_path():
        return _native_exec_path()

    def unix_exec(app, args = None, work_dir = None, extra_env = None, save_output = False):
        return native_exec(app, args, work_dir, extra_env, save_output)

    def native_make(args, work_dir):
        return native_exec('make', args, work_dir)

    def to_unix_path(p):
        return p

    def to_cmake_path(p):
        return p

def unix_make(targets, work_dir):
    return unix_exec('make', targets, work_dir)

def git(action, args = None, work_dir = None):
    all_args = [action]
    if args:
        all_args.extend(args)
    native_exec('git', all_args, work_dir)

def git_check(target_dir):
    if target_dir.endswith('.git'):
        head_file = path.join(target_dir, 'HEAD')
    else:
        head_file = path.join(target_dir, '.git', 'HEAD')
    return path.exists(head_file)
    
def git_short_rev(target_dir, rev = 'HEAD'):
    args = ['rev-parse', '--short', rev]
    output = native_exec('git', args, work_dir=target_dir, save_output=True)
    return output.strip()

def untar(file, target_dir = None, strip_root_dir = False):
    args = ['xf', to_unix_path(file)]
    if strip_root_dir:
        args.extend(['--strip', '1'])
    unix_exec('tar', args, target_dir)

def patch(target_file, patch_file):
    args = [to_unix_path(target_file), to_unix_path(patch_file)]
    unix_exec('patch', args)

def wget(url, output_file = None):
    args = [url]
    if output_file:
        args.extend(['-O', to_unix_path(output_file)])
    unix_exec('wget', args)

def which(command):
    if on_windows:
        command += '.exe'
    paths = _native_exec_path().split(os.pathsep)
    for item in paths:
        full_path = path.join(item, command)
        if path.exists(full_path):
            return full_path
    return None

def gcc_lib_dir(gcc):
    output = native_exec(gcc, ['-print-libgcc-file-name'], save_output=True)
    return path.dirname(path.normpath(output.strip()))

def redirect_output(output_file):
    global _output_file
    _output_file = output_file
