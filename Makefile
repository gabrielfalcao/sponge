all: clean test

clean:
	@find . -name '*.pyc' -delete

test:
	@echo "Running all tests ..."
	@nosetests -s --with-coverage --cover-package=sponge tests/{functional,unit}
	@echo "Done."

unit:
	@echo "Running unit tests ..."
	@nosetests -s --with-coverage --cover-package=sponge tests/unit
	@echo "Done."

functional:
	@echo "Running functional tests ..."
	@nosetests -s --with-coverage --cover-package=sponge tests/functional
	@echo "Done."
