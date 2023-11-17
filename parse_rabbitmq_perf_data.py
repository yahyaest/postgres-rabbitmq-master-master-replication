from datetime import datetime

current_datetime = datetime.now()
elapsed_list = []
start_at_list = []
log_file_list = ["network1/rabbitmq_client/rabbitmq_perf.txt", "network2/rabbitmq_client/rabbitmq_perf.txt","network3/rabbitmq_client/rabbitmq_perf.txt"]
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
        # sum_operation = 0
        print(f"There is {len(data) - 1 if len(data) > 0 else len(data)} message handled by consumer {index} \n")
        for line in data:
            if "INSERT" in line or "DELETE" in line or "UPDATE" in line :
                operation = line.replace('\n', '')
                active_consumer_number = active_consumer_number + 1
            else:
                line_data = line.split('--')
                elapsed = float(line_data[0].replace('\n', ''))
                started_at = float(line_data[1].replace('\n', ''))
                start_at_list.append(started_at)
                elapsed_list.append(elapsed)
                # sum_operation = sum_operation + elapsed

if len(elapsed_list) > 0 and len(start_at_list) > 0:
    # full_time = start_at_list[len(start_at_list) - 1] - start_at_list[0]
    full_time = max(start_at_list) - min(start_at_list)
    max_elapsed_transaction = max(elapsed_list)
    moy = round(full_time/len(elapsed_list), 5)

    print(f'We have {node_number} nodes with {active_consumer_number} active consumers. There is {len(start_at_list)} {operation} messages delivered around {formatted_datetime} in the queue with average {moy} s and longest with duration of {full_time} s')

    message = f'We have {node_number} nodes with {active_consumer_number} active consumers. There is {len(start_at_list)} {operation} messages delivered around {formatted_datetime} in the queue with average {moy} s and longest with duration of {full_time} s \n \n'

    with open("./rabbitmq_transactions_threading.txt","a") as f:
        f.write(message)

# Reset log files
for file in log_file_list:
    with open(file, 'w') as file:
        pass