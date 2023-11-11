# Database HA Actif/Actif replication with RabbitMQ Cluster

## POC-V1.0

- Create 2 docker networks, each network contain postgres, rabbitmq, django and front services.
- Postgres database 'crypto' contains only one table 'certificates'.
- Add publisher and consumer scripts within django service. Publisher script contains trigger and sequence sql commands.
- Each publisher send message to consumer of others networks.

## POC-V2.0

- Implement rabbitmq cluster.
- Each publisher send message to consumer of the same network and the rabbitmq cluster.
- Introduce block circular replication mechanism that use DB hostname and sql command to check data existance.
- Develop API and RabbitMQ perf script.
