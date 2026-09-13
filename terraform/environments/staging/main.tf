terraform {
  required_version = ">= 1.9.0"

  # State holds every value Terraform touches, secrets included, in plaintext.
  # It lives in a versioned remote bucket with locking - never in the repo.
  backend "s3" {
    bucket                      = "draftforge-tfstate"
    key                         = "staging/terraform.tfstate"
    region                      = "auto"
    use_lockfile                = true
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
  }

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.3"
    }
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.7"
    }
  }
}

provider "render" {
  api_key  = var.render_api_key
  owner_id = var.render_owner_id
}

provider "grafana" {
  url  = var.grafana_cloud_url
  auth = var.grafana_cloud_token
}

module "services" {
  source = "../../modules/render-service"

  environment  = "staging"
  repo_url     = var.repo_url
  branch       = "main"
  backend_plan = "starter"

  allowed_origins = [
    "https://draftforge-staging-web.onrender.com",
  ]
  trusted_hosts = [
    "draftforge-staging-api.onrender.com",
  ]
  app_public_url = "https://draftforge-staging-web.onrender.com"

  # Staging keeps the interactive docs: it is the environment people explore
  # the API in. Production forces them off regardless of this value.
  enable_docs = true
  log_format  = "json"

  supabase_url              = var.supabase_url
  supabase_anon_key         = var.supabase_anon_key
  supabase_service_role_key = var.supabase_service_role_key
  supabase_jwt_secret       = var.supabase_jwt_secret

  neo4j_uri      = var.neo4j_uri
  neo4j_username = var.neo4j_username
  neo4j_password = var.neo4j_password

  qdrant_url     = var.qdrant_url
  qdrant_api_key = var.qdrant_api_key

  groq_api_key = var.groq_api_key
  redis_url    = var.redis_url

  resend_api_key     = var.resend_api_key
  email_from_address = "DraftForge Staging <staging@draftforge.app>"

  otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
  otel_exporter_otlp_headers  = var.otel_exporter_otlp_headers
  # Full sampling in staging: volume is low and complete traces are worth more
  # than the saving.
  otel_traces_sampler_ratio = 1.0
}

module "observability" {
  source = "../../modules/observability"

  environment         = "staging"
  stack_slug          = var.grafana_stack_slug
  dashboard_dir       = "${path.root}/../../../observability/dashboards"
  alert_contact_email = var.alert_contact_email
}

output "api_url" {
  value = module.services.backend_url
}

output "app_url" {
  value = module.services.frontend_url
}

output "backend_service_id" {
  description = "Set as RENDER_STAGING_BACKEND_SERVICE_ID in repository secrets."
  value       = module.services.backend_service_id
}

output "frontend_service_id" {
  description = "Set as RENDER_STAGING_FRONTEND_SERVICE_ID in repository secrets."
  value       = module.services.frontend_service_id
}
