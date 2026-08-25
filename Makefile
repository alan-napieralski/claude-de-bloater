.PHONY: validate lint

validate:
	claude plugin validate . --strict

lint:
	npx claudelint --no-cache
