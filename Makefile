version := `python -c 'import sponge; print sponge.__version__'`
package-name := sponge-${version}
debian-name := python-sponge_${version}
debian-tarball-name := ${debian-name}.orig.tar.gz

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
	@nosetests -sdv --with-coverage --cover-package=sponge tests/unit
	@echo "Done."

functional:
	@echo "Running functional tests ..."
	@nosetests -sdv --with-coverage --cover-package=sponge tests/functional
	@echo "Done."

build: test
	@echo "Building sponge"
	@python setup.py build
	@echo "Done."

tarball: test
	@make clean
	@echo "Preparing tarball ..."
	@cp -drf . ../${package-name}
	@rm -rf ../${package-name}/.git
	@echo "Creating tarball ..."
	@tar czf ${package-name}.tar.gz ../${package-name}
	@rm -rf ../${package-name}
	@echo "Tarball created at at "${package-name}.tar.gz

deb-tarball: test
	@make clean
	@echo "Preparing tarball ..."
	@cp -drf . ../${package-name}
	@rm -rf ../${package-name}/.git
	@rm -rf ../${package-name}/debian
	@rm -rf ../${package-name}/docs/_build
	@echo "Creating tarball ..."
	@tar czf ../${debian-tarball-name} ../${package-name}
	@cp -drf debian ../${package-name}/debian
	@echo "Tarball created at at ../"${debian-tarball-name}