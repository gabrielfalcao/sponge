all: clean test

clean:
	@echo "Cleaning up all *.pyc files ..."
	@find . -name '*.pyc' -delete
	@echo "Cleaning up coverage metadata ..."
	@rm -f .coverage
	@echo "Cleaning up build files ..."
	@rm -rf build
test:
	@echo "Running all tests ..."
	@nosetests -s --with-coverage --cover-package=sponge tests/unit tests/functional
	@echo "Done."

unit:
	@echo "Running unit tests ..."
	@nosetests -s --with-coverage --cover-package=sponge tests/unit
	@echo "Done."

functional:
	@echo "Running functional tests ..."
	@nosetests -s --with-coverage --cover-package=sponge tests/functional
	@echo "Done."

build: test
	@echo "Building sponge"
	@python setup.py build
	@echo "Done."