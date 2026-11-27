# Set runner to 'poetry run', 'pipenv run', or 'python3'

# Targets
.PHONY: test build

test:
	poetry run pytest

build:
	poetry build
pre-commit:
	poetry run pre-commit run --all-files
