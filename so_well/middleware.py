# so_well/middleware.py
import os
import jwt
import requests
import json
import logging
from jwt.algorithms import RSAAlgorithm
from flask import request, g, jsonify

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the Cloudflare Access JWT public keys dynamically
TEAM_DOMAIN = os.getenv("TEAM_DOMAIN")
SERVICE_TOKEN_ID = os.getenv("SERVICE_TOKEN_ID")
SERVICE_TOKEN_SECRET = os.getenv("SERVICE_TOKEN_SECRET")
POLICY_AUD = os.getenv("POLICY_AUD")

logger.debug(f"TEAM_DOMAIN: {TEAM_DOMAIN}")
logger.debug(f"SERVICE_TOKEN_ID: {SERVICE_TOKEN_ID}")
logger.debug(f"SERVICE_TOKEN_SECRET: {SERVICE_TOKEN_SECRET}")
logger.debug(f"POLICY_AUD: {POLICY_AUD}")

if not TEAM_DOMAIN:
    raise ValueError("TEAM_DOMAIN environment variable is not set")

if not SERVICE_TOKEN_ID or not SERVICE_TOKEN_SECRET:
    raise ValueError("Service token ID or secret is not set")

if not POLICY_AUD:
    raise ValueError("POLICY_AUD environment variable is not set")

HTTPS_TEAM_DOMAIN = f"https://{TEAM_DOMAIN}"
CERTS_URL = f"{HTTPS_TEAM_DOMAIN}/cdn-cgi/access/certs"
logger.debug(f"CERTS_URL: {CERTS_URL}")

def _get_public_keys():
    try:
        headers = {
            "CF-Access-Client-Id": SERVICE_TOKEN_ID,
            "CF-Access-Client-Secret": SERVICE_TOKEN_SECRET,
        }
        logger.debug(f"Requesting public keys with headers: {headers}")
        r = requests.get(CERTS_URL, headers=headers)
        r.raise_for_status()
        logger.debug("Fetched public keys successfully")
        public_keys = []
        jwk_set = r.json()
        logger.debug(f"JWK Set: {jwk_set}")
        for key_dict in jwk_set['keys']:
            public_key = RSAAlgorithm.from_jwk(json.dumps(key_dict))
            logger.debug(f"Public Key: {public_key}")
            public_keys.append(public_key)
        return public_keys
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch public keys from {CERTS_URL}: {str(e)}")
        raise RuntimeError(f"Failed to fetch public keys from {CERTS_URL}") from e

def cloudflare_auth_middleware():
    def check_auth():
        token = request.headers.get('Cf-Access-Jwt-Assertion')
        logger.debug(f"Token: {token}")
        if not token:
            logger.warning("Missing required CF authorization token")
            return jsonify({"message": "Missing required CF authorization token"}), 403

        keys = _get_public_keys()
        valid_token = False

        for key in keys:
            try:
                payload = jwt.decode(
                    token,
                    key=key,
                    algorithms=['RS256'],
                    audience=POLICY_AUD
                )
                logger.debug(f"Payload: {payload}")
                if payload.get('iss') != HTTPS_TEAM_DOMAIN:
                    logger.warning("Invalid token issuer")
                    return jsonify({"message": "Invalid token issuer"}), 403

                email = payload.get('email')
                logger.debug(f"Email: {email}")
                if email:
                    g.user_email = email
                    valid_token = True
                    break
            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired")
                return jsonify({"message": "Token has expired"}), 403
            except jwt.InvalidAudienceError:
                logger.warning("Invalid audience")
                return jsonify({"message": "Invalid audience"}), 403
            except jwt.InvalidTokenError as e:
                logger.warning(f"Invalid token error: {str(e)}")
                continue

        if not valid_token:
            logger.warning("Invalid token")
            return jsonify({"message": "Invalid token"}), 403

        logger.info("Token is valid")

    return check_auth
