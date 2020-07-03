install:
	pip install .

install-tests:
	pip install -r requirements-tests.txt

tests:
	pytest --cov movexplo tests

.PHONY: tests
