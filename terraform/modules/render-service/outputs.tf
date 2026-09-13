output "backend_service_id" {
  description = "Render service id for the API. Used by the deploy workflow."
  value       = render_web_service.backend.id
}

output "backend_url" {
  description = "Public URL of the API."
  value       = "https://${render_web_service.backend.name}.onrender.com"
}

output "frontend_service_id" {
  description = "Render service id for the static site."
  value       = render_static_site.frontend.id
}

output "frontend_url" {
  description = "Public URL of the frontend."
  value       = "https://${render_static_site.frontend.name}.onrender.com"
}
