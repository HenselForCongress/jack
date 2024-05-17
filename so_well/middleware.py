# so_well/middleware.py
import os
import jwt
import requests
import json
from flask import request, g, jsonify

# Load the Cloudflare Access JWT public keys dynamically
TEAM_DOMAIN = os.getenv("TEAM_DOMAIN")
CERTS_URL = "{}/cdn-cgi/access/certs".format(TEAM_DOMAIN)
POLICY_AUD = os.getenv("POLICY_AUD")

def _get_public_keys():
    r = requests.get(CERTS_URL)
    public_keys = []
    jwk_set = r.json()
    for key_dict in jwk_set['keys']:
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
        public_keys.append(public_key)
    return public_keys

def cloudflare_auth_middleware():
    def check_auth():
        token = request.headers.get('Cf-Access-Jwt-Assertion')
        if not token:
            return jsonify({"message": "Missing required CF authorization token"}), 403
        keys = _get_public_keys()

        # Loop through the keys since we can't pass the key set to the decoder
        valid_token = False
        for key in keys:
            try:
                payload = jwt.decode(token, key=key, audience=POLICY_AUD, algorithms=['RS256'])
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
