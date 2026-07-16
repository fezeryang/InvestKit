# Security Identification Method Contract

Version: 1.0

## Required Inputs

- Raw subject query.
- Bounded Provider identity candidates with source metadata.

## Ordered Checks

1. Normalize query fields.
2. Compare legal entity, listing, market, and exchange.
3. Require one unique candidate.
4. Preserve ambiguity and missing disambiguators otherwise.

## Method Payload

Record `query`, `candidate_count`, `matched_fields`, `canonical_security`, `ambiguities`, and `provider_record_id`. A completed result requires a stable security ID, legal name, ticker, market, exchange, source ID, and demo status.

## Guards

- Never infer an identity outside supplied candidates.
- Never merge issuer and listing IDs.
- Never treat a fictional fixture as a real security.
