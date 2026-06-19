# keycloak-alias-guard

Keycloak SPI provider: **one mailbox — one account**.

`duplicateEmailsAllowed: false` compares email strings literally. The same person can register `user+1@gmail.com`, `u.ser@gmail.com`, and other aliases of one inbox. **keycloak-alias-guard** canonicalizes addresses and rejects registration or email change when the mailbox is already taken.

## Requirements

- Keycloak **26.5.x** (26.x with declarative User Profile)
- `registrationEmailAsUsername: true` or email as the primary user identifier (recommended)
- Declarative User Profile enabled (`declarative-user-profile`)

## What it does

| Component | Provider ID | Role |
|-----------|-------------|------|
| User Profile validator | `alias-guard` | Blocks duplicate mailbox on registration and email update |
| Event listener | `alias-guard-listener` | Writes `email_canonical` user attribute for fast lookup |

### Canonicalization

1. Trim and lowercase
2. **Gmail / Googlemail**: remove `.` in local part, strip `+tag`, domain → `gmail.com`
3. **Other domains**: strip `+tag` only

Examples:

| Input | Canonical form |
|-------|----------------|
| `U.Ser+promo@GoogleMail.com` | `user@gmail.com` |
| `john+2@outlook.com` | `john@outlook.com` |
| `already@gmail.com` already exists | `a.lready+1@gmail.com` is rejected |

## Installation

### Option A — JAR (recommended)

1. Download `keycloak-alias-guard-*.jar` from [GitHub Releases](https://github.com/dnwsilver/keycloak-alias-guard/releases) or build locally (see [CONTRIBUTING.md](CONTRIBUTING.md)).
2. Copy the JAR into Keycloak providers directory:

   ```text
   /opt/keycloak/providers/keycloak-alias-guard.jar
   ```

3. Rebuild the optimized server image:

   ```bash
   /opt/keycloak/bin/kc.sh build
   ```

4. Start Keycloak (`kc.sh start` or your container entrypoint).

### Option B — OCI provider image

Published images:

```text
ghcr.io/kolosov/keycloak-alias-guard:<version>
```

The image is a scratch wrapper with the JAR under `/jar/`. Extract it into your Keycloak build context or multi-stage Dockerfile:

```bash
docker pull ghcr.io/kolosov/keycloak-alias-guard:1.0.0
docker create --name kag-tmp ghcr.io/kolosov/keycloak-alias-guard:1.0.0
docker cp kag-tmp:/jar/. ./providers/
docker rm kag-tmp
/opt/keycloak/bin/kc.sh build
```

## Realm configuration

Deploy the **JAR first**, then apply realm settings. Import fails if the validator is referenced before the SPI is present.

### 1. User Profile — email validator

Add `alias-guard` to the `email` attribute validations (declarative User Profile JSON):

```json
{
  "name": "email",
  "validations": {
    "email": {},
    "length": { "max": 255 },
    "alias-guard": {}
  }
}
```

If you manage realms as YAML/JSON import, merge this into the `kc.user.profile.config` block for the `email` attribute.

### 2. Event listener

Register the listener so `email_canonical` is stored on user events.

**Admin Console:** Realm settings → Events → Event listeners → add `alias-guard-listener`.

**Declarative import:**

```yaml
eventsListeners:
  - jboss-logging
  - alias-guard-listener
```

Keep existing listeners (for example `jboss-logging`); append `alias-guard-listener`.

### 3. Recommended realm flags

| Setting | Value |
|---------|-------|
| `duplicateEmailsAllowed` | `false` |
| `registrationEmailAsUsername` | `true` |
| `verifyEmail` | `true` |

## Existing users (backfill)

Before enabling in production, set `email_canonical` for users created before the plugin. Use Admin REST or `kcadm`. Resolve duplicate canonical collisions manually — do not auto-merge accounts.

Example attribute value: canonical form of the user’s current email (same rules as above).

## Startup diagnostics

On Keycloak start, when the provider JAR is loaded, logs include:

```text
Alias Guard loaded: component=validator provider-id=alias-guard version=0.1.0-SNAPSHOT
Alias Guard loaded: component=event-listener provider-id=alias-guard-listener version=0.1.0-SNAPSHOT
```

Also visible in **Admin Console → Server info** (provider operational info).

## Error messages

Message key: `error-mailbox-not-unique`

Translations cover all locales shipped with Keycloak **26.5.x** base login theme (40 bundles, including `zh_Hans` / `zh_Hant` and legacy `zh_CN` / `zh_TW`). Wording matches Keycloak’s built-in `emailExistsMessage` per locale. Missing locale → English fallback.

Regenerate from upstream Keycloak:

```bash
python3 scripts/sync-message-locales.py
```

Bundles live in `src/main/resources/theme-resources/messages/`. Override in your login theme if needed.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for build, test, release, and CI.

## License

MIT — see [LICENSE](LICENSE).
