.PHONY: test docs

## Run the Python unit test suite.
test:
	PYTHONPATH=$(CURDIR) PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest

## Build the static TypeScript bundle for the docs page.
docs:
	npm run build
