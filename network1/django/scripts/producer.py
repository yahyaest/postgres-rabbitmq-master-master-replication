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
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', None)
RABBITMQ_HOST_LIST = os.environ.get('RABBITMQ_HOST_LIST', None)
rabbitmq_hosts = RABBITMQ_HOST_LIST.split(',')

try:
    postgres_connection = psycopg2.connect(
        dbname="crypto",
        user="postgres",
        password="postgres",
        # host=f"{DATABASE_HOST}",
        host="postgres",
        port="5432"
        )
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1) 


### Postgres 
postgres_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
# register a LISTEN command
cursor = postgres_connection.cursor()
cursor.execute("LISTEN certificate_notify_trigger;")

def handle_loop():
    def handle_notify():
        postgres_connection.poll()
        for notify in postgres_connection.notifies:
            payload = json.loads(notify.payload)
            payload['pid'] = notify.pid
            start_time = time.time()
            payload['start_time'] = start_time
            payload = json.dumps(payload)

            for node in rabbitmq_hosts:
                if node == RABBITMQ_HOST:
                    logger.warning(f"Skip publishing. Reason : source {RABBITMQ_HOST} and target host {node} are equal \n")
                    continue
                else:
                    logger.info(f"sending payload : {notify.payload} at pid : {notify.pid} and channel : {notify.channel} from host {RABBITMQ_HOST} to {node} \n")
                    credentials = pika.PlainCredentials(username='admin', password='admin')
                    pika_connection = pika.BlockingConnection(pika.ConnectionParameters(host=f'{node}', port=5672, credentials=credentials))
                    channel = pika_connection.channel()
                    channel.exchange_declare(exchange='replication', exchange_type='fanout', durable=True)
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