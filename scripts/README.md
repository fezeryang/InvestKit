# Scripts

This directory contains offline InvestKit maintenance and validation scripts.

Current stage rules:

- Do not add scripts that execute third-party assets.
- Do not add scripts that connect to brokerages or real-money services.
- Do not hardcode API keys.
- Prefer read-only validation scripts for Schema, registry, and report consistency.

Validate the complete governed Runtime Skill set with:

```bash
python3 scripts/quick_validate.py
```

The command is read-only, dependency-free, and fails unless exactly the one Runtime
prerequisite plus all 12 Investment Core Skill directories validate together.
