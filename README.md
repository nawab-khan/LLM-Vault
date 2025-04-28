# LLM Vault Deployment Guide

This README explains how to deploy and run the authenticated LLM API in a Minikube Kubernetes cluster, using Envoy as an API gateway and Auth0 for JWT-based authentication.

## Components

- **FastAPI Service** (`llm-fastapi`)
    
    - Hosts the `/predict` endpoint.
        
    - Performs inference using the Groq Python SDK and a chosen LLM (e.g., `gemma2-9b-it`).
        
- **Envoy Gateway** (`envoy-gateway`)
    
    - Validates incoming Auth0 JWTs on protected routes (`/predict`).
        
    - Forwards valid requests to the FastAPI service.
        
- **Auth0 (Identity Provider)**
    
    - Issues OAuth2-style JWTs to clients.
        
    - Envoy retrieves JWKS from Auth0 to validate tokens.
        
- **Kubernetes (Minikube)**
    
    - Orchestrates the FastAPI and Envoy deployments and services.
        

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/) installed and running
    
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured for Minikube context
    
- Docker CLI
    
- Auth0 account with a configured API and client
    
- Groq API key (exported locally as `GROQ_API_KEY`)
    

## Setup and Deployment

### 1. Configure Environment

```bash
# Start Minikube if not running
minikube start

# Configure Docker CLI to use Minikube's Docker daemon
eval $(minikube docker-env)

# Export your Groq API key (must start with 'gsk-')
export GROQ_API_KEY="gsk-..."
```

### 2. Create Kubernetes Secret

```bash
kubectl delete secret groq-api-key --ignore-not-found\# safely remove old secret
kubectl create secret generic groq-api-key \
  --from-literal=GROQ_API_KEY="$GROQ_API_KEY"
```

### 3. Build and Load Docker Image

```bash
# Build the FastAPI image in Minikube's Docker
docker build -t llm-fastapi:latest .
```

### 4. Deploy to Kubernetes

```bash
# Apply FastAPI deployment, Envoy ConfigMap & Envoy deployment
kubectl apply -f fastapi-deployment.yaml
kubectl apply -f envoy-config.yaml
kubectl apply -f envoy-deployment.yaml
```

Verify resources:

```bash
kubectl get deployments,pods,svc
```

### 5. Port-Forward Envoy

```bash
kubectl port-forward svc/envoy-gateway 8081:8081
```

## Retrieving an Auth0 Token

Before you can call the secured endpoints, you need a valid JWT from Auth0. Request one using a client‑credentials grant:

```bash
curl --request POST \
  --url https://dev-r742tubun7igvzc2.us.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id": "<YOUR_CLIENT_ID>",
    "client_secret": "<YOUR_CLIENT_SECRET>",
    "audience": "https://llm.api",
    "grant_type": "client_credentials"
}'
```

The response will include an `access_token`. Use that in the `Authorization` header:

```bash
-H "Authorization: Bearer <access_token>"
```

## Testing Endpoints

With port-forward active, use your Auth0 JWT:

- **Run inference**

    ```bash
    curl -X POST http://localhost:8081/predict \
      -H "Authorization: Bearer <YOUR_VALID_JWT>" \
      -H "Content-Type: application/json" \
      -d '{"prompt":"Hello, model!"}'
    ```


## File Structure

```
├── app/                      # FastAPI application code
│   ├── main.py
│   ├── auth.py
│   └── routes/predict.py     # Models and predict endpoints
├── Dockerfile                # Builds FastAPI container
├── requirements.txt          # Python dependencies
├── envoy.yaml                # Envoy configuration
├── fastapi-deployment.yaml   # K8s manifest for FastAPI
├── envoy-config.yaml         # ConfigMap for Envoy
├── envoy-deployment.yaml     # K8s manifest for Envoy
└── README.md                 # This guide
```
