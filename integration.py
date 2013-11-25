import json
import os
import requests
import subprocess


GANDALF_HOST = os.environ.get("GANDALF_HOST", "localhost")
TSURU_HOST = os.environ.get("TSURU_HOST", "localhost")
TSURU_PORT = os.environ.get("TSURU_PORT", "8888")
TSURU_URL = "http://{0}:{1}".format(TSURU_HOST, TSURU_PORT)
APP_NAME = "integration"
USER = "tester@globo.com"
PASSWORD = "123456"


def create_app(token):
    url = "{0}/apps".format(TSURU_URL)
    data = {"name": APP_NAME, "platform": "static"}
    return auth_request(requests.post, url, token, data=json.dumps(data)).text


def remove_app(token):
    url = "{0}/apps/{1}".format(TSURU_URL, APP_NAME)
    return auth_request(requests.delete, url, token).text


def deploy():
    # need an app to deploy
    remote = "git@{0}:{1}.git".format(GANDALF_HOST, APP_NAME) # use returned remote
    subprocess.call(["git", "push", remote, "master"])


def create_user():
    url = "{0}/users".format(TSURU_URL)
    data = {"email": USER, "password": PASSWORD}
    requests.post(url, json.dumps(data))


def remove_user():
    url = "{0}/users".format(TSURU_URL)
    requests.delete(url)


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
