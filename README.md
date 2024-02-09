The project consists of three main services:

- **Keycloak**: An open-source Identity and Access Management securing API endpoints.
- **PostgreSQL Database**: would at some point Store Keycloak data I think
- **Minimal Flask Api**: flask api with one keycloak protected route

## Prerequisites

- Docker and Docker Compose
- Python ^3.12 (for running tests outside of Docker container) and pip with poetry
- self-signed SSL/TSL certificates for https (I think keycloak requires the api it is used with to have TSL)

## Setup Instructions

1. **Clone the Repository**

    Clone this repository to your local machine to get started.
2. **set up simulated TSL certification**
   
    ```sh
    openssl genpkey -algorithm RSA -out key.pem
    ```
    ```sh
    openssl req -new -x509 -key key.pem -out cert.pem -days 365
     ```

3. **Start the Services**

    Navigate to the project directory and run the following command to start all services:

    ```sh
    docker-compose build
    ```

    - This command builds the Flask application image ( poetry) 
    ```sh
    docker-compose up -d
    ```
    - starts the Keycloak server (`keycloak:8080`), PostgreSQL database container (not actually used), then runs the Flask api exposed with `:5000`

4. **Access Keycloak Admin Console**

    - Open a browser and navigate to `http://localhost:8080/admin`.
    - Log in using the default admin credentials (`admin` for both username and password).

5. **Confirm Keycloak realm config**

    - The `realm-config.json` is imported during the docker-compose command to set up the realm, client (idk if there is a better way to set up keycloak config stuff)

6. **Access the Flask Application**

    - The Flask application is accessible at `https://127.0.0.1:5000`.

## Testing

To run tests:

1. Ensure the Docker containers are up and running.
2. Use the provided Python test scripts to test the integration. again you will need to install the project dependencies via poetry

    ```sh
    poetry install
    ```
   
3. Execute the tests:

    ```sh
    pytest
    ```

## Key Components

- **Docker Compose File**: Orchestrates the setup of Keycloak, PostgreSQL, and the Flask api.
- **Flask api**: Demonstrates how to implement a secure route with Keycloak token authentication.
- **Keycloak realm json file**: Includes setting up realms, clients, (I wasn't able to figure out how to import the user here so i just create it with the keycloak python library)
- **Tests**: Validates the protected route's accessibility with an authenticated token.

