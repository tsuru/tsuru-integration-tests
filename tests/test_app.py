import re
import os
import time
from os.path import join

from tests import BaseTestCase
from tests.utils import tsuru


class AppTestCase(BaseTestCase):

    def assert_units_len(self, length, retry=1):
        for i in xrange(retry):
            out, _ = tsuru.app_info('-a', self.appname)
            units = re.search(r'Units: (.*?)\n', out).group(1)
            if units == str(length):
                break
            if i == retry - 1:
                self.fail('Invalid units count, excepted {}, got {}'.format(length, units))
            print 'retrying...'
            time.sleep(5)

    @classmethod
    def setUpClass(cls):
        cls.reset_user()
        tsuru.app_create(cls.appname, 'python', '-t', cls.teamname)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = join(base_dir, '..', 'app')
        tsuru.app_deploy('-a', cls.appname, app_dir)

    def test_unit_add_remove(self):
        tsuru.unit_add('-a', self.appname, '2')
        self.assert_units_len(3)
        self.assert_app_is_up()
        tsuru.unit_remove('-a', self.appname, '2')
        self.assert_units_len(1, retry=10)
        self.assert_app_is_up()

    def test_stop_start(self):
        self.assert_app_is_up()
        tsuru.app_stop('-a', self.appname)
        self.assert_app_is_down()
        tsuru.app_start('-a', self.appname)
        self.assert_app_is_up()

    def test_restart(self):
        out, _ = tsuru.app_info('-a', self.appname)
        units = re.findall(r'\n\|\s([a-f0-9]+)\s\|', out)
        tsuru.app_restart('-a', self.appname)
        out, _ = tsuru.app_info('-a', self.appname)
        units_after = re.findall(r'\n\|\s([a-f0-9]+)\s\|', out)
        self.assertNotEqual(sorted(units), sorted(units_after))

    def test_run(self):
        tsuru.unit_add('-a', self.appname, '2')
        out, _ = tsuru.app_run('-a', self.appname, 'env')
        hosts = re.findall(r'TSURU_HOST=(.+)\n', out)
        self.assertEqual(len(hosts), 3)
        out, _ = tsuru.app_run('-a', self.appname, 'env', '-o')
        hosts = re.findall(r'TSURU_HOST=(.+)\n', out)
        self.assertEqual(len(hosts), 1)
        tsuru.unit_remove('-a', self.appname, '2')
        self.assert_units_len(1, retry=10)

    def test_log(self):
        out, _ = tsuru.app_log('--lines', '7', '-a', self.appname)
        parts = out.split('\n')
        self.assertEqual(len(parts), 8)
        self.assertEqual(parts[7], "")
        self.assert_app_is_up()
        out, _ = tsuru.app_log('--lines', '10', '-a', self.appname)
        self.assertRegexpMatches(out, r'output to log')
