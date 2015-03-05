import unittest
import re
import os
import base64

from tests.utils import tsuru, retry, shell, CmdError


def random_name(prefix=''):
    return "{}{}".format(prefix, base64.b16encode(os.urandom(12))).lower()


class BaseTestCase(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'appname', None):
            retry(tsuru.app_remove, '-a', cls.appname, '-y', count=1, ignore=r'.*not found.*')
        if getattr(cls, 'teamname', None):
            retry(tsuru.team_remove, cls.teamname, stdin='y', count=10, ignore=r'.*not found.*')
        if getattr(cls, 'username', None):
            retry(tsuru.user_remove, stdin='y', count=1, ignore=r'.*not found.*')

    @classmethod
    def reset_user(cls):
        if not getattr(cls, 'username', None):
            cls.username = '{}@somewhere.com'.format(random_name())
            cls.password = random_name()
            cls.appname = random_name('integration-test-app-')
            cls.teamname = random_name('integration-test-team-')
            cls.keyname = random_name('integration-test-key-')
        if os.environ.get('TSURU_TOKEN'):
            retry(tsuru.app_remove, '-a', cls.appname, '-y', count=10, ignore=r'.*not found.*')
            retry(tsuru.team_remove, cls.teamname, stdin='y', count=10, ignore=r'.*not found.*')
            tsuru.team_create(cls.teamname)
            return
        try:
            tsuru.login(cls.username, stdin=cls.password)
        except:
            pass
        else:
            retry(tsuru.app_remove, '-a', cls.appname, '-y', count=10, ignore=r'.*not found.*')
            retry(tsuru.key_remove, cls.keyname, '-y', count=1, ignore=r'.*not found.*')
            retry(tsuru.team_remove, cls.teamname, stdin='y', count=10, ignore=r'.*not found.*')
            retry(tsuru.user_remove, stdin='y', count=1, ignore=r'.*not found.*')
        tsuru.user_create(cls.username, stdin=cls.password + '\n' + cls.password)
        tsuru.login(cls.username, stdin=cls.password)
        tsuru.team_create(cls.teamname)

    def assert_app_is_up(self, appname=None, msg='Hello World!'):
        if appname is None:
            appname = self.appname
        out, _ = tsuru.app_info('-a', appname)
        addr = re.search(r'Address: (.*?)\n', out).group(1)
        out, _ = retry(shell.curl, '-fsSL', addr)
        self.assertEqual(out, msg)

    def assert_app_is_down(self, appname=None):
        if appname is None:
            appname = self.appname
        out, _ = tsuru.app_info('-a', appname)
        addr = re.search(r'Address: (.*?)\n', out).group(1)
        try:
            out, err = shell.curl('-fsSL', addr)
            self.fail('App should be down, curl result: {} - {}'.format(out, err))
        except CmdError:
            pass
