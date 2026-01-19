resource "tls_private_key" "cstrader_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "cstrader_cert" {
  private_key_pem = tls_private_key.cstrader_key.private_key_pem

  subject {
    common_name  = "cstrader.local"
    organization = "CSTrader Dev"
  }

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]

  validity_period_hours = 8760
}


resource "kubernetes_secret_v1" "cstrader_tls" {
  metadata {
    name      = "cstrader-tls-secret"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  type = "kubernetes.io/tls"

  data = {
    "tls.crt" = tls_self_signed_cert.cstrader_cert.cert_pem
    "tls.key" = tls_private_key.cstrader_key.private_key_pem
  }
}