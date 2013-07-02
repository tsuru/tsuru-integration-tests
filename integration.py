import subprocess
import requests
import os


TSURU_HOST = os.environs.get("TSURU_HOST", "localhost")
TSURU_PORT = os.environs.get("TSURU_PORT", "8888")
TSURU_URL = "http://{0}:{1}".format(TSURU_HOST, TSURU_PORT)
APP_NAME = "integration"


def create_app():
    url = "{0}/apps".format(TSURU_HOST)
    data = {"name": APP_NAME, "platform": "static"}
    response = requests.post(url, json.dumps(data))


def remove_app():
    url = "{0}/apps/{1}".format(TSURU_URL, APP_NAME)
    response = requests.delete(url)


def deploy():
    remote = "git@{0}:{1}.git".format(TSURU_HOST, APP_NAME)
    subprocess.call(["git", "push", remote, "master"])


def verify():
    url = "http://{0}.{1}".format(APP_NAME, TSURU_HOST)
    response = requests.get(url)


def main():
    create_app()
    deploy()
    verify()
    remove_app()
