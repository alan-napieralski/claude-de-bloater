.PHONY: release release-minor release-major validate lint

release:
	python3 scripts/release.py $(or $(VERSION),patch)

release-minor:
	python3 scripts/release.py minor

release-major:
	python3 scripts/release.py major

validate:
	claude plugin validate . --strict

lint:
	npx claudelint --no-cache
