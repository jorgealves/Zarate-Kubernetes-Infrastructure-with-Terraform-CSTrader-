resource "kubernetes_job_v1" "db_setup" {
  metadata {
    name      = "db-setup"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    backoff_limit = 4 
    
    ttl_seconds_after_finished = 100 

    template {
      metadata {
        labels = {
          app = "db-setup"
        }
      }

      spec {
        restart_policy = "OnFailure"

        init_container {
          name  = "wait-for-postgres"
          image = "busybox" 
          
          command = [
            "sh", 
            "-c", 
            "until nc -z database 5432; do echo 'Waiting for Postgres...'; sleep 2; done;"
          ]
        }

        container {
          name              = "migrator"
          image             = "cstrader:latest" 
          image_pull_policy = "Never"          

          env_from {
            secret_ref {
              name = kubernetes_secret_v1.cstrader-env.metadata[0].name
            }
          }
          env {
            name  = "PYTHONPATH"
            value = "/app"
          }

          command = ["/bin/sh", "-c"]
          args = [
            <<-EOT
              cd /app/backend &&
              echo "🚀 Starting Migrations..." &&
              poetry run alembic upgrade head &&
              
              echo "🌱 Seeding Admin User..." &&
              poetry run python src/initialize_admin.py &&

              echo "✅ All Done!"
            EOT
          ]
        }
      }
    }
  }

  depends_on = [
    kubernetes_service_v1.database,
    null_resource.docker_build_load
  ]
}