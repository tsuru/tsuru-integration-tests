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


class Cmd(object):

    def __init__(self, cmd):
        self.cmd = cmd

    def __getattr__(self, name):
        def cmd(*args, **kwargs):
            cmds = [self.cmd, name.replace("_", "-")]
            cmds.extend(args)
            print("\n\nExecuting {}\n******".format(" ".join(cmds)))
            return subprocess.call(cmds)
        return cmd


tsuru = Cmd("tsuru")
git = Cmd("git")


def create_app(token):
    return tsuru.app_create(APP_NAME, "static")


def remove_app(token):
    cmd = subprocess.Popen(["tsuru", "app-remove", "-a", APP_NAME], stdin=subprocess.PIPE)
    return cmd.communicate("y")


def _clone_repository(repository, dst):
    return git.clone(repository, dst)


def deploy(remote):
    app_dir = "/tmp/test_app"
    exits = []
    exits.append(_clone_repository(TEST_REPOSITORY, app_dir))
    exits.append(tsuru.app_deploy("-a", APP_NAME, app_dir))
    exits.append(subprocess.call(["rm", "-rf", app_dir]))
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
    cmd = subprocess.Popen(["tsuru", "user-create", USER], stdin=subprocess.PIPE)
    return cmd.communicate(PASSWORD + "\n" + PASSWORD)


def remove_user(token):
    cmd = subprocess.Popen(["tsuru", "user-remove"], stdin=subprocess.PIPE)
    return cmd.communicate("y")


def add_key(token):
    key_path = os.path.expanduser("~/.ssh/id_rsa.pub")
    key = "{}-key".format(USER)
    return tsuru.key_add(key, key_path)


def remove_key(token):
    cmd = subprocess.Popen(["tsuru", "key-remove", "{}-key".format(USER)], stdin=subprocess.PIPE)
    return cmd.communicate("y")


def add_team(token):
    return tsuru.team_create("testteam")


def remove_team(token):
    retry = True
    while retry:
        cmd = subprocess.Popen(
            ["tsuru", "team-remove", "testteam"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = cmd.communicate("y")[1]

        if not "it have access to apps" in output:
            return output


def login():
    cmd = subprocess.Popen(["tsuru", "login", USER], stdin=subprocess.PIPE)
    cmd.communicate(PASSWORD)
    token = subprocess.check_output(["tsuru", "token-show"])
    return token.split(" ")[-1]


def main():
    token = os.environ.get("TSURU_TOKEN")

    exits = []

    if not token:
        exits.append(create_user())
        token = login()

    exits.append(add_team(token))
    exits.append(add_key(token))
    remote = create_app(token)
    exits.append(deploy(remote))

    remove_app(token)
    remove_team(token)
    remove_key(token)

    token = os.environ.get("TSURU_TOKEN")

    if not token:
        remove_user(token)

    if 1 in exits:
        "Finished with failure!"
        exit(1)
    print("Success!")

if __name__ == "__main__":
    main()
