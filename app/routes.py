from flask import Blueprint, request, jsonify
import ipaddress
import dns.resolver
from pymongo import MongoClient, DESCENDING
import os
from prometheus_client import generate_latest, Counter
import time
import datetime
import requests

# Create a Blueprint for the routes
routes = Blueprint('routes', __name__)

#env
APP_VERSION = os.getenv('APP_VERSION', '0.1.0')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://root:c67vBNh24dWE@localhost:51903/')
DB_NAME = os.getenv('DB_NAME', 'domain_lookup')
DB_NAME = os.getenv('COLLECTION_NAME', 'queries')

# MongoDB connection details with authentication
client = MongoClient(MONGO_URI)
db = client['domain_lookup']
collection = db['queries']

def cleanup():
    print("Performing cleanup...")
    client.close()
def log_query(api_name, query_param, result):
    """Logs the query details in MongoDB."""
    log_entry = {
        "timestamp": datetime.datetime.now(),
        "api_name": api_name,
        "query_param": query_param,
        "result": result
    }
    collection.insert_one(log_entry)


# /v1/tools/lookup endpoint
@routes.route('/v1/tools/lookup', methods=['GET'])
def lookup_ipv4():
    domain = request.args.get('domain')
    
    if not domain:
        result = {"error": "Please provide a domain parameter."}
        log_query("lookup_ipv4", {"domain": domain}, result)
        return jsonify(result), 400

    try:
        # Perform DNS lookup for A records (IPv4)
        answers = dns.resolver.resolve(domain, 'A')
        ipv4_addresses = [str(rdata) for rdata in answers]

        result = {"domain": domain, "ipv4_addresses": ipv4_addresses}
        log_query("lookup_ipv4", {"domain": domain}, result)
        return jsonify(result)

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout) as e:
        result = {"error": str(e)}
        log_query("lookup_ipv4", {"domain": domain}, result)
        return jsonify(result), 400

# /v1/tools/validate endpoint
@routes.route('/v1/tools/validate', methods=['GET'])
def validate_ipv4():
    ip = request.args.get('ip')
    
    if not ip:
        result = {"error": "Please provide an ip parameter."}
        log_query("validate_ipv4", {"ip": ip}, result)
        return jsonify(result), 400

    try:
        # Validate if the input is an IPv4 address
        ipaddress.IPv4Address(ip)
        result = {"ip": ip, "valid": True}
        log_query("validate_ipv4", {"ip": ip}, result)
        return jsonify(result)
    except ipaddress.AddressValueError:
        result = {"ip": ip, "valid": False}
        log_query("validate_ipv4", {"ip": ip}, result)
        return jsonify(result), 400

# /v1/history endpoint
@routes.route('/v1/history', methods=['GET'])
def get_history():
    # Retrieve the latest 20 queries, sorted by the most recent first
    history = list(collection.find().sort("_id", DESCENDING).limit(20))
    
    # Convert ObjectId to string for JSON serialization
    for entry in history:
        entry['_id'] = str(entry['_id'])

    result = history
    log_query("get_history", {}, result)
    return jsonify(history)

@routes.route('/', methods=['GET'])
def root():
    # Get current UNIX epoch time
    current_time = int(time.time())
    
    # Check if the application is running in Kubernetes
    is_kubernetes = os.getenv('KUBERNETES_SERVICE_HOST') is not None

    # Prepare the response
    response = {
        "version": APP_VERSION,
        "date": current_time,
        "kubernetes": is_kubernetes
    }
    log_query("get_APP_version", {}, response)
    return jsonify(response)

# /metrics endpoint for Prometheus
@routes.route('/metrics')
def metrics():
    return generate_latest()

# /health endpoint for health check
@routes.route('/health', methods=['GET'])
def health():
    try:
        # Attempt to connect to MongoDB and run a simple query
        client.admin.command('ping')  # This is a simple ping command to check MongoDB connection
        return jsonify({"status": "healthy"}), 200

    except Exception as e:
        # If there is an error connecting to MongoDB
        return jsonify({"status": "unhealthy", "error": str(e)}), 503