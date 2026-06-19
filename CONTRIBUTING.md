# Contributing

## Prerequisites

- Java **17**
- Maven **3.9+**
- Docker (optional, for local provider image)

## Quick start

```bash
make help
make test
make package
```

## Makefile

Run `make help` for the full target list. Common targets:

| Target | Description |
|--------|-------------|
| `make help` | Show all targets |
| `make test` | Run unit tests |
| `make verify` | Run tests and packaging checks (`mvn verify`) |
| `make audit` | Scan dependencies for CVEs (`dependency-check:check`) |

Report: `target/dependency-check-report.html`. First run downloads the NVD database and can take several minutes. Optional: `NVD_API_KEY` env var for faster NVD sync ([nvd.nist.gov](https://nvd.nist.gov/developers/request-an-api-key)).

| `make package` | Build provider JAR |
| `make dist` | Copy JAR into `dist/` |
| `make image` | Build local Docker provider image |
| `make clean` | Remove `target/`, `dist/` |
| `make version` | Print Maven project version |

## Project layout

```text
src/main/java/io/github/aliasguard/   SPI implementation
src/main/resources/META-INF/services/ Service loader registrations
src/main/resources/theme-resources/   i18n message bundles
src/test/java/                        Unit tests
build/Provider.Dockerfile             Scratch OCI wrapper for the JAR
.github/workflows/ci.yml            GitHub Actions CI
```

## Local development

```bash
make test          # fast feedback loop
make verify        # same as CI test job
make package       # produce JAR in target/
make dist          # copy JAR to dist/
make image         # docker build keycloak-alias-guard:local
make clean         # reset build outputs
```

### Run tests only

```bash
make test
# or
mvn -B test
```

### Build JAR without tests

```bash
make package-skip-tests
```

### Local provider image

```bash
make image
docker run --rm keycloak-alias-guard:local ls -la /jar
```

## CI (GitHub Actions)

Workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

| Event | Pipeline |
|-------|----------|
| Pull request → `main` | `make verify` |
| Push → `main` | verify + JAR artifact + GHCR image (`<version>-sha.<short>`) |
| Tag `v*` (e.g. `v1.0.0`) | verify + GHCR image + GitHub Release with JAR + `latest` tag |

Published container:

```text
ghcr.io/kolosov/keycloak-alias-guard:<version>
```

For private packages, authenticate with a GitHub PAT (`read:packages`).

## Release

From a clean `main` branch with a `-SNAPSHOT` version in `pom.xml`:

```bash
make release-patch   # 0.1.0-SNAPSHOT -> v0.1.0 -> 0.1.1-SNAPSHOT
make release-minor   # 0.1.0-SNAPSHOT -> v0.2.0 -> 0.2.1-SNAPSHOT
make release-major   # 0.1.0-SNAPSHOT -> v1.0.0 -> 1.0.1-SNAPSHOT
```

Each target runs preflight checks first: `-SNAPSHOT` in `pom.xml`, tag not present locally or on `origin`, clean `main` (skipped for `--dry-run`).

1. Sets the release version in `pom.xml` (removes `-SNAPSHOT`, bumps minor/major when needed).
2. Commits, creates an annotated tag, and pushes `main` + the tag.
3. Bumps `pom.xml` to the next `-SNAPSHOT`, commits, and pushes `main`.

CI on the tag creates a GitHub Release and attaches the JAR.

Preview without changes:

```bash
python3 scripts/release.py patch --dry-run
```

Local only (no push):

```bash
python3 scripts/release.py patch --no-push
```

Manual bumps without releasing: `make bump-patch` / `make bump-minor` / `make bump-major`.

Pre-release check (non-SNAPSHOT version):

```bash
make release-check
```

## Adding behavior

- Canonicalization rules: `EmailCanonicalizer.java`
- Duplicate detection: `MailboxDuplicateChecker.java`
- Validator SPI id: `alias-guard` (`AliasGuardValidator.java`)
- Event listener id: `alias-guard-listener` (`AliasGuardEventListenerFactory.java`)

Add unit tests in `EmailCanonicalizerTest.java` for every new canonicalization rule.

### Message locales

Error strings follow Keycloak base theme locales (see `scripts/sync-message-locales.py`):

```bash
python3 scripts/sync-message-locales.py
```

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
