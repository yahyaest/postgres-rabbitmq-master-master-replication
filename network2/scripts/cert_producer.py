import multiprocessing
import pika
import asyncio
import uvloop
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

postgres_connection = psycopg2.connect(
    dbname="crypto",
    user="postgres",
    password="postgres",
    host="postgres2",
    port="5432"
    )

### Postgres 
postgres_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
# register a LISTEN command
cursor = postgres_connection.cursor()

cursor.execute("""
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
                        'old_record', row_to_json(OLD)
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

cursor.execute("LISTEN certificate_notify_trigger;")


def handle_loop():
    def handle_notify():
        pika_connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.17.0.6', port=5672))
        channel = pika_connection.channel()
        channel.exchange_declare(exchange='replication', exchange_type='fanout')
        postgres_connection.poll()
        for notify in postgres_connection.notifies:
            print(notify.payload)
            print('*************************************')
            channel.basic_publish(exchange='replication', routing_key='certificate_queue', body=notify.payload)
            print(" [x] Sent notification payload")
        pika_connection.close()
        postgres_connection.notifies.clear()

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.add_reader(postgres_connection, handle_notify)
    loop.run_forever()

# Create a new process to run the notification handling and SQL insert
insert_process = multiprocessing.Process(target=handle_loop)
insert_process.start()

# import select

# while True:
#     if select.select([connection],[],[],5) == ([],[],[]):
#         print("Timeout")
#     else:
#         connection.poll()
#         while connection.notifies:
#             for notify in connection.notifies:
#                 print("shit")
#                 #print(notify.payload)
#             # notify = connection.notifies.pop(0)
#             # print(f"Got NOTIFY: {notify.pid}, {notify.channel}, {notify.payload}")

# while True:
#     select.select([connection],[],[])
#     connection.poll()
#     events = []
#     while connection.notifies:
#         notify = connection.notifies.pop().payload
#         print(notify)
