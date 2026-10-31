reproduce:
	bash scripts/reproduce.sh

test:
	.venv/bin/python -m pytest -q
