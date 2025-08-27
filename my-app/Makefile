# Project Makefile
# This file contains targets for environment setup and deployment management

# Define default target when just 'make' is executed
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  help       - Show this help message"
	@echo "  ecosystem  - Set up development environment and dependencies"
	@echo "  clean      - Remove build artifacts and temporary files"
	@echo "  test       - Run project tests"

# The ecosystem target sets up the development environment and deployment configurations
# Usage: make ecosystem [ENV=dev|staging|prod]
#
# ENV variable defaults to 'dev' if not specified
# Example: make ecosystem ENV=prod
.PHONY: ecosystem
ecosystem:
	@echo "Setting up ecosystem for environment: $${ENV:-dev}"
	@echo "Installing dependencies..."
	npm install
	@echo "Configuring environment..."
	@if [ "$${ENV:-dev}" = "dev" ]; then \
		echo "Setting up development environment"; \
		npm run dev; \
	elif [ "$${ENV:-dev}" = "staging" ]; then \
		echo "Setting up staging environment"; \
		npm run build; \
		npm run start; \
	elif [ "$${ENV:-dev}" = "prod" ]; then \
		echo "Setting up production environment"; \
		npm run build; \
		npm run start:prod; \
	else \
		echo "Unknown environment: $${ENV:-dev}"; \
		exit 1; \
	fi
	@echo "Ecosystem setup complete for $${ENV:-dev} environment"

# Clean up build artifacts and temporary files
.PHONY: clean
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf .next
	rm -rf node_modules/.cache
	@echo "Cleanup complete"

# Run project tests
.PHONY: test
test:
	@echo "Running Next.js project tests..."
	npm test
