# Infrastructure as Code

Terraform definitions for DraftForge's managed-SaaS stack: Render (compute),
Grafana Cloud (observability), Cloudflare (DNS and WAF) and Upstash (Redis).

```
terraform/
├── modules/
│   ├── render-service/     # Backend web service + frontend static site
│   ├── observability/      # Grafana Cloud stack, dashboards and alert rules
│   └── edge/               # Cloudflare DNS, WAF and rate limiting
└── environments/
    ├── staging/
    └── production/
```

## What is and is not managed here

**Managed:** Render services and their environment variables, Grafana Cloud
stacks, dashboards and alert rules, Cloudflare DNS records and WAF rules, and
the Upstash Redis instance backing rate limiting.

**Not managed:** Supabase, Qdrant Cloud and Neo4j Aura. None of the three has a
Terraform provider capable of creating a project or cluster, so those are
provisioned once by hand and their connection details supplied as variables.
The database *schema* is versioned in `backend/migrations/`, which is the part
that actually changes.

This split is deliberate. A module that only pretends to manage a resource is
worse than an honest gap — it implies a `terraform destroy` would clean up
state that it would in fact leave behind.

## State

State lives in an S3-compatible bucket with locking, never in the repository:
it contains every value Terraform touches, including secrets, in plaintext.
`.gitignore` excludes `*.tfstate` and `*.tfvars` for that reason.

## Usage

```bash
cd terraform/environments/staging
terraform init
terraform plan      # CI posts this on every pull request
terraform apply     # CI applies on merge, gated by environment protection
```

Credentials are supplied as `TF_VAR_*` environment variables from GitHub
Actions secrets — never in a `.tfvars` file.

## First-time setup

1. Create the state bucket and enable versioning, so a corrupted state can be
   rolled back.
2. Provision Supabase, Qdrant and Neo4j by hand; record their URLs and keys.
3. Populate the repository secrets listed in `.github/workflows/terraform.yml`.
4. `terraform init && terraform apply` in `environments/staging` first —
   production should never be the environment a change is first tried on.
