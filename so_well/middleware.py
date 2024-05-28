# so_well/middleware.py
import os
import jwt
import requests
import json
from flask import request, g, jsonify

# Load the Cloudflare Access JWT public keys dynamically
TEAM_DOMAIN = os.getenv("TEAM_DOMAIN")
SERVICE_TOKEN_ID = os.getenv("SERVICE_TOKEN_ID")
SERVICE_TOKEN_SECRET = os.getenv("SERVICE_TOKEN_SECRET")

if not TEAM_DOMAIN:
    raise ValueError("TEAM_DOMAIN environment variable is not set")

if not SERVICE_TOKEN_ID or not SERVICE_TOKEN_SECRET:
    raise ValueError("Service token ID or secret is not set")

CERTS_URL = f"{TEAM_DOMAIN}/cdn-cgi/access/certs"

def _get_public_keys():
    try:
        headers = {
            "CF-Access-Client-Id": SERVICE_TOKEN_ID,
            "CF-Access-Client-Secret": SERVICE_TOKEN_SECRET,
        }
        r = requests.get(CERTS_URL, headers=headers)
        r.raise_for_status()
        public_keys = []
        jwk_set = r.json()
        for key_dict in jwk_set['keys']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
            public_keys.append(public_key)
        return public_keys
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch public keys from {CERTS_URL}") from e

def cloudflare_auth_middleware():
    def check_auth():
        token = request.headers.get('Cf-Access-Jwt-Assertion')
        if not token:
            return jsonify({"message": "Missing required CF authorization token"}), 403

        keys = _get_public_keys()
        valid_token = False

        for key in keys:
            try:
                payload = jwt.decode(token, key=key, algorithms=['RS256'])
                # Optional: Check the issuer ('iss') field matches your Cloudflare team domain
                if payload.get('iss') != TEAM_DOMAIN:
                    return jsonify({"message": "Invalid token issuer"}), 403

                email = payload.get('email')
                if email:
                    g.user_email = email
                    valid_token = True
                    break
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token has expired"}), 403
            except jwt.InvalidTokenError:
                continue

        if not valid_token:
            return jsonify({"message": "Invalid token"}), 403

    return check_auth
