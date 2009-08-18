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
	@nosetests -sd --with-coverage --cover-package=sponge tests/unit tests/functional
	@echo "Done."

unit:
	@echo "Running unit tests ..."
	@nosetests -sd --with-coverage --cover-package=sponge tests/unit
	@echo "Done."

functional:
	@echo "Running functional tests ..."
	@nosetests -sd --with-coverage --cover-package=sponge tests/functional
	@echo "Done."

build: test
	@echo "Building sponge"
	@python setup.py build
	@echo "Done."

tarball: test
	@make clean
	@echo "Preparing tarball ..."
	@cp -drf . ../sponge-`python -c 'import sponge; print sponge.__version__'`
	@rm -rf ../sponge-`python -c 'import sponge; print sponge.__version__'`/.git
	@echo "Creating tarball ..."	
	@tar czf sponge-`python -c 'import sponge; print sponge.__version__'`.tar.gz ../sponge-`python -c 'import sponge; print sponge.__version__'`
	@rm -rf ../sponge-`python -c 'import sponge; print sponge.__version__'`
	@echo "Tarball created at at sponge-`python -c 'import sponge; print sponge.__version__'`.tar.gz"