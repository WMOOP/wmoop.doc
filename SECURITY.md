# Security Policy

WMOOP is primarily a **data and code-generation** project, so its security surface is unusual.
Please read this before reporting.

## What counts as a security issue here

1. **Supply-chain / toolchain.** The generator and validators (planned `wmoop.tools`) turn WML
   model files into code in several languages. A malicious or malformed model file, or a bug in a
   generator template, could cause generated code to do something harmful, or could execute
   untrusted input at generation time. These are the highest-severity issues.
2. **Untrusted execution.** Conformance tests, demos and generators must **never** execute content
   embedded in model data. Model files are *data*, not scripts. A path that evaluates model content
   as code is a vulnerability.
3. **CI / automation.** Workflows that run on pull requests must not expose secrets to untrusted
   PRs, and must not run untrusted generated code with elevated permissions.
4. **Dependency vulnerabilities** in any binding repo (`wmoop.net`, etc.).

Factual errors, biased or disputed content, and ordinary modelling mistakes are **not** security
issues — raise those as normal issues (see [CONTRIBUTING.md](CONTRIBUTING.md) and
[ETHICS.md](ETHICS.md)).

## Reporting a vulnerability

- **Preferred:** open a [GitHub private security advisory](https://docs.github.com/code-security/security-advisories)
  on the affected repository ("Security" → "Report a vulnerability").
- Do **not** open a public issue for an exploitable vulnerability until it has been triaged and a
  fix is available.
- Include: affected repo and version/commit, a minimal reproduction (e.g. a model file or template
  that triggers it), impact, and any suggested mitigation.

## Our commitment

- We acknowledge reports within **5 working days** and aim to provide a remediation plan within
  **30 days** for confirmed issues.
- Generators and validators are designed to treat all model input as untrusted and to run in a
  sandbox with no network and no evaluation of model content.
- Security-relevant changes are recorded in [CHANGELOG.md](CHANGELOG.md).

> This policy is a starting point for a young project and will tighten as the toolchain matures.
