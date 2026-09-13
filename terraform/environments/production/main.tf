terraform {
  required_version = ">= 1.9.0"

  backend "s3" {
    bucket                      = "draftforge-tfstate"
    key                         = "production/terraform.tfstate"
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
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.40"
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

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

module "services" {
  source = "../../modules/render-service"

  environment  = "production"
  repo_url     = var.repo_url
  branch       = "main"
  backend_plan = "standard"

  # Exact origins only. The behaviour this replaces trusted every
  # *.onrender.com host, which anyone can obtain by deploying there.
  allowed_origins = [
    "https://${var.app_hostname}",
  ]
  trusted_hosts = [
    var.api_hostname,
    "draftforge-production-api.onrender.com",
  ]
  app_public_url = "https://${var.app_hostname}"

  # Redundant - the application forces docs off in production regardless - but
  # stated here so the intent is visible in the plan.
  enable_docs = false
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
  email_from_address = "DraftForge <onboarding@${var.root_domain}>"

  otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
  otel_exporter_otlp_headers  = var.otel_exporter_otlp_headers
  # Sampled down: production volume makes full tracing expensive, and 25% is
  # ample to characterise latency. Errors are still recorded on their spans.
  otel_traces_sampler_ratio = 0.25
}

module "observability" {
  source = "../../modules/observability"

  environment         = "production"
  stack_slug          = var.grafana_stack_slug
  dashboard_dir       = "${path.root}/../../../observability/dashboards"
  alert_contact_email = var.alert_contact_email
}

module "edge" {
  source = "../../modules/edge"

  environment          = "production"
  zone_id              = var.cloudflare_zone_id
  api_hostname         = var.api_hostname
  app_hostname         = var.app_hostname
  render_backend_host  = "draftforge-production-api.onrender.com"
  render_frontend_host = "draftforge-production-web.onrender.com"
}

output "api_url" {
  value = module.edge.api_url
}

output "app_url" {
  value = module.edge.app_url
}

output "backend_service_id" {
  description = "Set as RENDER_PROD_BACKEND_SERVICE_ID in repository secrets."
  value       = module.services.backend_service_id
}

output "frontend_service_id" {
  description = "Set as RENDER_PROD_FRONTEND_SERVICE_ID in repository secrets."
  value       = module.services.frontend_service_id
}
