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


.PHONY: deps
deps:
	pip-compile \
		--output-file requirements.txt \
		--upgrade \
		--rebuild \
		requirements.in \
		requirements.test.in 
