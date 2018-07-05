#!/usr/bin/env python3
import os
import sys
import configparser
from itertools import chain
import subprocess
import io

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_config(hrdfile):
    config = configparser.ConfigParser()
    origget = config.get
    def get(*args, **kwargs):
        if len(args) < 2:
            args = list(args)
            args.insert(0, 'hrd')
        return origget(*args, **kwargs).strip("'")

    config.get = get
    with open(hrdfile) as lines:
        lines = chain(("[hrd]",), lines)
        config.read_file(lines)
        return config

class SSHConfigGenerator:
    def __init__(self, rootpath, reponame, controller):
        self._rootpath = rootpath
        self._reponame = reponame
        if controller is None:
            self._controller = 22
        else:
            self._controller = controller
        if not rootpath and not reponame:
            raise RuntimeError("Pass either rootpath or reponame")
        self._host = None
        self._identityfile = None

    @property
    def host(self):
        if self._host is None:
            self._host = self.get_env_host()
        return self._host

    @property
    def rootpath(self):
        if self._rootpath is None:
            assert self._reponame is not None
            rootdir = '/opt/code/github'
            if not os.access(rootdir, os.W_OK):
                rootdir = os.path.expanduser('~/code/github/')
            rootdir = os.path.join(rootdir, 'gig-projects')
            os.makedirs(rootdir, exist_ok=True)
            repodirname = 'env_%s' % self._reponame
            repourl = 'git@github.com:gig-projects/%s' % repodirname
            rootpath = os.path.expanduser(os.path.join(rootdir, repodirname))
            if not os.path.exists(rootpath):
                proc = subprocess.Popen(['git', 'clone', repourl], cwd=rootdir, stdin=subprocess.PIPE, stderr=sys.stderr, stdout=sys.stderr)
            else:
                proc = subprocess.Popen(['git', 'pull'], cwd=rootpath, stdin=subprocess.PIPE, stderr=sys.stderr, stdout=sys.stderr)
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError("Failed to clone/update repo %s" % rootpath)
            self._rootpath = rootpath

        if not os.path.exists(self._rootpath):
            raise RuntimeError("Rootpath %s does not exists!" % self._rootpath)

        return self._rootpath

    @property
    def identityfile(self):
        if self._identityfile is None:
            self._identityfile = os.path.abspath(os.path.join(self.rootpath, 'keys', 'git_root'))
            if not os.path.exists(self._identityfile):
                eprint('Could not find private key %s' % self._identityfile)
                sys.exit(1)
            os.chmod(self._identityfile, 0o600)
        return self._identityfile


    def get_services(self, pattern):
        for dirpath, dirnames, filenames in os.walk(self.rootpath):
            if pattern in dirpath:
                dirnames[:] = []
                servicefile = os.path.join(dirpath, 'service.hrd')
                if os.path.exists(servicefile):
                    yield servicefile

    def get_hostname(self, name):
        host, _, domain = name.partition('.')
        if host.startswith('ovc_'):
            host = host[4:]
            domain = os.path.basename(self.rootpath)
            if domain.startswith('env_'):
                domain = domain[4:]
        if domain:
            host = '%s-%s' % (domain, host)
        return host

    def get_env_host(self):
        config = get_config(next(self.get_services('__ssloffloader__')))
        return config.get('instance.host')

    def print_git(self):
        print("Host %s" % self.get_hostname('ovc_git'))
        print("  Hostname %s" % self.host)
        print("  User root")
        print("  IdentityFile %s" % self.identityfile)
        print("")


    def print_host(self, host, reflector=None, reflectorport=None):
        print("Host %s" % host)
        print("  Hostname %s" % reflector)
        print("  Port %s" % reflectorport)
        print("  User root")
        print("  IdentityFile %s" % self.identityfile)
        print("  ProxyCommand ssh -A -i %s -q root@%s -p %s nc -q0 %%h %%p" % (self.identityfile, self.host, self._controller))
        print("")

    def generate(self):
        self.print_git()
        for servicefile in self.get_services('__node.ssh__'):
            config = get_config(servicefile)
            instance = config.get('service.instance')
            reflector = config.get('instance.ip')
            reflectorport = config.get('instance.ssh.port')
            host = self.get_hostname(instance)
            self.print_host(host, reflector, reflectorport)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(usage="Generate ssh config for environmetns")
    parser.add_argument('-p', '--path', help="repo path", default=None)
    parser.add_argument('-c', '--controller', help="controller port", default=None)
    parser.add_argument('-r', '--reponame', help="Name of the repo", default=None)
    options = parser.parse_args()
    generator = SSHConfigGenerator(options.path, options.reponame, options.controller)
    generator.generate()
