resource "kubernetes_stateful_set_v1" "database" {
  metadata {
    name      = "database"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    labels    = { app = "database" }
  }

  spec {
    service_name = "database"
    replicas     = 1

    selector {
      match_labels = { app = "database" }
    }

    template {
      metadata {
        labels = { app = "database" }
      }

      spec {
        container {
          name  = "postgres"
          image = "postgres:17"

          port {
            container_port = 5432
            name           = "postgres"
          }

          # Injeção de variáveis via Secret
          env {
            name = "POSTGRES_USER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.cstrader-env.metadata[0].name
                key  = "username"
              }
            }
          }

          env {
            name = "POSTGRES_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.cstrader-env.metadata[0].name
                key  = "password"
              }
            }
          }

          env {
            name = "POSTGRES_DB"
            value_from {
              secret_key_ref {
                name = kubernetes_secret_v1.cstrader-env.metadata[0].name
                key  = "dbname"
              }
            }
          }

          volume_mount {
            name       = "postgres-data"
            mount_path = "/var/lib/postgresql/data"
          }
        }
      }
    }

    volume_claim_template {
      metadata { name = "postgres-data" }
      spec {
        access_modes = ["ReadWriteOnce"]
        resources {
          requests = { storage = "1Gi" }
        }
      }
    }
  }

  depends_on = [kubernetes_secret_v1.cstrader-env]
}