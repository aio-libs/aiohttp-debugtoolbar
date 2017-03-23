# Some simple testing tasks (sorry, UNIX only).

flake:
	flake8 aiohttp_debugtoolbar tests

	@if python -c "import sys; sys.exit(sys.version_info < (3,5))"; then \
	    flake8 examples demo && \
            python setup.py check -rms; \
	fi

test: flake
	pytest -s ./tests/

vtest:
	pytest -s -v ./tests/

cov cover coverage: flake
	pytest -s --cov-report term --cov-report html --cov aiohttp_debugtoolbar
	@echo "open file://`pwd`/htmlcov/index.html"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover
	rm -rf htmlcov

doc:
	make -C docs html
	@echo "open file://`pwd`/docs/_build/html/index.html"

.PHONY: all build venv flake test vtest testloop cov clean doc
