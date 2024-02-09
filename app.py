from flask import Flask, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from keycloak import KeycloakOpenID
import logging

# -------------------
# Logging Configuration
# -------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logger = logging.getLogger(__name__)

# -------------------
# Application and Configuration
# -------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@postgres-db/keycloak_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -------------------
# Extensions Initialization
# -------------------
db = SQLAlchemy(app)
keycloak_openid = KeycloakOpenID(server_url="http://keycloak:8080/",
                                 client_id="test-client",
                                 realm_name="test-realm",
                                 client_secret_key="GgrHBKUSS4JpomAtQK1ex7Px8rYWywQU")

# -------------------
# Database Models
# -------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash = db.Column(db.String(80))

# -------------------
# Blueprint and Routes
# -------------------
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
        options = {"verify_signature": True, "verify_aud": True, "verify_exp": True}
        token_info = keycloak_openid.decode_token(token, key=KEYCLOAK_PUBLIC_KEY, options=options)
        logger.info(f'Token decoded successfully: {token_info}')
        return jsonify({'message': 'Access granted to protected route', 'token_info': token_info})
    except Exception as e:
        logger.error(f'Access denied due to error: {e}')
        return jsonify({'message': f'Access denied: {e}'}), 401

# Register Blueprint
app.register_blueprint(api)

# -------------------
# Main Entry Point
# -------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(ssl_context='adhoc', host='0.0.0.0', debug=True)
