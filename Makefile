.PHONY: test run test-deps clean

run: test

clean:
	@find . -name "*.pyc" -delete

test-deps:
	@pip install -r test-requirements.txt

test: test-deps
	@python -m unittest discover
	@flake8 --max-line-length 110 .
