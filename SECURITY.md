# Security policy

Report a problem with this repo through GitHub private vulnerability reporting (Security tab).

This repo is read-only API research: no report filing, no login, no real
identity, no load testing. The only secret-shaped string in it is the shared
key embedded in the municipality's public Play-Store APK (see
docs/design.md). Filing credentials, if ever approved, live in Actions
secrets / the vault, never in files.
