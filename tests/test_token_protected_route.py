import requests
import subprocess
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
    if response.ok:
        logger.info(f"User '{username}' created successfully.")
        return True
    else:
        logger.error(
            f"Failed to create user '{username}'. Status code: {response.status_code}, Response: {response.text}")
        return False

def delete_keycloak_user(admin_token, username):
    logger.info(f"Deleting Keycloak user '{username}'...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    search_response = send_request("GET", f"{KEYCLOAK_URL}/admin/realms/{TEST_REALM_NAME}/users?username={username}",
                                   headers=headers)
    if search_response.ok:
        user_id = search_response.json()[0]['id']
        delete_response = send_request("DELETE", f"{KEYCLOAK_URL}/admin/realms/{TEST_REALM_NAME}/users/{user_id}",
                                       headers=headers)
        if delete_response.ok:
            logger.info(f"User '{username}' deleted successfully.")
            return True
        else:
            logger.error(
                f"Failed to delete user '{username}'. Status code: {delete_response.status_code}, Response: {delete_response.text}")
            return False
    else:
        logger.error(
            f"Failed to find user '{username}' for deletion. Status code: {search_response.status_code}, Response: {search_response.text}")
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
        assert "Access granted to protected route" in protected_response.json().get("message",
                                                                                    ""), "Access to protected route was not granted."
        logger.info("Test passed: Access to protected route confirmed.")
    finally:
        if user_created:
            logger.info("delete")
            # delete_keycloak_user(admin_token, TEST_USER)

def stop_container(container_name):
    subprocess.check_call(['docker', 'stop', container_name])

def start_container(container_name):
    subprocess.check_call(['docker', 'start', container_name])

def test_basic_failover():
    # authentification
    admin_token = get_keycloak_admin_token()
    assert admin_token, "Failed to obtain admin token."

    user_created = create_keycloak_user(admin_token, TEST_USER, TEST_PASS)
    assert user_created, "Failed to create test user."

    try:
        logger.info("stop keycloak1 container")
        stop_container("keycloak-demo-keycloak1-1")

        logger.info("Verifying user existence post-failover")
        # Get a fresh admin token since the old one might be invalid due to failover
        admin_token_refreshed = get_keycloak_admin_token()
        assert admin_token_refreshed, "Failed to obtain refreshed admin token."
        headers = {"Authorization": f"Bearer {admin_token_refreshed}"}
        user_url = f"{KEYCLOAK_URL}/admin/realms/{TEST_REALM_NAME}/users?username={TEST_USER}"
        response = requests.get(user_url, headers=headers)

        assert response.status_code == 200, "Failed to verify user existence post-failover."
        users = response.json()
        assert any(user['username'] == TEST_USER for user in users), "Test user does not exist post-failover."

        logger.info("Test passed: User exists and is accessible even after keycloak1 failover.")
    finally:
        # Cleanup: attempt to delete the test user
        if user_created:
            admin_token_refreshed = get_keycloak_admin_token()
            assert admin_token_refreshed, "Failed to obtain refreshed admin token."
            success = delete_keycloak_user(admin_token_refreshed, TEST_USER)
            assert success, "Failed to delete test user."

        # start_container("keycloak-demo-keycloak1-1")

def login_as_user(username, password, client_id):
    login_url = f"{KEYCLOAK_URL}/realms/{TEST_REALM_NAME}/protocol/openid-connect/token"
    login_response = requests.post(login_url, data={
        "username": username,
        "password": password,
        "client_id": client_id,
        "grant_type": "password",
    })
    if login_response.status_code == 200:
        return login_response.json()['access_token']
    else:
        logger.info(f"Failed to log in as user {username}. Status code: {login_response.status_code}")
        return None

def test_session_failover():
    # Obtain admin token to perform admin operations
    admin_token = get_keycloak_admin_token()
    assert admin_token, "Failed to obtain admin token."

    # Create a new user in Keycloak
    user_created = create_keycloak_user(admin_token, TEST_USER, TEST_PASS)
    assert user_created, "Failed to create test user."

    try:
        # Obtain access token for the created user
        access_token = get_user_access_token(TEST_USER, TEST_PASS)
        assert access_token, "Failed to obtain access token for test user."

        # Define headers for authorization with the obtained access token
        headers = {"Authorization": f"Bearer {access_token}"}

        # Access a protected route or resource before failover to confirm access
        userinfo_url = f"{KEYCLOAK_URL}/realms/{TEST_REALM_NAME}/account/#/"
        pre_failover_response = send_request("GET", userinfo_url, headers=headers)
        assert pre_failover_response.status_code == 200, "Could not access user info before failover."

        # Simulate failover by stopping the Keycloak container
        logger.info("Stopping keycloak1 container")
        stop_container("keycloak-demo-keycloak1-1")

        # Attempt to access the protected route again with the same access token to verify session persistence
        post_failover_response = send_request("GET", userinfo_url, headers=headers)
        assert post_failover_response.status_code == 200, "Session did not persist through failover."

        logger.info("Test passed: User session persisted and protected route access confirmed after failover.")
    finally:
        # Cleanup: Delete the test user
        if user_created:
            admin_token_refreshed = get_keycloak_admin_token()
            success = delete_keycloak_user(admin_token_refreshed, TEST_USER)
            assert success, "Failed to delete test user."

        # Optionally, restart the stopped Keycloak instance for cleanup
        # start_container("keycloak-demo-keycloak1-1")
