dev-auth:
	docker compose up auth

dev-all:
	docker compose up --build

k8s-apply:
	kubectl apply -f deploy/k8s/

k8s-delete:
	kubectl delete -f deploy/k8s/
