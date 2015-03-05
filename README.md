tsuru-integration-tests
=======================

The goal of this test suite is to run integration tests against an existing
tsuru cloud. These integration tests will exclusively use `tsuru-client` and
`tsuru-admin` to run multiple operations on the cloud. Ideally all tsuru
commands will be tested using this suite.

Optionally we'll provide a way to bootstrap a new tsuru cloud and run tests
against it.

Running the script
------------------

    $ export TSURU_TARGET=tsuru.api.server:8080
    $ export TSURU_TOKEN=xxxxxxxxxxxxxx # optional
    $ make run

Exporting `TSURU_TOKEN` environment variable is optional. If it's set, it will
use it to authenticate in tsuru api server. If not set, the test script will
create a new user and team before running tests.