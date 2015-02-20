clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r requirements.txt

run: clean deps
	@python integration.py
