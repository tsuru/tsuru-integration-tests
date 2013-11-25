import requests
import unittest
import json
from mock import patch
from collections import namedtuple
from integration import (create_app, remove_app, deploy, create_user,
                         login, remove_user, auth_request)


class AppIntegrationTestCase(unittest.TestCase):

    @patch("requests.post")
    def test_create_app_should_post_and_repass_message(self, post):
        post.return_value = namedtuple("Response", ["text"])(text="app created")
        r = create_app()
        self.assertEqual("app created", r)

    @patch("requests.post")
    def test_create_app_should_call_correct_url(self, post):
        create_app()
        url = post.call_args[0][0]
        self.assertEqual("http://localhost:8888/apps", url)

    @patch("requests.post")
    def test_create_app_should_pass_correct_json(self, post):
        create_app()
        got = json.loads(post.call_args[0][1])
        expected = {"name": "integration", "platform": "static"}
        self.assertEqual(expected, got)

    @patch("requests.delete")
    def test_remove_app_should_delete_and_repass_message(self, delete):
        delete.return_value = namedtuple("Response", ["text"])(text="app removed")
        r = remove_app()
        self.assertEqual("app removed", r)

    @patch("requests.delete")
    def test_remove_app_should_call_right_url(self, delete):
        remove_app()
        url = delete.call_args[0][0]
        self.assertEqual("http://localhost:8888/apps/integration", url)

    @patch("subprocess.call")
    def test_deploy_should_call_git_push_with_right_remote(self, call):
        deploy()
        remote = "git@localhost:integration.git"
        self.assertListEqual(["git", "push", remote, "master"], call.call_args[0][0])


class UserIntegrationTestCase(unittest.TestCase):

    @patch("requests.post")
    def test_create_user_should_post_to_right_url(self, post):
        create_user()
        url = post.call_args[0][0]
        self.assertEqual("http://localhost:8888/users", url)

    @patch("requests.post")
    def test_create_user_should_pass_correct_json(self, post):
        create_user()
        got = json.loads(post.call_args[0][1])
        expected = {"email": "tester@globo.com", "password": "123456"}
        self.assertEqual(expected, got)

    @patch("requests.delete")
    def test_remove_user_should_delete_to_right_url(self, delete):
        remove_user()
        url = delete.call_args[0][0]
        self.assertEqual("http://localhost:8888/users", url)

    @patch("requests.post")
    def test_login_should_post_to_right_url(self, post):
        login()
        url = post.call_args[0][0]
        expected = "http://localhost:8888/users/tester@globo.com/tokens"
        self.assertEqual(expected, url)

    @patch("requests.post")
    def test_login_should_post_correct_json(self, post):
        login()
        got = json.loads(post.call_args[0][1])
        expected = {"password": "123456"}
        self.assertEqual(expected, got)

    @patch("requests.post")
    def test_login_should_return_token(self, post):
        post.return_value = namedtuple("Response", ["text", "status_code"])(text='{"token":"abc123"}', status_code=200)
        self.assertEqual("abc123", login())

class FakePost(object):
    def __call__(self, url, headers, **kwargs):
        self.url = url
        self.headers = headers


class AuthenticatedRequestTestCase(unittest.TestCase):

    def test_should_add_Authentication_header_to_post_request(self):
        post = FakePost()
        auth_request(post, "test.com")
        auth = post.headers["Authorization"]
        self.assertEquals(auth, "token123")


if __name__ == "__main__":
    unittest.main()
