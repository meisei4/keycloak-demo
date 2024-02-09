import requests
from conftest import logger, TEST_CLIENT_ID, TEST_REALM_NAME, CLIENT_SECRET, KEYCLOAK_URL, TEST_USER, TEST_PASS, \
    FLASK_APP_URL


def send_request(method, url, **kwargs):
    response = requests.request(method, url, **kwargs)
    if not response.ok:
        logger.info(f"Request failed. Status code: {response.status_code}, Response: {response.text}")
    return response

def get_token(client_id, realm_name, username, password, grant_type="password", client_secret=None):
    logger.info(f"Obtaining token for {username}...")
    payload = {
        "client_id": client_id,
        "username": username,
        "password": password,
        "grant_type": grant_type,
    }
    if client_secret:
        payload["client_secret"] = client_secret

    token_url = f"{KEYCLOAK_URL}/realms/{realm_name}/protocol/openid-connect/token"
    response = send_request("POST", token_url, data=payload)
    return response.json().get("access_token") if response.ok else None

def get_keycloak_admin_token():
    return get_token("admin-cli", "master", "admin", "admin")

def get_user_access_token(username, password):
    return get_token(TEST_CLIENT_ID, TEST_REALM_NAME, username, password, client_secret=CLIENT_SECRET)

def create_keycloak_user(admin_token, username, password):
    logger.info(f"Creating Keycloak user '{username}'...")
    headers = {"Authorization": f"Bearer {admin_token}",
               "Content-Type": "application/json"
               }
    payload = {"username": username,
               "enabled": True,
               "credentials": [{"type": "password",
                                "value": password,
                                "temporary": False}
                               ]
               }
    response = send_request("POST",
                            f"{KEYCLOAK_URL}/admin/realms/{TEST_REALM_NAME}/users",
                            headers=headers,
                            json=payload)
    return response.status_code == 201


def delete_keycloak_user(admin_token, username):
    logger.info(f"Deleting Keycloak user '{username}'...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    search_response = send_request("GET", f"{KEYCLOAK_URL}/admin/realms/{TEST_REALM_NAME}/users?username={username}",
                                   headers=headers)

    if search_response.ok:
        user_id = search_response.json()[0]['id']
        delete_response = send_request("DELETE", f"{KEYCLOAK_URL}/admin/realms/{TEST_REALM_NAME}/users/{user_id}",
                                       headers=headers)

        return delete_response.status_code in [204, 404]
    return False


def test_access_protected_route():
    admin_token = get_keycloak_admin_token()
    assert admin_token, "Failed to obtain admin token."

    user_created = create_keycloak_user(admin_token, TEST_USER, TEST_PASS)
    assert user_created, "Failed to create test user."

    try:
        access_token = get_user_access_token(TEST_USER, TEST_PASS)
        assert access_token, "Failed to obtain access token for test user."

        headers = {"Authorization": f"Bearer {access_token}"}
        protected_response = send_request("GET",
                                          f"{FLASK_APP_URL}/protected",
                                          headers=headers,
                                          verify=False)

        assert protected_response.status_code == 200, "Expected status code 200."
        assert "Access granted to protected route" in protected_response.json().get("message", ""), "Access to protected route was not granted."
        logger.info("Test passed: Access to protected route confirmed.")
    finally:
        if user_created:
            delete_keycloak_user(admin_token, TEST_USER)

