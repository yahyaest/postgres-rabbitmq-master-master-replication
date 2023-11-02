import pika
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
channel = connection.channel()
channel.exchange_declare(exchange='replication', exchange_type='fanout')
result = channel.queue_declare(queue='certificate_queue', exclusive=True)
queue_name = result.method.queue
print("queue_name is ", queue_name)
channel.queue_bind(exchange='replication', queue=queue_name)

# """
#         INSERT INTO certificates (owner, common_name, serial_number, fingerprint, cert_b64, expiration_date)
#         VALUES (%s, %s, %s, %s, %s, %s);
#     """, (owner, certificate_attributes["CommonName"], certificate_attributes["SerialNumber"],
#         certificate_attributes["Fingerprint"], base64_cert, certificate_attributes["ExpirationDate"])

def operation_handler(op):
    def handle_insert():
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
    
    def handle_delete():
        table, data = op['table'], op['old_record']

        sql = f"""DELETE FROM {table} 
        WHERE id={data['id']};
        """
        return sql
    
    sql = None
    if op['operation'] == 'INSERT':
        sql = handle_insert()
    if op['operation'] == 'DELETE':
        sql = handle_delete()
    # we can add other operation handlers here
    return sql

def callback(channel, method, properties, body):
    op = json.loads(body.decode('utf-8'))
    print("json is : ", op)
    sql = operation_handler(op)
    print("sql is : ", sql)
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
    print("cursor is ", cursor)
    cursor.execute(sql)


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()