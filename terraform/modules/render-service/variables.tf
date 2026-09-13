variable "environment" {
  description = "Deployment environment. Drives naming and the production safety invariants."
  type        = string

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be either \"staging\" or \"production\"."
  }
}

variable "service_name_prefix" {
  description = "Prefix for the Render service names."
  type        = string
  default     = "draftforge"
}

variable "repo_url" {
  description = "Git repository Render deploys from."
  type        = string
}

variable "branch" {
  description = "Branch Render tracks for this environment."
  type        = string
  default     = "main"
}

variable "region" {
  description = "Render region."
  type        = string
  default     = "oregon"
}

variable "backend_plan" {
  description = "Render instance plan for the API."
  type        = string
  default     = "starter"
}

# -----------------------------------------------------------------------------
# Application configuration
# -----------------------------------------------------------------------------

variable "allowed_origins" {
  description = "Exact browser origins permitted to call the API. No wildcards."
  type        = list(string)

  validation {
    condition     = !contains(var.allowed_origins, "*")
    error_message = "allowed_origins must not contain \"*\". Credentialed CORS requires exact origins."
  }
}

variable "trusted_hosts" {
  description = "Accepted Host header values."
  type        = list(string)
}

variable "app_public_url" {
  description = "Public URL of the frontend. Used to build invitation links."
  type        = string
}

variable "enable_docs" {
  description = "Expose /docs and /openapi.json. Ignored in production by the application."
  type        = bool
  default     = false
}

variable "log_format" {
  description = "console or json. Deployed environments should use json so Loki can index fields."
  type        = string
  default     = "json"
}

# -----------------------------------------------------------------------------
# Secrets
#
# Every one of these is sensitive, which keeps it out of plan output and CI
# logs. They are supplied as TF_VAR_* from repository secrets, never committed.
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
  description = "Bypasses row-level security. Never expose to any client."
  type        = string
  sensitive   = true
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

variable "groq_model" {
  type    = string
  default = "llama-3.3-70b-versatile"
}

variable "redis_url" {
  description = "Backs rate limiting and LLM token budgets."
  type        = string
  sensitive   = true
}

variable "resend_api_key" {
  type      = string
  sensitive = true
}

variable "email_from_address" {
  type    = string
  default = "DraftForge <onboarding@draftforge.app>"
}

variable "otel_exporter_otlp_endpoint" {
  type    = string
  default = ""
}

variable "otel_exporter_otlp_headers" {
  type      = string
  sensitive = true
  default   = ""
}

variable "otel_traces_sampler_ratio" {
  description = "Fraction of traces sampled. Lower in production to control cost."
  type        = number
  default     = 1.0

  validation {
    condition     = var.otel_traces_sampler_ratio >= 0 && var.otel_traces_sampler_ratio <= 1
    error_message = "otel_traces_sampler_ratio must be between 0 and 1."
  }
}
