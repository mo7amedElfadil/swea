# Makefile for the Application (Frontend & Backend)
.PHONY: help setup check-dependencies clean check_venv run_flask watch_tw stop_flask stop_tailwind stop_static restart_tw restart_static list status restart test version update-translation

# Default target
.DEFAULT_GOAL := help

# Commands
TMUX := $(shell which tmux 2> /dev/null)
NPM := $(shell which npm 2> /dev/null)

# Colors
RED := \e[31m
GREEN := \e[32m
BOLD := \e[1m
RESET := \e[0m

# Sessions
SWEA_SESSION := swea
TAILWIND_SESSION := tailwind
STATIC_FILE_SESSION := static

# scripts
TW_WATCH := npx tailwindcss -i ./app/static/css/src/index.css -o ./app/static/css/dist/output.css --minify --watch
FLASK_RUN := python -m app.run # flask run
VEN_ACTIVATE := . .venv/bin/activate

# Define run session
define run_session
	@$(TMUX) new-session -d -s "$(1)" "$(2)"
	@echo -e '$(1) app is $(GREEN)running \e[5m\e[1m...\e[0m$(RESET)'
endef

# Define kill session
define kill_session
	@if $(TMUX) ls | grep -q "$(1)"; then \
		$(TMUX) kill-session -t "$(1)"; \
		echo '$(1) app has $(RED)stopped!$(RESET)'; \
	else \
		echo 'No tmux session named "$(1)" found.'; \
	fi
endef


# Target to set up the project
setup: ## Setup project and install core tools and dependencies
	@$(MAKE) -s check-dependencies || exit 1
	@$(MAKE) -s check_venv || exit 1


# Check and install dependencies
check-dependencies:
ifndef TMUX
	@echo "-------Installing tmux...---------"
	sudo apt-get update
	sudo apt-get install -y tmux
endif
	npm install tailwindcss
	pip install -r requirements.txt

# Clean project dependencies
clean: ## Clean project dependencies
	@echo "Removing __pycache__ ..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +

check_venv:
	@if [ ! -d ".venv" ]; then \
		echo ".venv does not exist. Creating virtual environment..."; \
		python3 -m venv .venv; \
	else \
		$(VEN_ACTIVATE) && \
		$(TMUX) new-session -d -s "$(SWEA_SESSION)" "$(FLASK_RUN)"; \
	fi


# Run sessions
run_flask: check_venv ## Run flask application
	@echo 'flask running on session "swea"'

watch_tw: clean ## Run tailwindcss watch
	@echo 'Watching for changes in tailwindcss...'
	@$(TMUX) new-session -d -s "$(TAILWIND_SESSION)" "$(TW_WATCH)"

stop_flask: ## Stop flask application
	@$(call kill_session,$(SWEA_SESSION))

stop_tailwind: ## Stop tailwindcss watch
	@$(call kill_session,$(TAILWIND_SESSION))

restart_tw: stop_tailwind  ## Restart tailwindcss watch
	@$(MAKE) -s watch_tw

list: ## List all running tmux sessions
	@$(TMUX) ls

# Check status
status: ## Check the status of tmux sessions
	@$(TMUX) ls || echo "No tmux sessions running."

# Restart application
restart: ## Restart flask server
	@$(MAKE) -s stop_flask run_flask && \
	echo "$(BOLD)Restarted$(RESET)"

test: ## Run backend tests
	@echo 'no tests yet'
# Version and info
version: ## Display project version
	@echo "Project Version: 1.0.0"

update-translation: ## Update translations
	@echo "Updating translations..."
	@pybabel extract -F babel.cfg -o messages.pot .
	@pybabel update -i messages.pot -d app/translations
	@pybabel compile -d app/translations
	@$(MAKE) -s restart

# Help message
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
