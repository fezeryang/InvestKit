# Manifest-Driven Harness Design

Date: 2026-07-17

## Why a control plane is required

The current Runtime knows an allowlisted set of Skills and one fixed workflow. It
does not model a candidate that is present but unavailable, an API that is usable
only with a credential, a reference that must never execute, or two interchangeable
providers for the same capability. Those are control-plane concerns.

A Trellis-like investment Harness needs a stable separation:

```text
descriptive catalog
  -> governance and permission policy
  -> intent-to-capability selection
  -> dependency planning
  -> typed adapter execution
  -> persisted evidence and diagnostics
```

## Manifest contract

Each entry should contain only declarative values and stable adapter identifiers.
It must not contain import strings, shell commands, arbitrary URLs to execute, or
code paths controlled by a candidate. A first-party registry maps known adapter IDs
to implementations.

Required dimensions:

- identity: schema version, stable asset ID, display name, version/origin;
- classification: exactly one taxonomy type and one or more capability tags;
- governance: decision, approval status, review evidence, license status;
- execution: runtime state, adapter kind/ID, dependencies, platform support;
- permissions: network mode, allowlisted hosts, credential environment names;
- operator explanation: bounded reason and remediation text.

## Planner behavior

Planning must be a pure offline operation. Its inputs are the normalized research
intent, catalog snapshot, policy/permission snapshot, and requested workflow
profile. Its output lists:

- selected assets in dependency order;
- alternatives considered;
- skipped assets and explicit reasons;
- blocking capabilities and remediation;
- the catalog/policy digest used for resume validation.

The planner rejects cycles, unknown dependencies, incompatible types, blocked
adapters, and ambiguous provider ties. Execution consumes the frozen plan and may
not silently substitute an asset after work starts.

## Adapter boundary

The first implementation should use typed Python protocols inside the existing
standard-library-only package. This is smaller and safer than dynamically importing
candidate code. Stable families are Skill, Tool/MCP, Data Provider, Quant Module,
Agent, Workflow, Template, and Reference. Reference adapters are intentionally
non-executable.

Future MCP or subprocess plugins can sit behind the same protocol after an approved
isolation and authentication design. The catalog schema should therefore avoid
assuming that every adapter is an in-process Python class.

## Guangfa security boundary

The adapted draft documentation identifies a shared HTTPS endpoint and
`GF_SKILLS_APIKEY`. A safe first-party adapter must:

- accept the key only from an injected environment lookup;
- require a separate explicit network-permission value;
- allowlist the exact HTTPS origin and reject redirects to other origins;
- use bounded timeouts and response sizes;
- validate strict JSON and operation-specific response shapes;
- redact headers, request bodies, credentials, and vendor payloads from errors;
- expose an injectable transport so tests are entirely offline;
- distinguish authentication, throttling, vendor, schema, and network failures.

No live request is part of automated tests. Live verification is a separate operator
action and must be reported as unverified until performed with authorization.

## Delivery slices

1. Catalog visibility is the first useful outcome: all 49 assets become queryable
   and diagnosable without making any asset executable.
2. Dependency planning turns the catalog into a Harness rather than an inventory.
3. Guangfa F10 and valuation adapters enable the first equity data path.
4. Symbol-first research composes provider evidence with selected analytical Skills.
5. Package lifecycle and additional host projections build on the same catalog.

This sequence prevents a credentialed integration from becoming a one-off path that
bypasses governance, persistence, or Doctor.
