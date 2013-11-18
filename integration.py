import json
import os
import requests
import subprocess


GANDALF_HOST = os.environ.get("TSURU_HOST", "localhost")
TSURU_HOST = os.environ.get("TSURU_HOST", "localhost")
TSURU_PORT = os.environ.get("TSURU_PORT", "8888")
TSURU_URL = "http://{0}:{1}".format(TSURU_HOST, TSURU_PORT)
APP_NAME = "integration"


def create_app():
    url = "{0}/apps".format(TSURU_URL)
    data = {"name": APP_NAME, "platform": "static"}
    return requests.post(url, json.dumps(data)).text


def remove_app():
    url = "{0}/apps/{1}".format(TSURU_URL, APP_NAME)
    return requests.delete(url).text


def deploy():
    remote = "git@{0}:{1}.git".format(TSURU_HOST, APP_NAME)
    subprocess.call(["git", "push", remote, "master"])


def verify():
    url = "http://{0}:{1}.git".format(GANDALF_HOST, APP_NAME)
    response = requests.get(url)


def main():
    create_app()
    deploy()
    verify()
    remove_app()
