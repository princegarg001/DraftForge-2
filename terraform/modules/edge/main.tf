terraform {
  required_version = ">= 1.9.0"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.40"
    }
  }
}

variable "zone_id" {
  type = string
}

variable "environment" {
  type = string
}

variable "api_hostname" {
  description = "Hostname for the API, e.g. api.draftforge.app"
  type        = string
}

variable "app_hostname" {
  description = "Hostname for the frontend, e.g. app.draftforge.app"
  type        = string
}

variable "render_backend_host" {
  description = "Render-assigned hostname for the API service."
  type        = string
}

variable "render_frontend_host" {
  description = "Render-assigned hostname for the static site."
  type        = string
}

# -----------------------------------------------------------------------------
# DNS. Proxied so Cloudflare terminates TLS and the WAF rules below actually
# see the traffic - an unproxied record bypasses all of it.
# -----------------------------------------------------------------------------
resource "cloudflare_record" "api" {
  zone_id = var.zone_id
  name    = var.api_hostname
  content = var.render_backend_host
  type    = "CNAME"
  proxied = true
  comment = "DraftForge API (${var.environment}) - managed by Terraform"
}

resource "cloudflare_record" "app" {
  zone_id = var.zone_id
  name    = var.app_hostname
  content = var.render_frontend_host
  type    = "CNAME"
  proxied = true
  comment = "DraftForge frontend (${var.environment}) - managed by Terraform"
}

# -----------------------------------------------------------------------------
# Edge rate limiting.
#
# The application's Redis limiter is per-user and precise; this is the blunt
# layer in front of it. It matters because the application limiter still costs
# a worker, a Redis round trip and a Supabase auth lookup per request - an edge
# rule rejects a flood before any of that happens.
# -----------------------------------------------------------------------------
resource "cloudflare_ruleset" "rate_limit" {
  zone_id = var.zone_id
  name    = "draftforge-${var.environment}-rate-limit"
  kind    = "zone"
  phase   = "http_ratelimit"

  rules {
    description = "Throttle credential endpoints"
    expression  = "(http.request.uri.path contains \"/api/v1/auth/\" or http.request.uri.path contains \"/api/v1/invitations/\")"
    action      = "block"

    ratelimit {
      characteristics     = ["ip.src", "cf.colo.id"]
      period              = 60
      requests_per_period = 20
      mitigation_timeout  = 600
    }
  }

  rules {
    description = "Throttle inference endpoints"
    expression  = "(http.request.uri.path contains \"/api/v1/chat/\" or http.request.uri.path contains \"/api/v1/ai/\")"
    action      = "block"

    ratelimit {
      characteristics     = ["ip.src", "cf.colo.id"]
      period              = 60
      requests_per_period = 60
      mitigation_timeout  = 300
    }
  }
}

# -----------------------------------------------------------------------------
# WAF
# -----------------------------------------------------------------------------
resource "cloudflare_ruleset" "waf" {
  zone_id = var.zone_id
  name    = "draftforge-${var.environment}-waf"
  kind    = "zone"
  phase   = "http_request_firewall_custom"

  rules {
    description = "Managed rules"
    expression  = "true"
    action      = "execute"

    action_parameters {
      id = "efb7b8c949ac4650a09736fc376e9aee" # Cloudflare Managed Ruleset
    }
  }

  rules {
    description = "Block requests with no user agent"
    expression  = "(http.user_agent eq \"\")"
    action      = "block"
  }
}

output "api_url" {
  value = "https://${var.api_hostname}"
}

output "app_url" {
  value = "https://${var.app_hostname}"
}
