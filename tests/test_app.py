import re
import os
import time
from os.path import join

from tests import BaseTestCase
from tests.utils import tsuru, retry


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
        cls.username = 'tester@globo.com'
        cls.password = '123456'
        cls.appname = 'myapp'
        cls.teamname = 'testteam'
        cls.keyname = 'mykey'

        try:
            tsuru.login(cls.username, stdin=cls.password)
            retry(tsuru.app_remove, '-a', cls.appname, '-y', count=1, ignore=r'.*not found.*')
            retry(tsuru.key_remove, cls.keyname, '-y', count=1, ignore=r'.*not found.*')
            retry(tsuru.team_remove, cls.teamname, stdin='y', count=10, ignore=r'.*not found.*')
            retry(tsuru.user_remove, stdin='y', count=1, ignore=r'.*not found.*')
        except Exception as e:
            print e
        tsuru.user_create(cls.username, stdin=cls.password + '\n' + cls.password)
        tsuru.login(cls.username, stdin=cls.password)
        tsuru.team_create(cls.teamname)
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
