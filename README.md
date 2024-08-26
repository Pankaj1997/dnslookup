# DNS Lookup Service

A Flask-based microservice for DNS lookup and IP validation with MongoDB integration. Provides RESTful APIs to resolve domains, validate IPs, and log query history.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)

## Installation

### Manual Installation
```
pip install -r requirements.txt
python app.py
```

### Using Docker Compose
To start the application with Docker Compose, run:
```
cd docker-setup
docker-compose up -d
```

### Using Kubernetes & helm
Substitute appVersion and namespace in the bellow-snippet.
```
cd kubernetes-setup
helm package dnslookup-helm/
helm install dnsrelease dnslookup-<appVersion>.tgz -n <namespace>

export POD_NAME=$(kubectl get pods --namespace <namespace> -l "app.kubernetes.io/name=dnslookup,app.kubernetes.io/instance=dnsrelease" -o jsonpath="{.items[0].metadata.name}")

export CONTAINER_PORT=$(kubectl get pod --namespace iocl-uat-uat $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")

echo "Visit http://127.0.0.1:8080 to use your application"

kubectl --namespace <namespace> port-forward $POD_NAME 8080:$CONTAINER_PORT
```

## Usage
### Access the API
You can interact with the service via the following endpoints:

```
curl http://localhost:3000/v1/tools/lookup?domain=example.com
```

## API Endpoints
### / (Root)
Description: Returns the current version, date, and Kubernetes status.
Method: GET
Response:
```
{
  "version": "0.1.0",
  "date": 1663534325,
  "kubernetes": false
}
```

### /v1/tools/lookup
Description: Resolves the IPv4 addresses for the given domain.
Method: GET
Parameters:
    domain (string): The domain name to lookup.
Response:
```
{
  "domain": "example.com",
  "ipv4_addresses": ["93.184.216.34"]
}
```

### /v1/tools/validate
Description: Validates if the input is an IPv4 address.
Method: GET
Parameters:
    ip (string): The IP address to validate.
Response:
```
{
  "ip": "1.2.3.4",
  "valid": true
}
```

### /v1/history
Description: Retrieves the latest 20 saved queries from the database.
Method: GET
Response:
```
[
  {
    "_id": "60f5b9e7c4f7c23456789012",
    "timestamp": "2024-08-25T09:12:42",
    "api_name": "lookup_ipv4",
    "query_param": {"domain": "example.com"},
    "result": {"domain": "example.com", "ipv4_addresses": ["93.184.216.34"]}
  },
  ...
]

```
### /metrics
Description: Provides Prometheus metrics.
Method: GET


### /health
Description: Checks MongoDB connectivity.
Method: GET
Response:
```
{
  "status": "healthy"
}
```

## Configuration
The following environment variables are used:

MONGO_URI: The URI for connecting to MongoDB.
DB_NAME: The name of the MongoDB database.
COLLECTION_NAME: The name of the MongoDB collection.
APP_VERSION: The version of the application.

