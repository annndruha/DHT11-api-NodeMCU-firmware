# Temperature monitor API

This is a pet project for study FastAPI and SQLAlchemy.
The goal of the project is to collect data from a temperature and humidity sensor (like DHT11) and write data to a database.
Example: [api.annndruha.space](https://api.annndruha.space/)

This repo contains **only api server**, which able to receive data from devices and manage them. (Colored at picture)

![Work scheme](https://user-images.githubusercontent.com/51162917/227819225-0682b933-3776-4597-bf75-5f4ac84b7385.png)

## Setup

### Requirements

* First of all, you need a server that will work 24/7
* You also need a permanent ip address for this server (or domain name with or permanent ip)
* Next you need database for collecting data (for example PostgreSQL docker container)

### Preparations

**Prepare database**
* Create a user `temperature_monitor` in database
* Create a schema `temperature_monitor` (schema name must be same as user)

**Write down a environment variables**

On this step you need to remember or write down special environment variables

* After user creation combine an info about user, host and database in special string named `DB_DNS`:
```dotenv
DB_DSN=postgresql://temperature_monitor:passowrd@api_or_ip_address:5432/databasename
```
* Generate any strong `ADMIN_TOKEN`. It will need to manage devices and get collected data
```dotenv
ADMIN_TOKEN=JMUW191K57OC7C4Q7Y7Q
```

### Download and launch this repo [docker container](https://github.com/annndruha/temperature-monitor-api/pkgs/container/temperature-monitor-api)
There are two different ways:

**Way 1: Using GitHub self-hosted runner**

If you have an installed  GitHub self-hosted runner, fork this repo.
Next create in repo GitHub environment with two secrets: `DB_DSN` and `ADMIN_TOKEN`

After that create on last commit tag started with `v`, for example: `v2023.03.27`.
This tag will trigger a deployment workflow `build_and_publish.yml` and all next setup steps will be performed automatically.

**Way 2: Manual**

*Download:*
```commandline
docker pull ghcr.io/annndruha/temperature-monitor-api:latest
```

*Migrate Database.* This step need to create a necessary tables inside you schema.

While doing this step this happens: A docker creates a container from image, run it, run inside container command `alembic upgrade head` and remove a container.

Instead `${{ DB_DSN }}` and `${{ ADMIN_TOKEN }}` use your variables.
```commandline
docker run \
    --rm \
    --env DB_DSN=${{ DB_DSN }} \
    --env ADMIN_TOKEN=${{ ADMIN_TOKEN }} \
    --name temperature_monitor_api_migration \
    --workdir="/" \
    ghcr.io/annndruha/temperature-monitor-api:latest \
    alembic upgrade head
```

*Run container*

Finally, run container!

> Note: depends on your configuration, `--expose` and `--publish` can be replaced with `--network`.
> Also don't forget to make sure that ports accessible from outside
```commandline
docker run \
    --detach \
    --restart always \
    --expose=443 \
    --publish 443:443 \
    --env DB_DSN='${{ DB_DSN }}' \
    --env ADMIN_TOKEN=${{ ADMIN_TOKEN }} \
    --name temperature_monitor_api \
    ghcr.io/annndruha/temperature-monitor-api:latest
```

### Usage

Almost any information about api you can file find in `/docs` section after server run.

There are two important things that need to know:

**Create device**

For using api by some device, first is need to create device itself by `POST /create_device`.
The api generate to you a *device_token*, which need to paste in every `POST /create_measurment` request from your device.

**Measurement record format**

For save disk space reason, not every measurement are recorded on a database.
It's recorded only **if temperature or humidity changes** from previous record for this device **or time since last record > 1 min**

[//]: # (If it happens, the api recorded into database are two records: 1&#41; last values of temp temperature )

[//]: # (and humidity with new timestamp 2&#41; new values with timestamp a few milliseconds later.)

[//]: # ()
[//]: # (Graphically it seems like that:)

[//]: # ()
[//]: # (<img alt="Measurement record format" width=600px src="https://user-images.githubusercontent.com/51162917/227822432-e171ecf1-9a7f-4c1a-aba2-f422f4b91017.png" />)
