from datetime import datetime

current_datetime = datetime.now()
elapsed_list = []
log_file_list = ["network1/django/rabbitmq_perf.txt", "network2/django/rabbitmq_perf.txt"]
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
operation = ""
node_number = len(log_file_list)
active_consumer_number = 0

# Parse log files
index = 0
for file in log_file_list:
    with open(file,"r") as f:
        data = f.readlines()
        index = index + 1
        print(f"There is {len(data) - 1 if len(data) > 0 else len(data)} message handled by consumer {index} \n")
        for line in data:
            if "INSERT" in line or "DELETE" in line :
                operation = line.replace('\n', '')
                active_consumer_number = active_consumer_number + 1
            else:
                elapsed = float(line.replace('\n', ''))
                elapsed_list.append(elapsed)

if len(elapsed_list) > 0:
    max_elapsed_transaction = max(elapsed_list)
    moy = round(max_elapsed_transaction/len(elapsed_list), 5)

    print(f'We have {node_number} nodes with {active_consumer_number} active consumers. There is {len(elapsed_list)} {operation} messages delivered around {formatted_datetime} in the queue with average {moy} s and longest with duration of {max_elapsed_transaction} s')

    message = f'We have {node_number} nodes with {active_consumer_number} active consumers. There is {len(elapsed_list)} {operation} messages delivered around {formatted_datetime} in the queue with average {moy} s and longest with duration of {max_elapsed_transaction} s \n \n'

    with open("./rabbitmq_transactions_threading.txt","a") as f:
        f.write(message)

# Reset log files
for file in log_file_list:
    with open(file, 'w') as file:
        pass