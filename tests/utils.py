import os
import subprocess
import time
import re


TSURU_TARGET = os.environ.get("TSURU_TARGET", "localhost:8080")


class CmdError(Exception):
    def __init__(self, cmds, exit_code, stdout, stderr):
        self.cmds = cmds
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "Error running '{}', return code {}\nstdout:\n{}\nstderr:\n{}".format(
            ' '.join(self.cmds),
            self.exit_code,
            self.stdout,
            self.stderr,
        )


class Cmd(object):

    def __init__(self, cmd, token=None, root_params=None):
        self.cmd = cmd
        self.token = token
        self.root_params = root_params or []

    def __call__(self, *args, **kwargs):
        new_root = []
        new_root.extend(self.root_params)
        new_root.extend(args)
        return Cmd(self.cmd, token=self.token, root_params=new_root)

    def __getattr__(self, name):
        def cmd(*args, **kwargs):
            cmds = []
            if self.cmd:
                cmds.append(self.cmd)
            cmds.extend(self.root_params)
            cmds.append(name.replace("_", "-"))
            cmds.extend(args)

            stdin = kwargs.get('stdin')
            stdin_pipe = None
            if stdin:
                stdin_pipe = subprocess.PIPE

            print("Executing '{}'".format(" ".join(cmds)))

            envs = {}
            envs.update(os.environ)
            envs.update(kwargs.get('envs') or {})

            token = kwargs.get('token', self.token)
            if token:
                envs['TSURU_TOKEN'] = token

            if not TSURU_TARGET:
                raise Exception("TSURU_TARGET env cannot be empty")
            envs['TSURU_TARGET'] = TSURU_TARGET

            popen = subprocess.Popen(
                cmds,
                stdin=stdin_pipe,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=envs,
            )
            stdout, stderr = popen.communicate(stdin)
            if popen.returncode != 0:
                raise CmdError(cmds, popen.returncode, stdout, stderr)
            return stdout, stderr
        return cmd


def get_token():
    with open(os.path.expanduser('~/.tsuru_token'), 'r') as f:
        return f.read()


def retry(func, *args, **kwargs):
    count = kwargs.pop('count', 10)
    sleep = kwargs.pop('sleep', 5)
    ignore = kwargs.pop('ignore', None)
    for i in xrange(count):
        try:
            return func(*args, **kwargs)
        except CmdError as value:
            if ignore and re.match(ignore, value.stderr, re.DOTALL):
                return True
            if i == count - 1:
                raise
            print 'retrying...'
            time.sleep(sleep)


shell = Cmd('')
tsuru = shell('tsuru')
git = shell('git')
