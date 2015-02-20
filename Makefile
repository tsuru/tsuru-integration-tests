clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r requirements.txt

test-deps:
	@pip install -r test_requirements.txt

test: clean test-deps
	@python test_integration.py

run: clean deps
	@python integration.py
