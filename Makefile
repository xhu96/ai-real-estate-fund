.PHONY: install install-api test compile smoke readiness health audit api demo frontend docker docker-prod release-manifest release-zip release clean

install:
	python -m pip install -e .

install-api:
	python -m pip install -e ".[api]"

compile:
	python -m compileall -q src app/backend tests

test: compile
	python -m pip install -e ".[api,dev]" -q
	python -m pytest -q

smoke:
	python scripts/smoke_test.py

readiness:
	APP_ENV=ci python -m ai_real_estate_fund readiness --strict

health:
	python -m ai_real_estate_fund health

audit:
	python -m ai_real_estate_fund audit-verify --strict

diligence:
	python -m ai_real_estate_fund institutional examples/duplex_sunbelt.json

backtest:
	python -m ai_real_estate_fund.backtesting.cli --examples examples/properties.csv

api:
	python -m pip install -e ".[api]"
	uvicorn app.backend.main:create_app --factory --reload

demo:
	bash scripts/dev.sh

frontend:
	cd app/frontend && npm install && npm run dev

docker:
	docker compose up --build

docker-prod:
	APP_ENV=production docker compose -f compose.production.yml up --build

release-manifest:
	python scripts/release_manifest.py

release-zip:
	bash scripts/make_release_zip.sh

# Full local release build: gate, pip artifacts, manifest, and the curated turnkey zip.
# Then `git tag vX.Y.Z && git push origin vX.Y.Z` to publish via .github/workflows/release.yml.
release: test
	python -m build
	python scripts/release_manifest.py --out dist/release-manifest.json
	bash scripts/make_release_zip.sh
	@echo "dist/ now has: curated zip + wheel + sdist + release-manifest.json"
	@echo "Publish: git tag v$$(grep -m1 -E '^version' pyproject.toml | sed -E 's/.*\"([^\"]+)\".*/\\1/') && git push origin --tags"

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache dist build *.egg-info
