import logging

KEYCLOAK_URL = "http://localhost:80"
FLASK_APP_URL = "https://127.0.0.1:5000"

TEST_REALM_NAME = "test-realm"
TEST_CLIENT_ID = "test-client"
CLIENT_SECRET = "GgrHBKUSS4JpomAtQK1ex7Px8rYWywQU"
TEST_USER = "testuser"
TEST_PASS = "testpass"

logger = logging.getLogger(__name__)

def pytest_configure():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s')
