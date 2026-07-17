# Security Policy

InvestKit handles credentialed, read-only investment data and must never receive
brokerage credentials, order authority, private keys, or funds-transfer secrets.

Do not report a vulnerability in a public issue when the report contains an API
key, credential, private research bundle, unpublished issuer information, or a
working exploit. Use GitHub's private vulnerability reporting for this repository
when it is enabled by the owner. Otherwise contact the repository owner privately
without attaching secrets or proprietary data.

The detailed project policy is maintained in
[`docs/security/security-policy.md`](docs/security/security-policy.md). It covers
third-party Skills, provider credentials, network permission, provenance, local
files, telemetry, and the permanent no-trading boundary.

Only the latest published release is eligible for security fixes. Until a GitHub
release is published, the `main` branch is development software and must not be
treated as a supported production release.
