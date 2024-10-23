# Set default target
.DEFAULT_GOAL := help

# Variables

## Python
PYTHON := python3
PIP := pip
VENV_NAME := venv

# .env file
ENV_FILE := .env

# Help target
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  1. install           Install dependencies and set up the environment (should be run first)"
	@echo "  2. run_single_agent  Run the single-agent interaction example script"	
	@echo "  3. run_multi_agent   Run the multi-agent interaction example script"
	@echo "  4. copy_env          Copy the .env.example file to .env"
	@echo "  5. test              Run the tests"
	@echo "  6. clean             Remove the virtual environment and its contents"

# Install dependencies and set up the environment
install: 
	$(PYTHON) -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate && \
	$(PIP) install -r requirements.txt 

# Copy the .env.example file to .env
copy_env:
	cp .env.example .env

# Run the single-agent interaction example script
run_single_agent: 
	. $(VENV_NAME)/bin/activate && \
	$(PYTHON) single_agent_example.py

# Run the multi-agent interaction example script
run_multi_agent:
	. $(VENV_NAME)/bin/activate && \
	$(PYTHON) multi_agent_example.py

# Run the tests
test:
	. $(VENV_NAME)/bin/activate && \
	pytest -v tests/

# Clean the virtual environment
clean:
	rm -rf $(VENV_NAME)