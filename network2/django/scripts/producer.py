import multiprocessing
import os
import sys
import json
import time
import pika
import asyncio
import uvloop
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Create a logger
# Create a logger
import logging
from colorlog import ColoredFormatter

logger = logging.getLogger(__name__)
formatter = ColoredFormatter(
    '%(log_color)s%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)
handler = logging.StreamHandler()  
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

DATABASE_HOST = os.environ.get('DATABASE_HOST', None)

try:
    postgres_connection = psycopg2.connect(
        dbname="crypto",
        user="postgres",
        password="postgres",
        # host=f"{DATABASE_HOST}",
        host="postgres2",
        port="5432"
        )
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1) 

### Postgres 
postgres_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
# register a LISTEN command
cursor = postgres_connection.cursor()

cursor.execute(f"""
    CREATE OR REPLACE FUNCTION notify_certificate_changes()
    RETURNS trigger AS
    $$
    BEGIN
        PERFORM pg_notify(
                'certificate_notify_trigger',
                json_build_object(
                        'table', TG_TABLE_NAME,
                        'operation', TG_OP,
                        'new_record', row_to_json(NEW),
                        'old_record', row_to_json(OLD),
                        'hostname', '{DATABASE_HOST}'::text
                    )::text
            );

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    DROP TRIGGER IF EXISTS certificate_notify_trigger ON certificates;
    
    CREATE TRIGGER certificate_notify_trigger
    AFTER INSERT OR UPDATE OR DELETE ON certificates
    FOR EACH ROW EXECUTE PROCEDURE notify_certificate_changes();

""")

cursor.execute("""
    CREATE SEQUENCE IF NOT EXISTS even2_id_seq START 2 INCREMENT 2;
    ALTER TABLE certificates
    ALTER COLUMN id SET DEFAULT nextval('even2_id_seq');

""")

cursor.execute("LISTEN certificate_notify_trigger;")


def handle_loop():
    def handle_notify():
        credentials = pika.PlainCredentials(username='admin', password='admin')
        pika_connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq_node20', port=5672, credentials=credentials))
        channel = pika_connection.channel()
        channel.exchange_declare(exchange='replication', exchange_type='fanout', durable=True)
        postgres_connection.poll()
        for notify in postgres_connection.notifies:
            logger.info(f"sending payload : {notify.payload} at pid : {notify.pid} from host {DATABASE_HOST} \n")
            payload = json.loads(notify.payload)
            payload['pid'] = notify.pid
            start_time = time.time()
            payload['start_time'] = start_time
            payload = json.dumps(payload)

            channel.basic_publish(exchange='replication', routing_key='crypto', body=payload)
        pika_connection.close()
        postgres_connection.notifies.clear()

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.add_reader(postgres_connection, handle_notify)
    loop.run_forever()

# Create a new process to run the notification handling and SQL insert
logger.info('[*] Waiting for database changes to be published. To exit press CTRL+C')
insert_process = multiprocessing.Process(target=handle_loop)
insert_process.start()

# import select

# while True:
#     if select.select([connection],[],[],5) == ([],[],[]):
#         logger.info("Timeout")
#     else:
#         connection.poll()
#         while connection.notifies:
#             for notify in connection.notifies:
#                 logger.info("shit")
#                 #logger.info(notify.payload)
#             # notify = connection.notifies.pop(0)
#             # logger.info(f"Got NOTIFY: {notify.pid}, {notify.channel}, {notify.payload}")

# while True:
#     select.select([connection],[],[])
#     connection.poll()
#     events = []
#     while connection.notifies:
#         notify = connection.notifies.pop().payload
#         logger.info(notify)
