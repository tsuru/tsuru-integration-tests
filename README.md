[![Build Status](https://api.travis-ci.org/andrewsmedina/tsuru-integration-tests.png)](https://travis-ci.org/andrewsmedina/tsuru-integration-tests/)

tsuru-integration-tests
=======================

It is a script to test a simple tsuru workflow:

* app create
* deploy
* check the app content
* remove app

Install
-------

    pip install -r requirements.txt

Running the script
------------------

    python integration.py

Running tests of the tests
--------------------------

    python test_integration.py
