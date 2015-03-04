#!/bin/bash -el

function add_platform() {
	platform=$1
	echo "adding platform $platform..."
	output_file="/tmp/platform-update-${platform}"
	set +e
	tsuru-admin platform-add $platform -d https://raw.githubusercontent.com/tsuru/basebuilder/master/${platform}/Dockerfile | tee $output_file
	result=$?
	set -e
	if [[ $result != 0 ]]; then
		if [[ $(tail -n1 $output_file) != "Error: Duplicate platform" ]]; then
			echo "error adding platform $platform"
			exit $result
		fi
	fi
}

function clean_tsuru_now() {
	rm /tmp/tsuru-now.bash
	tsuru app-remove -ya tsuru-dashboard 2>/dev/null
	mongo tsurudb --eval 'db.platforms.remove({_id: "python"})'
	docker rmi -f tsuru/python 2>/dev/null
}

export DEBIAN_FRONTEND=noninteractive
sudo -E apt-get update
sudo -E apt-get install curl -qqy
sudo -E apt-get update
sudo -E apt-get install linux-image-extra-$(uname -r) -qqy
curl -sL https://raw.githubusercontent.com/tsuru/now/master/run.bash -o /tmp/tsuru-now.bash
bash /tmp/tsuru-now.bash "$@" --without-dashboard

export GOPATH=$HOME/go
export PATH=$GOPATH/bin:$PATH
export DOCKER_HOST="tcp://127.0.0.1:4243"

set +e
clean_tsuru_now
set -e

clone_basebuilder /tmp/basebuilder
echo -e "Host localhost\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config

add_platform $platform

rm -rf /tmp/basebuilder
rm -rf /tmp/app-*
