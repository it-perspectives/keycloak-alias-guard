# keycloak-alias-guard — developer commands
#
# Usage:
#   make help              Show all targets
#   make test              Run unit tests
#   make package           Build provider JAR
#
# Requirements: Java 17, Maven 3.9+, Docker (optional, for `image`)

.DEFAULT_GOAL := help

# --- Tooling -----------------------------------------------------------------

MVN        ?= mvn
DOCKER     ?= docker
DOCKER_PLATFORM ?= linux/amd64

# --- Project metadata (from pom.xml) -------------------------------------------

ARTIFACT_ID  := keycloak-alias-guard
JAR_GLOB     := target/$(ARTIFACT_ID)-*.jar
DIST_DIR     := dist
IMAGE_NAME   := keycloak-alias-guard
IMAGE_TAG    ?= local
PROVIDER_DOCKERFILE := build/Provider.Dockerfile

# --- Phony targets -------------------------------------------------------------

.PHONY: help test verify package package-skip-tests dist image clean version release-check sync-locales bump-major bump-minor bump-patch release release-patch release-minor release-major audit

# --- Help ----------------------------------------------------------------------

help: ## Show this help
	@echo "keycloak-alias-guard — available targets:"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make test"
	@echo "  make verify"
	@echo "  make package && make dist && make image"

# --- Build & test --------------------------------------------------------------

test: ## Run unit tests (mvn test)
	$(MVN) -B test

verify: ## Run full verification pipeline (mvn verify) — same as CI test job
	$(MVN) -B verify

audit: ## Scan dependencies for known CVEs (OWASP Dependency-Check; report in target/)
	$(MVN) -B dependency-check:check

package: ## Build provider JAR with tests
	$(MVN) -B package

package-skip-tests: ## Build provider JAR without running tests
	$(MVN) -B package -DskipTests

# --- Distribution --------------------------------------------------------------

dist: package-skip-tests ## Copy built JAR into dist/
	@rm -rf $(DIST_DIR)
	@mkdir -p $(DIST_DIR)
	@cp $(JAR_GLOB) $(DIST_DIR)/
	@ls -la $(DIST_DIR)/

# --- Container image -----------------------------------------------------------

image: dist ## Build local Docker provider image (tag: keycloak-alias-guard:local)
	@VERSION=$$($(MVN) -q -DforceStdout help:evaluate -Dexpression=project.version); \
	$(DOCKER) buildx build \
		--platform $(DOCKER_PLATFORM) \
		--load \
		--build-arg VERSION="$$VERSION" \
		-f $(PROVIDER_DOCKERFILE) \
		-t $(IMAGE_NAME):$(IMAGE_TAG) \
		$(DIST_DIR)
	@echo "Built $(IMAGE_NAME):$(IMAGE_TAG) ($(DOCKER_PLATFORM))"

# --- Utilities -----------------------------------------------------------------

version: ## Print Maven project version
	@$(MVN) -q -DforceStdout help:evaluate -Dexpression=project.version

release-check: ## Fail if pom.xml version still contains SNAPSHOT
	@VERSION=$$($(MVN) -q -DforceStdout help:evaluate -Dexpression=project.version); \
	if echo "$$VERSION" | grep -q SNAPSHOT; then \
		echo "Release blocked: version is $$VERSION (remove -SNAPSHOT first)"; \
		exit 1; \
	fi; \
	echo "Release version OK: $$VERSION"

clean: ## Remove build outputs (target/, dist/)
	$(MVN) -B clean
	@rm -rf $(DIST_DIR)

sync-locales: ## Regenerate message bundles from Keycloak upstream translations
	python3 scripts/sync-message-locales.py

# --- Version -------------------------------------------------------------------

bump-patch: ## Bump patch version in pom.xml (0.1.0-SNAPSHOT -> 0.1.1-SNAPSHOT)
	python3 scripts/bump-version.py patch

bump-minor: ## Bump minor version in pom.xml (0.1.0-SNAPSHOT -> 0.2.0-SNAPSHOT)
	python3 scripts/bump-version.py minor

bump-major: ## Bump major version in pom.xml (0.1.0-SNAPSHOT -> 1.0.0-SNAPSHOT)
	python3 scripts/bump-version.py major

release: ## Show release targets (use release-patch, release-minor, or release-major)
	@echo "Release targets:"
	@echo "  make release-patch   Release current SNAPSHOT as patch (0.1.0-SNAPSHOT -> v0.1.0 -> 0.1.1-SNAPSHOT)"
	@echo "  make release-minor   Release next minor (0.1.0-SNAPSHOT -> v0.2.0 -> 0.2.1-SNAPSHOT)"
	@echo "  make release-major   Release next major (0.1.0-SNAPSHOT -> v1.0.0 -> 1.0.1-SNAPSHOT)"
	@echo ""
	@echo "Dry run: python3 scripts/release.py patch --dry-run"

release-patch: ## Tag patch release, push, bump pom.xml to next SNAPSHOT
	python3 scripts/release.py patch

release-minor: ## Tag minor release, push, bump pom.xml to next SNAPSHOT
	python3 scripts/release.py minor

release-major: ## Tag major release, push, bump pom.xml to next SNAPSHOT
	python3 scripts/release.py major
