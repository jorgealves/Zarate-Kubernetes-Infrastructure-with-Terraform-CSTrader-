# --- Variáveis ---
CLUSTER_NAME = terraform-cstrader
TF_VARS = -var-file env.tfvars

# Ficheiros de output dos planos
PLAN_CLUSTER = cluster.plan
PLAN_APP = app.plan

.PHONY: init plan-cluster apply-cluster images plan-app apply-app start_terraform clean

init:
	terraform init

plan:
	@echo "🔍 Planning Kubernetes App resources..."
	terraform plan -out=$(PLAN_APP) $(TF_VARS)

# Aplica o plano da aplicação
apply: plan
	@echo "🚀 Deploying App to Kubernetes..."
	terraform apply $(PLAN_APP)



ingress-ip:
	@echo "🔧 To access the app, add this to your host's /etc/hosts file:"
	@IP=$$(minikube ip -p $(CLUSTER_NAME)); \
	grep -qxF "$$IP cstrader.local" /etc/hosts || \
	echo "$$IP cstrader.local" | sudo tee -a /etc/hosts > /dev/null

test-ingress:
	@echo "🌐 Testing Ingress access..."
	curl -v https://cstrader.local --insecure

sleep:
	@echo "⏳ Waiting for resources to stabilize..."
	sleep 15

start_terraform: init apply ingress-ip sleep test-ingress
	@echo "✅ CSTrader deployed!"


clean:
	@echo "🧹 Destroying Terraform resources..."
	terraform destroy -auto-approve $(TF_VARS) || true
	@echo "🗑️ Deleting Minikube cluster..."
	minikube delete -p $(CLUSTER_NAME) || true
	@echo "🧽 Cleaning local Terraform files..."
	rm -rf .terraform
	rm -f *.tfstate
	rm -f *.tfstate.backup
	rm -f *.plan
	rm -f .terraform.lock.hcl
	docker rmi cstrader:latest || true
	@echo "🧹 Cleaning Kubernetes webhooks..."
	kubectl delete -A ValidatingWebhookConfiguration ingress-nginx-admission || true
