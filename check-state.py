import requests
from colorama import Fore, Style
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

token = 'YOUR_TOKEN'

def send_request(device_id):
    url = f'https://api.io.solutions/v1/io-explorer/devices/{device_id}/summary'
    headers = {"Token": token}
    response = requests.get(url, headers=headers)
    return device_id, response

def choose_group():
    groups = list(set([server["group"] for server in data]))
    groups.append("all")
    groups.sort()
    
    print("Select group:")
    for i, group in enumerate(groups):
        print(f"{i+1}. {group}")
    
    choice = input("Enter group number: ")
    if choice == "0":
        return None
    elif choice == str(len(groups)):
        return "all"
    elif choice.isdigit() and int(choice) <= len(groups):
        return groups[int(choice)-1]
    else:
        print("Invalid choice. Please try again.")
        return choose_group()

executor = ThreadPoolExecutor(max_workers=10)

device_ids = []

# Read device IDs from JSON file
with open('servers.json', 'r') as file:
    data = json.load(file)
    for device in data:
        device_ids.append(device['device_id'])

# Filter device IDs by group
group = choose_group()
if group is not None and group != "all":
    device_ids = [device['device_id'] for device in data if device['group'] == group]

futures = []

for device_id in device_ids:
    future = executor.submit(send_request, device_id)
    futures.append(future)

for future in as_completed(futures):
    device_id, response = future.result()

    if response.status_code == 200:
        response_json = response.json()

        if 'data' in response_json:
            status = response_json['data']['status']
            status_duration = response_json['data']['status_duration']

            print(f"Device ID: {device_id}")

            if status == "up":
                print(f"Status: {Fore.GREEN}Running{Style.RESET_ALL}")
            elif status == "down":
                device = next((device for device in data if device['device_id'] == device_id), None)
                if device:
                    device_name = device['device_name']
                    group = device['group']
                    print(f"Status: {Fore.RED}{status}{Style.RESET_ALL}")
                    print(f"Device Name: {device_name}")
                    print(f"Group: {group}")
                else:
                    print(f"Status: {Fore.RED}{status}{Style.RESET_ALL}")
            else:
                print(f"Status: {Fore.YELLOW}{status}{Style.RESET_ALL}")

            if status_duration:
                print(f"Status Duration: {status_duration}")

            print()
        else:
            print(f"Device ID: {device_id}\n{response_json}\n")
    else:
        print(f"Device ID: {device_id}\nError: API request failed with status code {response.status_code}\n")