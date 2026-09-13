# Supplied as TF_VAR_* from GitHub Actions secrets. Never committed to a
# .tfvars file - see .gitignore.

variable "repo_url" {
  type    = string
  default = "https://github.com/HimanshiSingla-Sigma/DraftForge-2"
}

# -----------------------------------------------------------------------------
# Provider credentials
# -----------------------------------------------------------------------------
variable "render_api_key" {
  type      = string
  sensitive = true
}

variable "render_owner_id" {
  type = string
}

variable "grafana_cloud_url" {
  type = string
}

variable "grafana_cloud_token" {
  type      = string
  sensitive = true
}

variable "grafana_stack_slug" {
  type = string
}

variable "alert_contact_email" {
  type = string
}

# -----------------------------------------------------------------------------
# Managed services provisioned outside Terraform
#
# Supabase, Qdrant Cloud and Neo4j Aura have no provider capable of creating a
# project or cluster, so they are created once by hand and their connection
# details passed in here.
# -----------------------------------------------------------------------------
variable "supabase_url" {
  type      = string
  sensitive = true
}

variable "supabase_anon_key" {
  type      = string
  sensitive = true
}

variable "supabase_service_role_key" {
  type      = string
  sensitive = true
}

variable "supabase_jwt_secret" {
  type      = string
  sensitive = true
}

variable "neo4j_uri" {
  type      = string
  sensitive = true
}

variable "neo4j_username" {
  type      = string
  sensitive = true
}

variable "neo4j_password" {
  type      = string
  sensitive = true
}

variable "qdrant_url" {
  type      = string
  sensitive = true
}

variable "qdrant_api_key" {
  type      = string
  sensitive = true
}

variable "groq_api_key" {
  type      = string
  sensitive = true
}

variable "redis_url" {
  type      = string
  sensitive = true
}

variable "resend_api_key" {
  type      = string
  sensitive = true
}

# -----------------------------------------------------------------------------
# Observability
# -----------------------------------------------------------------------------
variable "otel_exporter_otlp_endpoint" {
  type    = string
  default = ""
}

variable "otel_exporter_otlp_headers" {
  type      = string
  sensitive = true
  default   = ""
}
