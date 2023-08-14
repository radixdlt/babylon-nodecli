.PHONY: install
install:
	$(shell chmod +x add-version.sh)
	$(shell ./add-version.sh)
.PHONY: output
output-ubuntu-focal: install
	DOCKER_BUILDKIT=1 docker build --platform linux/amd64 --output type=local,dest=out/ubuntu/focal --progress plain -f Dockerfile.ubuntufocal  .
.PHONY: output
output-ubuntu-jammy: install
	DOCKER_BUILDKIT=1 docker build --platform linux/amd64 --output type=local,dest=out/ubuntu/jammy --progress plain -f Dockerfile.ubuntujammy  .

.PHONEY: cmds-reference
cmds-reference: local
	./generate-cmds-help.sh

.PHONEY: test
test: test
	pipenv install
	pipenv run pip install pytest pytest-cov
	pipenv run pytest tests/ --doctest-modules --junitxml=junit/test-results.xml --cov=. --cov-report=xml --cov-report=html
