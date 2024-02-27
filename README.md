
keycloak1 log:
```log
2024-02-13 11:46:09,623 INFO  [org.infinispan.CLUSTER] (Shutdown thread) ISPN000080: Disconnecting JGroups channel `ISPN`
2024-02-13 11:46:09,648 INFO  [io.quarkus] (Shutdown thread) Keycloak stopped in 0.073s
```

keycloak2 log:

```log
2024-02-13 11:46:09,584 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=authenticationSessions] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,594 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=sessions] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,598 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=clientSessions] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,601 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=work] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,603 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=org.infinispan.PERMISSIONS] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,605 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=loginFailures] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,608 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=offlineClientSessions] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,613 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=org.infinispan.ROLES] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,615 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=org.infinispan.CONFIG] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,618 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=offlineSessions] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,621 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) [Context=actionTokens] ISPN100008: Updating cache members list [5ba9978151c0-9578], topology id 21
2024-02-13 11:46:09,625 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) ISPN000094: Received new cluster view for channel ISPN: [5ba9978151c0-9578|8] (1) [5ba9978151c0-9578]
2024-02-13 11:46:09,626 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) ISPN100001: Node 0eeb92f29b3d-3460 left the cluster
2024-02-13 11:46:09,626 INFO  [org.infinispan.CLUSTER] (jgroups-22,5ba9978151c0-9578) ISPN100001: Node 0eeb92f29b3d-3460 left the cluster
```


pytest log: 
```log
[2024-02-13 20:46:08,719] [INFO] [MainThread] Obtaining token for admin...
[2024-02-13 20:46:09,364] [INFO] [MainThread] Creating Keycloak user 'testuser'...
[2024-02-13 20:46:09,490] [INFO] [MainThread] User 'testuser' created successfully.
[2024-02-13 20:46:09,491] [INFO] [MainThread] stop keycloak1 container
[2024-02-13 20:46:10,012] [INFO] [MainThread] Verifying user existence post-failover
[2024-02-13 20:46:10,012] [INFO] [MainThread] Obtaining token for admin...
[2024-02-13 20:47:10,113] [INFO] [MainThread] Test passed: User exists and is accessible even after keycloak1 failover.
[2024-02-13 20:47:10,113] [INFO] [MainThread] Obtaining token for admin...
[2024-02-13 20:47:10,155] [INFO] [MainThread] Deleting Keycloak user 'testuser'...
[2024-02-13 20:47:10,202] [INFO] [MainThread] User 'testuser' deleted successfully.
```




## Keycloak basic example

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


resources:
https://www.keycloak.org/server/all-config#_database
https://www.keycloak.org/server/configuration#_formats_for_environment_variables
https://infinispan.org/docs/stable/titles/configuring/configuring.html
https://www.keycloak.org/high-availability/introduction
https://www.keycloak.org/server/caching

https://infinispan.org/docs/stable/titles/server/server.html#discovery-tcpping_cluster-transport

https://infinispan.org/docs/stable/titles/server/server.html#using-inline-jgroups-stacks_cluster-transport

http://www.jgroups.org/manual4/index.html#TCPPING_Prot

http://www.jgroups.org/manual4/index.html#TCPPING

https://www.keycloak.org/server/hostname

https://github.com/infinispan/infinispan/blob/main/core/src/main/resources/default-configs/default-jgroups-tcp.xml

https://docs.docker.com/network/drivers/host/

https://docs.docker.com/network/network-tutorial-host/


logs for when TCPPING host is incorrect (TCP requires explicit ip for discovery, it doesnt discover beyond that provided IP)
```commandline
2024-02-27 14:16:50 2024-02-27 05:16:50,623 WARN  [org.infinispan.PERSISTENCE] (keycloak-cache-init) ISPN000554: jboss-marshalling is deprecated and planned for removal
2024-02-27 14:16:51 2024-02-27 05:16:51,475 INFO  [org.infinispan.CONTAINER] (keycloak-cache-init) ISPN000556: Starting user marshaller 'org.infinispan.jboss.marshalling.core.JBossUserMarshaller'
2024-02-27 14:16:53 2024-02-27 05:16:53,927 INFO  [org.infinispan.CLUSTER] (keycloak-cache-init) ISPN000078: Starting JGroups channel `ISPN` with stack `ian_minimal_tcp`
2024-02-27 14:16:53 2024-02-27 05:16:53,938 INFO  [org.jgroups.JChannel] (keycloak-cache-init) local_addr: 2b5f58e7-01ea-4845-87d6-d262a372084b, name: fd56c8ccb848-50546
2024-02-27 14:16:56 2024-02-27 05:16:56,996 INFO  [org.jgroups.protocols.pbcast.GMS] (keycloak-cache-init) fd56c8ccb848-50546: no members discovered after 3006 ms: creating cluster as coordinator
2024-02-27 14:16:57 2024-02-27 05:16:57,128 INFO  [org.infinispan.CLUSTER] (keycloak-cache-init) ISPN000094: Received new cluster view for channel ISPN: [fd56c8ccb848-50546|0] (1) [fd56c8ccb848-50546]
2024-02-27 14:16:58 2024-02-27 05:16:58,574 INFO  [org.infinispan.CLUSTER] (keycloak-cache-init) ISPN000079: Channel `ISPN` local address is `fd56c8ccb848-50546`, physical addresses are `[192.168.30.5:7800]`
2024-02-27 14:16:58 2024-02-27 05:16:58,657 WARN  [org.infinispan.CONFIG] (keycloak-cache-init) ISPN000569: Unable to persist Infinispan internal caches as no global state enabled
```
logs for when proper IP is set:
```commandline
2024-02-27 03:18:28,356 WARN  [org.infinispan.PERSISTENCE] (keycloak-cache-init) ISPN000554: jboss-marshalling is deprecated and planned for removal
2024-02-27 03:18:28,457 INFO  [org.infinispan.CONTAINER] (keycloak-cache-init) ISPN000556: Starting user marshaller 'org.infinispan.jboss.marshalling.core.JBossUserMarshaller'
2024-02-27 03:18:28,667 INFO  [org.infinispan.CLUSTER] (keycloak-cache-init) ISPN000078: Starting JGroups channel `ISPN` with stack `ian_minimal_tcp`
2024-02-27 03:18:28,669 INFO  [org.jgroups.JChannel] (keycloak-cache-init) local_addr: 0a239b1d-1df7-419f-b661-51af57788939, name: 4db62eccdf6d-61094
2024-02-27 03:18:28,752 INFO  [org.keycloak.broker.provider.AbstractIdentityProviderMapper] (main) Registering class org.keycloak.broker.provider.mappersync.ConfigSyncEventListener
2024-02-27 03:18:34,947 INFO  [org.infinispan.CLUSTER] (keycloak-cache-init) ISPN000094: Received new cluster view for channel ISPN: [ff1c91465345-51196|1] (2) [ff1c91465345-51196, 4db62eccdf6d-61094]
2024-02-27 03:18:34,991 INFO  [org.infinispan.CLUSTER] (keycloak-cache-init) ISPN000079: Channel `ISPN` local address is `4db62eccdf6d-61094`, physical addresses are `[192.168.30.4:7800]`
2024-02-27 03:18:35,008 WARN  [org.infinispan.CONFIG] (keycloak-cache-init) ISPN000569: Unable to persist Infinispan internal caches as no global state enabled
2024-02-27 03:18:35,147 INFO  [org.infinispan.LIFECYCLE] (jgroups-5,ISPN,4db62eccdf6d-61094) [Context=org.infinispan.PERMISSIONS] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,173 INFO  [org.infinispan.LIFECYCLE] (non-blocking-thread--p2-t5) [Context=org.infinispan.PERMISSIONS] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,193 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=org.infinispan.ROLES] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,196 INFO  [org.infinispan.LIFECYCLE] (non-blocking-thread--p2-t8) [Context=org.infinispan.ROLES] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,208 INFO  [org.infinispan.LIFECYCLE] (jgroups-11,ISPN,4db62eccdf6d-61094) [Context=org.infinispan.CONFIG] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,210 INFO  [org.infinispan.LIFECYCLE] (non-blocking-thread--p2-t14) [Context=org.infinispan.CONFIG] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,286 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=actionTokens] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,379 INFO  [org.infinispan.LIFECYCLE] (jgroups-11,ISPN,4db62eccdf6d-61094) [Context=actionTokens] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,439 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=authenticationSessions] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,442 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=authenticationSessions] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,518 INFO  [org.infinispan.LIFECYCLE] (jgroups-11,ISPN,4db62eccdf6d-61094) [Context=clientSessions] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,520 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=clientSessions] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,578 INFO  [org.infinispan.LIFECYCLE] (jgroups-11,ISPN,4db62eccdf6d-61094) [Context=loginFailures] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,581 INFO  [org.infinispan.LIFECYCLE] (jgroups-11,ISPN,4db62eccdf6d-61094) [Context=loginFailures] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,623 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=offlineClientSessions] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,626 INFO  [org.infinispan.LIFECYCLE] (jgroups-11,ISPN,4db62eccdf6d-61094) [Context=offlineClientSessions] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,687 INFO  [org.infinispan.LIFECYCLE] (jgroups-11,ISPN,4db62eccdf6d-61094) [Context=offlineSessions] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,690 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=offlineSessions] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,749 INFO  [org.infinispan.LIFECYCLE] (jgroups-11,ISPN,4db62eccdf6d-61094) [Context=sessions] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,751 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=sessions] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
2024-02-27 03:18:35,809 INFO  [org.infinispan.LIFECYCLE] (jgroups-6,ISPN,4db62eccdf6d-61094) [Context=work] ISPN100002: Starting rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], phase READ_OLD_WRITE_ALL, topology id 2
2024-02-27 03:18:35,811 INFO  [org.infinispan.LIFECYCLE] (non-blocking-thread--p2-t13) [Context=work] ISPN100010: Finished rebalance with members [ff1c91465345-51196, 4db62eccdf6d-61094], topology id 2
```

ETH blockchains study basics
- write some local smart contracts
- smart contract