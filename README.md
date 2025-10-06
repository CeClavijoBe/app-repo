My Flask App - GitOps Application
Flask application with Prometheus metrics integration, deployed using GitOps with ArgoCD.

Project Structure
app-repo/
├── app.py # Flask application with Prometheus metrics
├── requirements.txt # Python dependencies
├── Dockerfile # Container image definition
├── .dockerignore # Docker build exclusions
├── .github/
│ └── workflows/
│ └── ci-cd.yml # GitHub Actions CI/CD pipeline
├── my-app-chart/ # Helm Chart
│ ├── Chart.yaml
│ ├── values.yaml
│ └── templates/
│ ├── deployment.yaml
│ ├── service.yaml
│ ├── serviceaccount.yaml
│ ├── servicemonitor.yaml
│ └── \_helpers.tpl
└── README.md
Application Features
Endpoints
/ - Main endpoint that returns "Hello, World!"
/health - Liveness probe endpoint
/ready - Readiness probe endpoint
/metrics - Prometheus metrics endpoint
Metrics Exposed
my_requests_total - Counter: Total number of requests received by endpoint and method
request_duration_seconds - Histogram: Request duration in seconds by endpoint
active_requests - Gauge: Number of currently active requests
Local Development
Prerequisites
Python 3.11+
Docker
kubectl
Helm 3.x
Run Locally
bash

# Install dependencies

pip install -r requirements.txt

# Run the application

python app.py

# Access the application

curl http://localhost:5000
curl http://localhost:5000/metrics
Build Docker Image Locally
bash
docker build -t my-flask-app:local .
docker run -p 5000:5000 my-flask-app:local
CI/CD Pipeline
The GitHub Actions workflow automatically:

Build & Push: Builds Docker image and pushes to Docker Hub
Tag: Tags image with Git SHA and latest
Update Chart: Updates the Helm chart's values.yaml with new image tag
Commit: Commits and pushes changes back to repository
Pipeline Triggers
Push to main branch
Manual workflow dispatch
Required Secrets
Configure these secrets in your GitHub repository settings:

DOCKER_USERNAME - Docker Hub username
DOCKER_PASSWORD - Docker Hub password/token
Image Repository
Images are pushed to: ceclavijo/my-flask-app

Helm Chart
Installation
bash

# Install directly

helm install my-app ./my-app-chart

# Install with custom values

helm install my-app ./my-app-chart -f custom-values.yaml
Configuration
Key values in values.yaml:

yaml
replicaCount: 2

image:
repository: ceclavijo/my-flask-app
tag: "latest"

service:
type: ClusterIP
port: 80

resources:
limits:
cpu: 500m
memory: 256Mi
requests:
cpu: 100m
memory: 128Mi

serviceMonitor:
enabled: true # Creates VMServiceScrape for VictoriaMetrics
ServiceMonitor
The chart includes a VMServiceScrape resource for VictoriaMetrics to automatically discover and scrape metrics from the application.

GitOps Deployment
This application is deployed via ArgoCD from the infra-repo.

How it works
Developer pushes code to main branch
GitHub Actions builds and pushes Docker image
GitHub Actions updates my-app-chart/values.yaml with new image tag
ArgoCD (watching this repo) detects the change
ArgoCD automatically syncs the new version to Kubernetes
ArgoCD Application
The ArgoCD Application manifest in infra-repo points to this chart:

yaml
source:
repoURL: https://github.com/CeClavijoBe/app-repo
targetRevision: main
path: my-app-chart
Monitoring
Accessing Metrics
bash

# Port-forward to the application

kubectl port-forward svc/my-app 8080:80

# View metrics

curl http://localhost:8080/metrics
Grafana Dashboard
Metrics are automatically scraped by VictoriaMetrics and available in Grafana.

Sample PromQL queries:

promql

# Request rate

rate(my_requests_total[5m])

# Request duration p95

histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))

# Active requests

active_requests
Testing
Test Endpoints
bash

# Health check

curl http://my-app/health

# Readiness check

curl http://my-app/ready

# Generate traffic

for i in {1..100}; do curl http://my-app/; done

# Check metrics

curl http://my-app/metrics
Verify ServiceMonitor
bash

# Check if VMServiceScrape is created

kubectl get vmservicescrape

# Check if metrics are being scraped

kubectl logs -n monitoring -l app.kubernetes.io/name=vmagent | grep my-app
Troubleshooting
Application not starting
bash

# Check pod logs

kubectl logs -l app.kubernetes.io/name=my-app

# Check pod events

kubectl describe pod -l app.kubernetes.io/name=my-app
Metrics not appearing in Grafana
bash

# Verify ServiceMonitor exists

kubectl get vmservicescrape

# Check VMAgent is scraping

kubectl logs -n monitoring -l app.kubernetes.io/name=vmagent

# Test metrics endpoint directly

kubectl port-forward svc/my-app 8080:80
curl http://localhost:8080/metrics
CI/CD pipeline fails
Check GitHub Actions logs
Verify Docker Hub credentials in secrets
Ensure Git user is configured correctly
Check for merge conflicts in values.yaml
Development Workflow
Make changes to app.py
Test locally
Commit and push to main
GitHub Actions builds and deploys automatically
ArgoCD syncs changes to Kubernetes
Monitor in Grafana
Security
Application runs as non-root user (UID 1000)
Read-only root filesystem
No privilege escalation
Minimal base image (python:3.11-slim)
Security context enforced
Resources
Flask Documentation
Prometheus Python Client
Helm Documentation
ArgoCD Documentation
