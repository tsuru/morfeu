deps:
	@pip install -r requirements_test.txt

test: deps
	@coverage run -m unittest discover
	@coverage report --omit="*/tests/*" --include="./*" -m
