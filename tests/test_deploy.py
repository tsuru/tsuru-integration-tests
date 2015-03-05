import re
import os
from os.path import join

from tests import BaseTestCase
from tests.utils import tsuru, git, shell


class CreationAndDeployTestCase(BaseTestCase):

    def setUp(self):
        self.reset_user()

    def test_create_app(self):
        out, _ = tsuru.app_create(self.appname, 'python', '-t', self.teamname)
        repo = re.findall(r'project is "(.*)"', out)
        self.assertTrue(len(repo) == 1)
        self.assertRegexpMatches(repo[0], r'.+?@.+?:' + self.appname + r'\.git')

    def test_app_deploy(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = join(base_dir, '..', 'app')
        tsuru.app_create(self.appname, 'python', '-t', self.teamname)
        tsuru.app_deploy('-a', self.appname, app_dir)
        self.assert_app_is_up()

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
exec /usr/bin/ssh -o StrictHostKeyChecking=no -i {} "$@"
'''.format(join(fix_dir, 'my.key')))
        shell.chmod('+x', git_cmd_path)

        tsuru.key_add(self.keyname, join(fix_dir, 'my.key.pub'))
        out, _ = tsuru.app_create(self.appname, 'python', '-t', self.teamname)
        repo = re.findall(r'project is "(.*)"', out)
        shell.rm('-rf', git_dir)

        git.init(app_dir)
        git_in_app = git('--git-dir', git_dir, '--work-tree', app_dir)
        git_in_app.add('-A', app_dir)
        git_in_app.commit('-m', 'first')
        _, err = git_in_app.push(repo[0], 'master', envs={'GIT_SSH': git_cmd_path})
        self.assertRegexpMatches(err, r'\nremote: OK\s*?\n')
        self.assert_app_is_up()
