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

1. Set release version in `pom.xml` (remove `-SNAPSHOT`), or bump with `make bump-patch` / `make bump-minor` / `make bump-major`.
2. Commit and push to `main`.
3. Create and push an annotated tag:

   ```bash
   git tag -a v0.1.0 -m "v0.1.0"
   git push origin v0.1.0
   ```

4. CI creates a GitHub Release and attaches the JAR.
5. Bump `pom.xml` to the next `-SNAPSHOT` on `main`.

Pre-release check:

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
