import pika
import os
import json
import time
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
RABBITMQ_QUEUE = os.environ.get('RABBITMQ_QUEUE', None)
RABBITMQ_ROUTING_KEY = os.environ.get('RABBITMQ_ROUTING_KEY', None)
SOURCE_ID = os.environ.get('SOURCE_ID', None)


credentials = pika.PlainCredentials(username='admin', password='admin')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq_node10', port=5672, credentials=credentials))
channel = connection.channel()
channel.exchange_declare(exchange='replication1', exchange_type='direct', durable=True)
result = channel.queue_declare(queue=f'{RABBITMQ_QUEUE}', durable=True)
queue_name = result.method.queue
logger.info(f"queue_name is {queue_name} \n")
channel.queue_bind(exchange='replication1', queue=queue_name, routing_key=f'{RABBITMQ_ROUTING_KEY}')

# """
#         INSERT INTO certificates (owner, common_name, serial_number, fingerprint, cert_b64, expiration_date)
#         VALUES (%s, %s, %s, %s, %s, %s);
#     """, (owner, certificate_attributes["CommonName"], certificate_attributes["SerialNumber"],
#         certificate_attributes["Fingerprint"], base64_cert, certificate_attributes["ExpirationDate"])

def handle_insert(op):
    table, data = op['table'], op['new_record']

    sql_key = ''
    sql_value = ''

    for key, value in data.items():
        sql_key = sql_key + f"'{key}',"
        sql_value = sql_value + f"'{value}',"
    
    sql_key = sql_key[:-1]
    sql_value = sql_value[:-1] 

    sql = f"""INSERT INTO {table} 
    VALUES ({sql_value});
    """
    return sql

def handle_update(op):
    table, data = op['table'], op['new_record']

    sql_key = ''
    sql_value = ''

    for key, value in data.items():
        if key != 'id':
            sql_key = sql_key + f"'{key}',"
            sql_value = sql_value + f"{key} = '{value}', "
    
    sql_key = sql_key[:-2]
    sql_value = sql_value[:-2] 

    sql = f"""UPDATE {table} 
    SET {sql_value}
    WHERE id={data['id']};
    ;
    """
    return sql

def handle_delete(op):
    table, data = op['table'], op['old_record']

    sql = f"""DELETE FROM {table} 
    WHERE id={data['id']};
    """
    return sql

def operation_handler(op):
    sql = None
    if op['operation'] == 'INSERT':
        sql = handle_insert(op)
    if op['operation'] == 'UPDATE':
        sql = handle_update(op)
    if op['operation'] == 'DELETE':
        sql = handle_delete(op)
    # we can add other operation handlers here
    return sql

def callback(channel, method, properties, body):
    op = json.loads(body.decode('utf-8'))
    logger.info(f"json operation payload is : {op} \n")
    try:
        if op['source_id'] == SOURCE_ID:
            logger.warning(f"Skip applying operation {op['operation']} from source_id {op['source_id']} to source_id {SOURCE_ID}. Reason : source and target are equal \n")
        else :
            logger.info(f"Apply operation {op['operation']} from source_id {op['source_id']} to source_id  {SOURCE_ID} \n")
            sql = operation_handler(op)
            logger.info(f"sql is : {sql} \n")
            ### Postgres 
            connection = psycopg2.connect(
            dbname="crypto",
            user="postgres",
            password="postgres",
            host="postgres",
            port="5432"
            )
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()
            cursor.execute("""SET SESSION custom_variable.source_session = 'rabbitmq';""")
            cursor.execute(sql)
            start_time = op['start_time']
            end_time = time.time()
            elapsed = round(end_time - start_time, 3)
            logger.info(f"elapsed time is {elapsed} s \n")
            logger.debug(f"sending to source_id {SOURCE_ID} wit pid {op['pid']} at start time {start_time}, end time {end_time} with elapsed time {elapsed} s \n")
            if os.path.exists("/code/rabbitmq_perf.txt"):
                if os.stat("/code/rabbitmq_perf.txt").st_size == 0:
                    with open("/code/rabbitmq_perf.txt","a") as f:
                        f.write(op['operation'])
                        f.write("\n")
            with open("/code/rabbitmq_perf.txt","a") as f:
                f.write(f"{str(elapsed)} -- {time.time()}")
                f.write("\n")
                
    except Exception as e:
        with open("/code/rabbitmq_perf_errors.txt","a") as f:
            from datetime import datetime
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{formatted_time} - {str(e)}")
            f.write("\n")
        logger.error(f"Exception : {e} \n")

try:
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
except Exception as e:
    with open("/code/rabbitmq_perf_errors.txt","a") as f:
                f.write(str(e))
                f.write("\n")
    logger.error(f"Exception : {e} \n")