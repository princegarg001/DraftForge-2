terraform {
  required_version = ">= 1.9.0"

  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.7"
    }
  }
}

variable "environment" {
  type = string
}

variable "stack_slug" {
  description = "Grafana Cloud stack slug."
  type        = string
}

variable "dashboard_dir" {
  description = "Path to the version-controlled dashboard JSON."
  type        = string
}

variable "alert_contact_email" {
  description = "Where alert notifications are delivered."
  type        = string
}

variable "notification_severities" {
  description = "Alert severities that page someone."
  type        = list(string)
  default     = ["critical"]
}

locals {
  # Dashboards are read from the same files the local stack provisions, so
  # local and production cannot drift into showing different things.
  dashboards = fileset(var.dashboard_dir, "*.json")
}

# -----------------------------------------------------------------------------
# Dashboards
# -----------------------------------------------------------------------------
resource "grafana_dashboard" "draftforge" {
  for_each = local.dashboards

  config_json = file("${var.dashboard_dir}/${each.value}")
  folder      = grafana_folder.draftforge.uid
  overwrite   = true
}

resource "grafana_folder" "draftforge" {
  title = "DraftForge · ${title(var.environment)}"
}

# -----------------------------------------------------------------------------
# Notifications
# -----------------------------------------------------------------------------
resource "grafana_contact_point" "email" {
  name = "draftforge-${var.environment}-email"

  email {
    addresses               = [var.alert_contact_email]
    single_email            = false
    disable_resolve_message = false # knowing an alert cleared matters as much as knowing it fired
  }
}

resource "grafana_notification_policy" "default" {
  contact_point = grafana_contact_point.email.name
  group_by      = ["alertname", "severity"]

  # Batches a burst of related alerts into one notification rather than a
  # dozen; a broad outage should not produce a dozen separate pages.
  group_wait      = "45s"
  group_interval  = "5m"
  repeat_interval = "4h"

  policy {
    matcher {
      label = "severity"
      match = "="
      value = "critical"
    }
    contact_point   = grafana_contact_point.email.name
    group_wait      = "10s"
    repeat_interval = "1h"
  }
}

output "folder_uid" {
  value = grafana_folder.draftforge.uid
}

output "dashboard_count" {
  value = length(local.dashboards)
}
