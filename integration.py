TSURU_HOST = "http://localhost:8888"


def create_app():
    url = "{0}/apps".format(TSURU_HOST)
    data = {"name": "integration", "platform": "static"}
    response = requests.post(url, json.dumps(data))


def remove_app():
    url = "{0}/apps/integration".format(TSURU_HOST)
    response = requests.delete(url)


def deploy():
    remote = "git@localhost:integration.git"
    subprocess.call(["git", "push", remote, "master"])


def verify():
    url = "http://app.localhost:8888"
    response = requests.get(url)


def main():
    create_app()
    deploy()
    verify()
    remove_app()
