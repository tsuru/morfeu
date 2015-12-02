clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r requirements_test.txt

all_deps:
	@pip install -r requirements_test.txt
	@pip install -r requirements.txt

test: clean deps
	@coverage run -m unittest discover
	@coverage report --omit="*/tests/*" --include="./*" -m
	@flake8 --max-line-length 110 .
