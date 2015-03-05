import unittest
import re

from tests.utils import tsuru, retry, shell, CmdError


class BaseTestCase(unittest.TestCase):

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
