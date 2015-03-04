import unittest
import re
import os
import time
import shutil
from os.path import join

from tests.utils import tsuru, git, CmdError, shell


class ok_not_found(object):
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        if isinstance(value, CmdError):
            if re.match(r'.*not found.*', value.stderr, re.DOTALL):
                return True
        return False


class IntegrationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.username = 'tester@globo.com'
        cls.password = '123456'
        cls.appname = 'myapp'
        cls.teamname = 'testteam'
        cls.keyname = 'mykey'

    def setUp(self):
        try:
            tsuru.login(self.username, stdin=self.password)
            with ok_not_found():
                tsuru.app_remove('-a', self.appname, '-y')
            with ok_not_found():
                tsuru.key_remove(self.keyname, '-y')
            for i in xrange(10):
                try:
                    with ok_not_found():
                        tsuru.team_remove(self.teamname, stdin='y')
                    break
                except CmdError as e:
                    print 'retrying...'
                    time.sleep(5)
            with ok_not_found():
                tsuru.user_remove(stdin='y')
        except Exception as e:
            print e
        tsuru.user_create(self.username, stdin=self.password + '\n' + self.password)
        tsuru.login(self.username, stdin=self.password)
        tsuru.team_create(self.teamname)

    def test_create_app(self):
        out, _ = tsuru.app_create(self.appname, 'python', '-t', self.teamname)
        repo = re.findall(r'project is "(.*)"', out)
        self.assertTrue(len(repo) == 1)
        self.assertRegexpMatches(repo[0], r'.+?@.+?:' + self.appname + r'\.git')

    def test_app_git_deploy(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = join(base_dir, '..', 'app')
        git_dir = join(app_dir, '.git')
        fix_dir = join(base_dir, 'gen_fixtures')
        git_cmd_path = join(fix_dir, 'gitcmd')

        shell.mkdir('-p', fix_dir)
        shell.ssh_keygen('-t', 'rsa', '-N', '', '-f', join(fix_dir, 'my.key'), stdin='y')
        with open(git_cmd_path, 'w') as f:
            f.write('''#!/bin/bash
exec /usr/bin/ssh -i {} "$@"
'''.format(join(fix_dir, 'my.key')))
        shell.chmod('+x', git_cmd_path)

        tsuru.key_add(self.keyname, join(fix_dir, 'my.key.pub'))
        out, _ = tsuru.app_create(self.appname, 'python', '-t', self.teamname)
        repo = re.findall(r'project is "(.*)"', out)
        try:
            shutil.rmtree(git_dir)
        except:
            pass
        git.init(app_dir)
        git_in_app = git('--git-dir', git_dir, '--work-tree', app_dir)
        git_in_app.add('-A', app_dir)
        git_in_app.commit('-m', 'first')
        _, err = git_in_app.push(repo[0], 'master', envs={'GIT_SSH': git_cmd_path})
        self.assertRegexpMatches(err, r'\nremote: OK\s*?\n')
        out, _ = tsuru.app_info('-a', self.appname)
        addr = re.search(r'Address: (.*?)\n', out).group(1)
        out, _ = shell.curl('-fsSL', addr)
        self.assertEqual(out, "Hello World!")
