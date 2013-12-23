import os
import os.path as path
import stat
import sys
import shutil
import tempfile
import subprocess
import urllib2
import tarfile
import logging
import zipfile

from pip.download import unpack_http_url
from pip.index import PackageFinder
from pip.req import InstallRequirement, RequirementSet
from pip.locations import build_prefix, src_prefix


PYTHONPATH = 'PYTHONPATH'


class BuildLocations(object):

    def __init__(self, ctx_root):
        self.root = mkdir(path.join(ctx_root, 'build'))
        self.dist = mkdir(path.join(ctx_root, 'dist'))
        self.dist_lib = mkdir(path.join(self.dist, 'lib'))
        self.dist_python = mkdir(path.join(self.dist_lib, 'python'))
        self.files = mkdir(path.join(ctx_root, 'files'))


class DeploymentLocations(object):

    def __init__(self, ctx_root, project_name):
        self.root = mkdir(path.join(ctx_root, 'layout'))

        self.usr = mkdir(path.join(self.root, 'usr'))
        self.usr_share = mkdir(path.join(self.usr, 'share'))
        self.project_share = mkdir(path.join(self.usr_share, project_name))

        self.etc = mkdir(path.join(self.root, 'etc'))
        self.init_d = mkdir(path.join(self.etc, 'init.d'))


class BuildContext(object):

    def __init__(self, ctx_root, pkg_index, project_name):
        self.root = ctx_root
        self.pkg_index = pkg_index
        self.deploy = DeploymentLocations(ctx_root, project_name)
        self.build = BuildLocations(ctx_root)


def read(relative):
    contents = open(relative, 'r').read()
    return [l for l in contents.split('\n') if l != '']


def mkdir(location):
    if not path.exists(location):
        os.mkdir(location)
    return location


def download(url, dl_location):
    u = urllib2.urlopen(url)
    localFile = open(dl_location, 'w')
    localFile.write(u.read())
    localFile.close()


def run_python(bctx, cmd, cwd=None):
    env = os.environ.copy()
    env[PYTHONPATH] = bctx.build.dist_python
    run(cmd, cwd, env)


def run(cmd, cwd=None, env=None):
    print('>>> Exec: {}'.format(cmd))
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        close_fds=True)

    done = False
    while not done:
        line = proc.stdout.readline()
        if line:
            print(line.rstrip('\n'))
        else:
            done = True

    if proc.returncode and proc.returncode != 0:
        print('Failed with return code: {}'.format(proc.returncode))
        sys.exit(1)


def unpack(name, bctx, stage_hooks, filename, dl_target):
    if dl_target.endswith('.tar.gz') or dl_target.endswith('.tgz'):
        archive = tarfile.open(dl_target, mode='r|gz')
        build_location = path.join(
            bctx.build.root, filename[:-7])
    elif dl_target.endswith('.tar.bz2'):
        archive = tarfile.open(dl_target, mode='r|bz2')
        build_location = path.join(
            bctx.build.root, filename[:-8])
    elif dl_target.endswith('.zip'):
        archive = zipfile.ZipFile(dl_target, mode='r')
        build_location = path.join(bctx.build.root, filename[:-4])
    else:
        print('Unknown archive format: {}'.format(dl_target))
        raise Exception()

    archive.extractall(bctx.build.root)
    return build_location


def install_req(name, bctx, stage_hooks=None):
    req = InstallRequirement.from_line(name, None)
    found_req = bctx.pkg_index.find_requirement(req, False)
    dl_target = path.join(bctx.build.files, found_req.filename)

    # stages
    call_hook(name, 'download.before',
              stage_hooks, bctx=bctx, fetch_url=found_req.url)
    download(found_req.url, dl_target)
    call_hook(name, 'download.after',
              stage_hooks, bctx=bctx, archive=dl_target)

    call_hook(name, 'unpack.before',
              stage_hooks, bctx=bctx, archive=dl_target)
    build_location = unpack(
        name, bctx, stage_hooks, found_req.filename, dl_target)
    call_hook(name, 'unpack.after',
              stage_hooks, bctx=bctx, build_location=build_location)

    call_hook(name, 'build.before',
              stage_hooks, bctx=bctx, build_location=build_location)
    run_python(
        bctx,
        'python setup.py build'.format(build_location),
        build_location)
    call_hook(name, 'build.after',
              stage_hooks, bctx=bctx, build_location=build_location)

    call_hook(name, 'install.before',
              stage_hooks, bctx=bctx, build_location=build_location)
    run_python(
        bctx,
        'python setup.py install --home={}'.format(bctx.build.dist),
        build_location)
    call_hook(name, 'install.after',
              stage_hooks, bctx=bctx, build_location=build_location)


def call_hook(name, stage, stage_hooks, **kwargs):
    if stage_hooks:
        if name in stage_hooks:
            hooks = stage_hooks[name]
            if stage in hooks:
                hook = hooks[stage]
                print('Calling hook {} for stage {}'.format(hook, stage))
                hook(kwargs)


def read_requires(filename, bctx, pkg_index, hooks):
    lines = open(filename, 'r').read()

    if not lines:
        raise Exception()

    for line in lines.split('\n'):
        if line and len(line) > 0:
            install_req(line, bctx, hooks)


def copytree(src, dst, symlinks=False):
    names = os.listdir(src)
    if not os.path.exists(dst):
        os.makedirs(dst)

    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)

        if symlinks and os.path.islink(srcname):
            linkto = os.readlink(srcname)
            os.symlink(linkto, dstname)
        elif os.path.isdir(srcname):
            copytree(srcname, dstname, symlinks)
        else:
            shutil.copy2(srcname, dstname)


def build(requirements_file, hooks, project_name, version):
    # Pip package finder is used to locate dependencies for downloading
    pkg_index = PackageFinder(
        find_links=[],
        index_urls=["http://pypi.python.org/simple/"])

    # Build context holds all of the directories and state information
    bctx = BuildContext(tempfile.mkdtemp(), pkg_index, project_name)

    # Build the project requirements and install them
    read_requires(requirements_file, bctx, pkg_index, hooks)

    # Build root after requirements are finished
    run_python(bctx, 'python setup.py build')
    run_python(bctx, 'python setup.py install --home={}'.format(
        bctx.build.dist))

    # Copy all of the important files into their intended destinations
    local_layout = path.join('.', 'pkg/layout')
    copytree(local_layout, bctx.deploy.root)

    # Copy the built virtualenv
    copytree(bctx.build.dist, bctx.deploy.project_share)

    # Let's build a tarfile
    tar_filename = '{}_{}.tar.gz'.format(project_name, version)
    tar_fpath = path.join(bctx.root, tar_filename)

    # Open the
    tarchive = tarfile.open(tar_fpath, 'w|gz')
    tarchive.add(bctx.deploy.root, arcname='')
    tarchive.close()

    # Copy the finished tafile
    shutil.copyfile(tar_fpath, path.join('.', tar_filename))

    # Clean the build dir
    print('Cleaning {}'.format(bctx.root))
    shutil.rmtree(bctx.root)


hooks = {
}

requirements_file = 'tools/pip-requires'

if len(sys.argv) != 2:
    print('usage: build.py <project-name>')
    exit(1)

version = read('VERSION')[0]

build(requirements_file, hooks, sys.argv[1], version)
