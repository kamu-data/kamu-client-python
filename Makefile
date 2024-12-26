###############################################################################
# Dev
###############################################################################

.PHONY: fmt
fmt:
	black .
	isort .


.PHONY: lint
lint:
	pylint kamu tests
	flake8 kamu tests


.PHONY: test
test:
	pytest -s


###############################################################################
# Dependencies
###############################################################################

.PHONY: deps-compile
deps-compile:
	pip-compile \
		--extra dev --extra spark \
		--upgrade \
		--rebuild \
		pyproject.toml


.PHONY: deps-sync
deps-sync:
	pip-sync requirements.txt


.PHONY: deps
deps: deps-compile deps-sync


###############################################################################
# Publishing
###############################################################################

.PHONY: build
build:
	rm -rf dist
	python -m build
	twine check dist/*


.PHONY: publish
publish: build
	twine upload dist/*
