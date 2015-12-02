deps:
	@pip install -r requirements_test.txt

test: deps
	@python -m unittest discover
