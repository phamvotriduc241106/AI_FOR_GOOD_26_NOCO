.PHONY: setup run demo test lint fmt eval feature docker lanes web web-test

setup:  ## create venv and install everything
	python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]" && cp -n .env.example .env || true

run:    ## start the demo app with the provider from .env
	streamlit run app/NOCO_Scout.py

demo:   ## offline rehearsal: fake provider, no key, no network
	LLM_PROVIDER=fake streamlit run app/NOCO_Scout.py

test:
	pytest

lint:
	ruff check . && ruff format --check .

fmt:
	ruff check . --fix && ruff format .

eval:   ## score every labeled case file; writes evals/results/<name>.md
	@for f in evals/cases/*.jsonl; do \
	  echo "== $$f"; \
	  python -m hackkit.evals "$$f" --out "evals/results/$$(basename $$f .jsonl).md" || exit 1; \
	done

feature: ## make feature NAME=intake_triage TITLE="Intake triage"
	python -m hackkit.scaffold $(NAME) "$(TITLE)"

docker:
	docker build -t hackkit . && docker run --rm -p 8501:8501 --env-file .env hackkit

lanes:  ## rebuild the workflow block of docs/DAY_OF.md; optional: make lanes SET="T1=merged T2=doing"
	python scripts/lanes.py $(if $(SET),--set $(SET))

web:    ## NOCO Scout web edition (HTML/CSS/JS): open http://localhost:8600/web/
	python -m http.server 8600 --bind 127.0.0.1

web-test: ## JS port must match the Python implementation exactly (needs Node.js)
	python web/tools/export_parity.py /tmp/noco_parity.json && PARITY_JSON=/tmp/noco_parity.json node --test web/tests/parity.test.mjs
