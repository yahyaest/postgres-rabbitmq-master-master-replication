from datetime import datetime, timedelta
import json
import sys
from threading import Thread
import time
import requests
import requests.adapters




# API endpoint URL
url = "http://192.168.64.2:5000/certificates/"

data = {
    "owner":"xxx",
    "common_name":"two",
    "serial_number":"123",
    "fingerprint":"123",
    "cert_b64":"two",
    "expiration_date":"2025"
    }

headers = {}
headers['Content-Type'] = 'application/json'


# curl -X POST -H "Content-Type: application/json" -H  -d '{"owner":"two","common_name":"two","serial_number":"123","fingerprint":"123","cert_b64":"two","expiration_date":"2025"}' http://192.168.144.4:5000/certificates/

# Send POST request
payload = json.dumps(data)
responses_status = []
responses_results = []
thread_number = int(sys.argv[1]) if len(sys.argv) > 1 else 100

current_datetime = datetime.now()
current_datetime = current_datetime + timedelta(hours=1)
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=3000, pool_maxsize=1000)
# session.mount('https://', adapter)


elapsed_list= []
def task(i, payload, elapsed_list):
    payload = payload.replace("xxx", f"name_{i}")
    start_time = time.time()
    response = session.post(url, data=payload, verify=False, headers=headers)
    elapsed = round(time.time() - start_time, 3) 
    elapsed_list.append(elapsed)
    responses_status.append(response.status_code)
    responses_results.append({"status": response.status_code, "text": response.text, "duration": f"{elapsed} s"})
    print(f'thread {i} --> elapsed in {elapsed} s with status {response.status_code}')
    if response.status_code != 201:
        print(response.text)

thread_list = []
for i in range(0, thread_number):
    thread = Thread(target=task, args=[i, payload, elapsed_list])
    thread.start()
    # print(f'thread {i} --> started')
    thread_list.append(thread)

for t in thread_list:
    t.join()
    print(f'thread {t} --> joined')

max_elapsed_thread = max(elapsed_list)
moy = round(max_elapsed_thread/len(elapsed_list), 5)



print(f"{thread_number} thread were lunched at {formatted_datetime}.There are {responses_status.count(201)} posted certificates with 201 status of {len(responses_status)} threads executed elapsed in {max_elapsed_thread} s with average {moy} s")

message = f"{thread_number} thread were lunched at {formatted_datetime}.There are {responses_status.count(201)} posted certificates with 201 status of {len(responses_status)} threads executed elapsed in {max_elapsed_thread} s with average {moy} s \n \n"


with open("./certificates_threading.txt","a") as f:
    f.write(message)


with open(f"./logs/perf_api_{formatted_datetime.strip()}.json","a") as f:
    json.dump(responses_results,f, indent=4)





# /usr/local/lib/python3.11/site-packages/urllib3/connectionpool.py:1043: InsecureRequestWarning: Unverified HTTPS request is being made to host '10.30.250.30'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
#   warnings.warn(




