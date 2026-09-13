# Infrastructure

Terraform under `terraform/`, targeting Render plus managed SaaS.

## Layout

```
terraform/
├── modules/
│   ├── render-service/    Backend web service + frontend static site
│   ├── observability/     Grafana Cloud folder, dashboards, alert routing
│   └── edge/              Cloudflare DNS, WAF, edge rate limiting
└── environments/
    ├── staging/
    └── production/
```

## What is and is not managed

**Managed:** Render services and their environment variables, Grafana Cloud
dashboards and notification policies, Cloudflare DNS and WAF, Upstash Redis.

**Not managed:** Supabase, Qdrant Cloud, Neo4j Aura.

::: info Why the gap is deliberate
None of the three has a provider capable of creating a project or cluster. They
are provisioned once by hand and their connection details passed in as
variables.

A module that only *pretends* to manage a resource is worse than an honest gap:
it implies a `terraform destroy` would clean up state it would in fact leave
behind, and implies a `plan` would detect drift it cannot see.

The part of those services that actually changes — the schema — is versioned in
`backend/migrations/`.
:::

## Invariants encoded in the modules

The application refuses to start in production unless several conditions hold.
The modules set them, so an environment that would fail that startup check never
gets created:

```hcl
variable "allowed_origins" {
  validation {
    condition     = !contains(var.allowed_origins, "*")
    error_message = "allowed_origins must not contain \"*\"."
  }
}
```

| Setting | Production value | Reason |
| :--- | :--- | :--- |
| `ALLOWED_ORIGINS` | Exact https origins | The `*.onrender.com` regex trusted any deployer |
| `RATE_LIMIT_ENABLED` | `true` | Off means the LLM endpoints are unmetered again |
| `REDIS_REQUIRED` | `true` | Limits must fail closed, not open |
| `ENABLE_DOCS` | `false` | A published schema maps the API for an attacker |
| `DEBUG` | `false` | Tracebacks disclose internals |

## Environment differences

| | Staging | Production |
| :--- | :--- | :--- |
| Instances | 1 | 2 |
| Plan | starter | standard |
| Trace sampling | 100% | 25% |
| Docs | enabled | forced off |
| Custom domain | no | Cloudflare |
| Log level | DEBUG | INFO |

Production runs two instances because FastEmbed loads its ONNX model on first
use — a cold start costs several seconds on the first student request.

Sampling drops to 25% because full tracing at production volume is expensive and
a quarter is ample to characterise latency. Errors are still recorded on their
spans regardless.

## State

Remote, S3-compatible, versioned, with locking.

State contains **every value Terraform touches, secrets included, in
plaintext**. `.gitignore` excludes `*.tfstate` and `*.tfvars` for that reason,
and versioning on the bucket means a corrupted state can be rolled back.

## The edge layer

Cloudflare records are proxied so the WAF actually sees traffic — an unproxied
record bypasses all of it.

Edge rate limiting sits in front of the application limiter. That is not
duplication: the application limiter is per-user and precise, but still costs a
worker, a Redis round trip and a profile lookup per request. An edge rule
rejects a flood before any of that happens.

## First-time setup

1. Create the state bucket; enable versioning.
2. Provision Supabase, Qdrant and Neo4j by hand; record credentials.
3. Populate the repository secrets listed in `terraform.yml`.
4. `terraform apply` in `environments/staging` **first** — production should
   never be where a change is tried first.
5. Copy the service-id outputs into repository secrets for the deploy workflow.

## Changing infrastructure

```bash
cd terraform/environments/staging
terraform plan
```

Open a PR: CI posts the plan as a comment. After merge, run the `terraform`
workflow with `workflow_dispatch` for the target environment. Production is
behind environment protection.

Never `terraform apply` production from a laptop. The audit trail and the
review gate both live in the workflow.
