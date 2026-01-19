variable "cluster_name" {
  description = "O nome do perfil do Minikube"
  type        = string
  default     = "terraform-cstrader"
}

resource "null_resource" "docker_build_load" {
  triggers = {
    always_run = "${timestamp()}"
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    
    command = <<EOT
      docker build -f ../backend/ops/Dockerfile -t cstrader:latest ..
      docker build -f ../frontend/Dockerfile -t cstrader-frontend:latest ../frontend/

      minikube -p ${var.cluster_name} image load cstrader:latest
      minikube -p ${var.cluster_name} image load cstrader-frontend:latest
    EOT
  }

  depends_on = [minikube_cluster.docker]
}