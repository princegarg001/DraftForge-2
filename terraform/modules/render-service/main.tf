terraform {
  required_version = ">= 1.9.0"

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.3"
    }
  }
}

locals {
  is_production = var.environment == "production"

  backend_name  = "${var.service_name_prefix}-${var.environment}-api"
  frontend_name = "${var.service_name_prefix}-${var.environment}-web"

  # The application refuses to start in production unless these hold (see
  # app/config.py). Setting them here means an environment that would fail
  # that check never gets created in the first place.
  common_env = {
    APP_NAME    = "DraftForge"
    APP_VERSION = "1.0.0"
    ENVIRONMENT = var.environment
    DEBUG       = "false"

    ALLOWED_ORIGINS = join(",", var.allowed_origins)
    TRUSTED_HOSTS   = join(",", var.trusted_hosts)
    APP_PUBLIC_URL  = var.app_public_url
    ENABLE_DOCS     = local.is_production ? "false" : tostring(var.enable_docs)

    SUPABASE_REFERENCE_BUCKET  = "reference-documents"
    SUPABASE_DRAFT_BUCKET      = "student-drafts"
    SUPABASE_SUBMISSION_BUCKET = "assignment-submissions"

    NEO4J_DATABASE         = "neo4j"
    QDRANT_COLLECTION_NAME = "legal_reference_corpus"

    LLM_PROVIDER       = "groq"
    GROQ_MODEL         = var.groq_model
    EMBEDDING_PROVIDER = "fastembed"
    EMBEDDING_MODEL    = "BAAI/bge-small-en-v1.5"

    # Rate limiting must be on and must fail closed in production; the
    # application validates both.
    RATE_LIMIT_ENABLED = "true"
    REDIS_REQUIRED     = "true"

    EMAIL_PROVIDER     = "resend"
    EMAIL_FROM_ADDRESS = var.email_from_address

    OTEL_ENABLED              = var.otel_exporter_otlp_endpoint != "" ? "true" : "false"
    OTEL_SERVICE_NAME         = local.backend_name
    OTEL_TRACES_SAMPLER_RATIO = tostring(var.otel_traces_sampler_ratio)

    LOG_FORMAT = var.log_format
    LOG_LEVEL  = local.is_production ? "INFO" : "DEBUG"
  }

  secret_env = {
    SUPABASE_URL              = var.supabase_url
    SUPABASE_ANON_KEY         = var.supabase_anon_key
    SUPABASE_SERVICE_ROLE_KEY = var.supabase_service_role_key
    SUPABASE_JWT_SECRET       = var.supabase_jwt_secret

    NEO4J_URI      = var.neo4j_uri
    NEO4J_USERNAME = var.neo4j_username
    NEO4J_PASSWORD = var.neo4j_password

    QDRANT_URL     = var.qdrant_url
    QDRANT_API_KEY = var.qdrant_api_key

    GROQ_API_KEY   = var.groq_api_key
    REDIS_URL      = var.redis_url
    RESEND_API_KEY = var.resend_api_key

    OTEL_EXPORTER_OTLP_ENDPOINT = var.otel_exporter_otlp_endpoint
    OTEL_EXPORTER_OTLP_HEADERS  = var.otel_exporter_otlp_headers
  }
}

# -----------------------------------------------------------------------------
# Backend API
# -----------------------------------------------------------------------------
resource "render_web_service" "backend" {
  name   = local.backend_name
  plan   = var.backend_plan
  region = var.region

  runtime_source = {
    native_runtime = {
      auto_deploy   = false # deploys are driven by the deploy workflow, after CI passes
      branch        = var.branch
      build_command = "pip install -r requirements.txt"
      repo_url      = var.repo_url
      runtime       = "python"
      start_command = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers"
      root_directory = "backend"
    }
  }

  env_vars = merge(
    { for k, v in local.common_env : k => { value = v } },
    { for k, v in local.secret_env : k => { value = v } },
  )

  health_check_path = "/health"

  # Production keeps a warm instance: the FastEmbed ONNX model loads on first
  # use, so a cold start costs several seconds on the first student request.
  num_instances = local.is_production ? 2 : 1
}

# -----------------------------------------------------------------------------
# Frontend
# -----------------------------------------------------------------------------
resource "render_static_site" "frontend" {
  name = local.frontend_name

  repo_url       = var.repo_url
  branch         = var.branch
  root_directory = "frontend"
  build_command  = "npm ci && npm run build"
  publish_path   = "dist"

  env_vars = {
    # Only VITE_-prefixed values reach the browser, and this is the one that
    # is meant to. No secret may ever be added here: Vite inlines these into
    # the shipped bundle.
    VITE_API_URL = { value = "https://${local.backend_name}.onrender.com" }
  }

  routes = [
    {
      type        = "rewrite"
      source      = "/*"
      destination = "/index.html"
    }
  ]
}
