import json
import os
import requests
import subprocess


TSURU_HOST = os.environ.get("TSURU_HOST", "localhost")
TSURU_PORT = os.environ.get("TSURU_PORT", "8888")
TSURU_URL = "http://{0}:{1}".format(TSURU_HOST, TSURU_PORT)
APP_NAME = "integration"
USER = "tester@globo.com"
PASSWORD = "123456"
TEST_REPOSITORY = "git://github.com/flaviamissi/tsuru-app-sample.git"


def create_app(token):
    url = "{0}/apps".format(TSURU_URL)
    data = {"name": APP_NAME, "platform": "static"}
    r = auth_request(requests.post, url, token, data=json.dumps(data))
    if r.status_code != 200:
        return ""
    return r.json()["repository_url"]


def remove_app(token):
    url = "{0}/apps/{1}".format(TSURU_URL, APP_NAME)
    return auth_request(requests.delete, url, token).text


def _clone_repository(repository, dst):
    subprocess.call(["git", "clone", repository, dst])


def _push_repository(remote, git_dir):
    subprocess.call(["git", "--git-dir={0}".format(git_dir), "push", remote, "master"])


def deploy(remote):
    _clone_repository(TEST_REPOSITORY, "/tmp/test_app")
    _push_repository(remote, "/tmp/test_app/.git")


def create_user():
    url = "{0}/users".format(TSURU_URL)
    data = {"email": USER, "password": PASSWORD}
    requests.post(url, json.dumps(data))


def remove_user(token):
    url = "{0}/users".format(TSURU_URL)
    auth_request(requests.delete, url, token)


def add_key(token):
    url = "{0}/users/keys".format(TSURU_URL)
    f = open(os.path.expanduser("~/.ssh/id_rsa.pub"))
    key = f.read()
    f.close
    auth_request(requests.post, url, token, data=json.dumps({"key": key}))


def remove_key(token):
    url = "{0}/users/keys".format(TSURU_URL)
    f = open(os.path.expanduser("~/.ssh/id_rsa.pub"))
    key = f.read()
    f.close
    auth_request(requests.delete, url, token, data=json.dumps({"key": key}))


def add_team(token):
    url = "{0}/teams".format(TSURU_URL)
    auth_request(requests.post, url, token, data=json.dumps({"name": "testteam"}))


def remove_team(token):
    url = "{0}/teams/testteam".format(TSURU_URL)
    #requests.delete(url)
    auth_request(requests.delete, url, token)


def login():
    url = "{0}/users/{1}/tokens".format(TSURU_URL, USER)
    data = {"password": PASSWORD}
    r = requests.post(url, json.dumps(data))
    if r.status_code > 201:
        return ""
    token = json.loads(r.text)["token"]
    return token

def auth_request(method, url, token, **kwargs):
    return method(url, headers={"Authorization": token}, **kwargs)


def main():
    create_user()
    token = login()
    create_app(token)
    deploy()
    remove_app()
