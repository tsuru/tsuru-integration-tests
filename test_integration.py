import unittest
from mock import patch
from collections import namedtuple
from integration import create_app


class IntegrationTestCase(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
