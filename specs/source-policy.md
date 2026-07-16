# Source Policy

Spec version: 1.0.0

## Source selection

Prefer primary, dated, and identifiable sources. For a real provider this would
normally mean regulated filings, issuer publications, or an authorized data
service. The offline slice uses only an InvestKit-owned fictional fixture.

## Provenance contract

For every source retain:

- stable identifier and human-readable title;
- provider or fixture identity and version;
- as-of date and retrieval time when one exists;
- market, currency, units, and field definitions when applicable;
- limitations, warnings, and any missing fields;
- the local task data artifact derived from the source.

Source references must be deterministic and must stay within approved first-party
source and initialized project roots. A source record is not evidence of truth by
itself; source quality and conflicts must still be evaluated.

## Restrictions

Do not fetch undeclared network resources, execute source material, weaken
transport security, or expose credentials. Do not imply that fixture data is
real-time. No source grants permission for brokerage or transaction activity.
