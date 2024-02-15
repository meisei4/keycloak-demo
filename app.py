from flask import Flask, jsonify, request, Blueprint
from keycloak import KeycloakOpenID
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

keycloak_openid = KeycloakOpenID(server_url="http://nginx/",
                                 client_id="test-client",
                                 realm_name="test-realm",
                                 client_secret_key="DfszfQqJ2gFh8wuda5RMPrfwdqyiQ7Ax")

api = Blueprint('api', __name__)

@api.route('/')
def index():
    logger.info('Serving the index route')
    return jsonify({'message': 'Welcome to the Flask Keycloak demo!'})

@api.route('/protected')
def protected():
    logger.info('Attempting to access protected route')
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        logger.info('Authorization header is missing')
        return jsonify({'message': 'Authorization header is missing'}), 401

    token = auth_header.split()[1]
    try:
        logger.info('Attempting to decode the token...')
        KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
        options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
        token_info = keycloak_openid.decode_token(token, key=KEYCLOAK_PUBLIC_KEY, options=options)
        logger.info(f'Token decoded successfully: {token_info}')
        return jsonify({'message': 'Access granted to protected route', 'token_info': token_info})
    except Exception as e:
        logger.error(f'Access denied due to error: {e}')
        return jsonify({'message': f'Access denied: {e}'}), 401

app.register_blueprint(api)

if __name__ == '__main__':
    app.run(ssl_context='adhoc', host='0.0.0.0', debug=True)
