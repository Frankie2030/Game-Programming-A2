# Variables
# TEST=test
MAIN_SCRIPT=main.py

.PHONY: install run

# Run code locally
run:
	source .venv/bin/activate && \
	python3 src/$(MAIN_SCRIPT)

# Install Python dependencies locally
install:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r requirements.txt
