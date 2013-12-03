import json
import os
import requests
import subprocess


TSURU_HOST = os.environ.get("TSURU_HOST", "localhost")
TSURU_PORT = os.environ.get("TSURU_PORT", "8080")
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
        print("Caugth error while creating app: {0} - {1}".format(r.status_code, r.text))
        return 1
    print("app created")
    return r.json()["repository_url"]


def remove_app(token):
    url = "{0}/apps/{1}".format(TSURU_URL, APP_NAME)
    r = auth_request(requests.delete, url, token)
    if r.status_code != 200:
        return 1
    print("remove app: {0}".format(r.text))
    return 0


def _clone_repository(repository, dst):
    return subprocess.call(["git", "clone", repository, dst])


def _push_repository(remote, git_dir):
    return subprocess.call(["git", "--git-dir={0}".format(git_dir), "push", remote, "master"])


def deploy(remote):
    exits = []
    exits.append(_clone_repository(TEST_REPOSITORY, "/tmp/test_app"))
    exits.append(_push_repository(remote, "/tmp/test_app/.git"))
    exits.append(subprocess.call(["sudo", "rm", "-r", "/tmp/test_app"]))
    if 1 in exits:
        print("deploy finished with error")
        return 1
    return 0

def verify():
    url = "http://{0}.{1}".format(APP_NAME, TSURU_HOST)
    response = requests.get(url)
    if response.status_code == 200:
        print("Application responding successfuly")
    else:
        print("Application not responding: {0} - {1}".format(response.status_code, response.text))


def create_user():
    url = "{0}/users".format(TSURU_URL)
    data = {"email": USER, "password": PASSWORD}
    r = requests.post(url, json.dumps(data)).text
    print("create user output: {0}".format(r))


def remove_user(token):
    url = "{0}/users".format(TSURU_URL)
    print("remove user output: {0}".format(auth_request(requests.delete, url, token)))


def add_key(token):
    url = "{0}/users/keys".format(TSURU_URL)
    try:
        f = open(os.path.expanduser("~/.ssh/id_rsa.pub"))
        key = f.read()
        f.close
        code = auth_request(requests.post, url, token, data=json.dumps({"key": key})).status_code
        print("key added")
        if code != 200:
            return 1
        return 0
    except IOError:
        print("id_rsa.pub not found, create and run the tests again")
        return 1


def remove_key(token):
    url = "{0}/users/keys".format(TSURU_URL)
    f = open(os.path.expanduser("~/.ssh/id_rsa.pub"))
    key = f.read()
    f.close
    r = auth_request(requests.delete, url, token, data=json.dumps({"key": key}))
    if r.status_code != 200:
        return 1
    print("remove key: {0}".format(r.text))
    return 0


def add_team(token):
    url = "{0}/teams".format(TSURU_URL)
    r = auth_request(requests.post, url, token, data=json.dumps({"name": "testteam"}))
    if r.status_code != 200:
        return 1
    print("add team: {0}".format(r.text))
    return 0


def remove_team(token):
    url = "{0}/teams/testteam".format(TSURU_URL)
    r = auth_request(requests.delete, url, token)
    if r.status_code != 200:
        print ("error removing team: {0} - {1}".format(r.status_code, r.text))
        return 1
    print("success removing team: {0} - {1}".format(r.status_code, r.text))
    return 0


def login():
    url = "{0}/users/{1}/tokens".format(TSURU_URL, USER)
    data = {"password": PASSWORD}
    r = requests.post(url, json.dumps(data))
    if r.status_code > 201:
        return 1
    token = json.loads(r.text)["token"]
    return token

def auth_request(method, url, token, **kwargs):
    return method(url, headers={"Authorization": "bearer {0}".format(token)}, **kwargs)


def main():
    exits = []
    exits.append(create_user())
    token = login()
    exits.append(add_team(token))
    exits.append(add_key(token))
    remote = create_app(token)
    exits.append(deploy(remote))

    remove_app(token)
    remove_team(token)
    remove_key(token)
    remove_user(token)
    if 1 in exits:
        "Finished with failure!"
        exit(1)
    print("Success!")

if __name__ == "__main__":
    main()
