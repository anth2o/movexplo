install: # used by the web server
	pip install .

install-dev: # used to dev locally
	pip install -e ".[writer,tests]"

install-tests: # used by the CI
	pip install ".[writer,tests]"

tests:
	pytest --cov movexplo tests

.PHONY: tests
