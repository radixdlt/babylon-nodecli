.PHONY: install
install: prepare
	$(shell chmod +x add-version.sh)
	$(shell ./add-version.sh)
.PHONY: output
output-ubuntu-focal: install
	DOCKER_BUILDKIT=1 docker build --platform linux/amd64 --output type=local,dest=out/ubuntu/focal --progress plain -f Dockerfile.ubuntufocal  .
.PHONY: output
output-ubuntu-jammy: install
	DOCKER_BUILDKIT=1 docker build --platform linux/amd64 --output type=local,dest=out/ubuntu/jammy --progress plain -f Dockerfile.ubuntujammy  .

.PHONEY: prepare
prepare:
	git config core.hooksPath .githooks

.PHONEY: cmds-reference
cmds-reference: prepare
	./generate-cmds-help.sh

.PHONEY: test
test: prepare
	pipenv install
	pipenv run pip install pytest pytest-cov
	pipenv run pytest tests/ --doctest-modules --junitxml=junit/test-results.xml --cov=. --cov-report=xml --cov-report=html
