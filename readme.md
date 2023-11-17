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

## POC-V3.0

- Introduce sql session to block trigger if database operation is from rabbitmq consumer.
- Add source_id in trigger json payload function and in consumer block operation if same source_id.
- Extract sql trigger and séquence in init.sql file that execute at postgres start-up.
- Extract producer and consumer in rabbitmq-client container.
- Each producer write in all consumer except his own and each consumer write only on his database.
- Add support for UPDATE operation.
- Make rabbitmq cluster with disk mode.
- Each rabbitmq node has it's own queue and related producer/consumer communicate throug that queue.
- Add third network/VM
- Update architecture schema.
- Update perf script.
- Add perf test rapport.