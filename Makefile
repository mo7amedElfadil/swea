# Makefile for the Application (Frontend & Backend)
.PHONY: help setup check-dependencies clean check_venv run_flask watch_tw watch_static queue_worker up_db down_db stop_flask stop_tailwind stop_static stop_queue restart restart_tw stop_static stop_queue list status test version update-translation db_init db_migrate db_upgrade db_reset

# Default target
.DEFAULT_GOAL := help

# Commands
TMUX := $(shell which tmux 2> /dev/null)
NPM := $(shell which npm 2> /dev/null)
PYTHON := $(shell which python3 2> /dev/null)
FLASK := $(shell which flask 2> /dev/null)

# Colors
RED := \e[31m
GREEN := \e[32m
BOLD := \e[1m
RESET := \e[0m

# Sessions
SWEA_SESSION := swea
TAILWIND_SESSION := tailwind
STATIC_FILE_SESSION := hmr
WORKER_SESSION := queue_worker

# scripts
TW_WATCH := npm run dev:wt_css
#STATIC_WATCH := npm run dev:static
FLASK_RUN := python -m app.run # flask run
QUEUE_WORKER := python -m app.services.queue_worker
VEN_ACTIVATE := . .venv/bin/activate
UP_DB := docker compose up -d
DOWN_DB := docker compose down

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
	@$(MAKE) -s check_npm || exit 1
	@$(MAKE) -s db_init || exit 1
	@$(MAKE) -s db_migrate || exit 1 
	@$(MAKE) -s db_upgrade || exit 1


# Check and install dependencies
check-dependencies:
ifndef TMUX
	@echo "-------Installing tmux...---------"
	sudo apt-get update
	sudo apt-get install -y tmux
endif

# Clean project dependencies
clean: ## Clean project dependencies
	@echo "Removing __pycache__ ..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +

check_venv:
	@if [ ! -d ".venv" ]; then \
		echo ".venv does not exist. Creating virtual environment..."; \
		$(PYTHON) -m venv .venv && \
		$(VEN_ACTIVATE) && \
		echo "Installing requirements..."; \
		pip install --quiet -r requirements.txt; \
		echo "Virtual environment is ready."; \
	else \
		$(VEN_ACTIVATE); \
	fi
	

check_npm:
	@if [ ! -d "node_modules" ]; then \
		echo "node_modules does not exist. Installing npm packages..."; \
		$(NPM) install --silent; \
	fi


#run everything
run: run_flask watch_tw watch_static queue_worker ## Run the application



# Run sessions
run_flask: clean check_venv ## Run flask application
	@$(call run_session,$(SWEA_SESSION),$(VEN_ACTIVATE) && $(FLASK_RUN))

watch_tw: check_npm clean ## Run tailwindcss watch
	@$(call run_session,$(TAILWIND_SESSION),$(TW_WATCH))

watch_static: ## Watch for changes in css, html files
	@echo 'Watching for changes in static files {html,css}...'
	@$(call run_session,$(STATIC_FILE_SESSION),hmr app)

queue_worker: clean check_venv ## Run the queue worker
	@echo 'Running the queue worker...'
	@$(call run_session,$(WORKER_SESSION),$(VEN_ACTIVATE) && $(QUEUE_WORKER))

up_db: ## Start the database (docker-compose: MongoDB & Redis)
	@$(UP_DB)

down_db: ## Stop the database (docker-compose: MongoDB & Redis)
	@$(DOWN_DB)

# Stop everything
stop: stop_flask stop_tailwind stop_static stop_queue ## Stop the application

# Stop sessions
stop_flask: ## Stop flask application
	@$(call kill_session,$(SWEA_SESSION))

stop_tailwind: ## Stop tailwindcss watch
	@$(call kill_session,$(TAILWIND_SESSION))

stop_static: ## Stop watching static files 
	@$(call kill_session,$(STATIC_FILE_SESSION))

stop_queue: ## Stop the queue worker
	@$(call kill_session,$(QUEUE_WORKER))

# Restart application
restart: ## Restart flask server
	@$(MAKE) -s stop_flask run_flask && \
	echo "$(BOLD)Restarted$(RESET)"

restart_tw: stop_tailwind  ## Restart tailwindcss watch
	@$(MAKE) -s watch_tw

restart_static: stop_static ## Restart watching static files
	@$(MAKE) -s watch_static

restart_queue: stop_queue ## Restart the queue worker
	@$(MAKE) -s queue_worker

list: ## List all running tmux sessions
	@$(TMUX) ls

# Check status
status: ## Check the status of tmux sessions
	@$(TMUX) ls || echo "No tmux sessions running."

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

# Database management
db_init: ## Initialize the database with Flask-Migrate
	@echo "Initializing database with Flask-Migrate..."
	@$(FLASK) db init

db_migrate: ## Generate a new migration script
	@echo "Generating migration script..."
	@$(FLASK) db migrate -m "Initial setup"

db_upgrade: ## Apply the latest migration to the database
	@echo "Applying the latest migration..."
	@$(FLASK) db upgrade

db_reset: ## Reset the database (drop all tables and reapply migrations)
	@echo "Resetting the database..."
	@$(FLASK) db downgrade base
	@$(FLASK) db upgrade

# Help message
help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
