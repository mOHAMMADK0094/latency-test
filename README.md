# Latency-Test

This is a simple service which provides testing latency in services like Nats, Redis and Postgres, it also tests the availability of server and the time needed for TCP connections then exports metrics for prometheus.

### ENV vars needed for internal server
- REDIS_HOST
- REDIS_PORT
- NATS_HOST
- NATS_PORT
- DB_HOST
- DB_NAME
- DB_PORT
- DB_USER
- DB_PASSWORD

### ENV vars needed for external server
- M_INSTANCE: The server name which you are running external app.
- DISCORD_WEBHOOK : Webhook of the discord channel to send errors.
- TEST_HOST : The internal server's IP address.
- TEST_HOST_PORT : The internal server's port for checking TCP connections.

Note: The Internal server listens on `8000` and the External server listens on `8900` by default.

## How to use
- Run internal server inside your infrastructure.
- Run external server on another server outside of your datacenter to check network connectivity from outside.

#### Adding to prometheus
- Add `EXTERNAL_SERVER_IP:8900/metrics` to Prometheus scrape config.
- Set scrape_timeout to minimum `30s`.

