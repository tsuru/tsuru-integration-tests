clean:
	@find . -name "*.pyc" -delete

test-deps:
	@pip install -r test-requirements.txt

deps:
	@pip install -r requirements.txt

test: clean test-deps
	@flake8 --max-line-length 110 .

run: clean deps
	@python integration.py
