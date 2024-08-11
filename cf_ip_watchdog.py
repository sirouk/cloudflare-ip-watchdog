import os
import argparse
current_pid = os.getpid()
import requests
import subprocess

import datetime
import time
subprocess.run(["python3", "-m", "pip", "install", "pytz"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
import pytz
subprocess.run(["python3", "-m", "pip", "install", "tzlocal"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
from tzlocal import get_localzone

import re
import sys

# for discord bot
subprocess.run(["python3", "-m", "pip", "install", "python-dotenv"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
from dotenv import load_dotenv
import socket
import hashlib
import json


# Constants
CLOUDFLARE_IPV4_URL = "https://www.cloudflare.com/ips-v4"
CLOUDFLARE_IPV6_URL = "https://www.cloudflare.com/ips-v6"
CACHE_FILE = "cloudflare_ip_cache.json"

# Updates
auto_update_enabled = True
update_interval = 3600  # Time in seconds check for updates (3600 sec = 1 hr)

# Uptime
watchdog_interval = 120 # Time in seconds to check for liveness

# Comms
discord_mention_code = '<@&1203050411611652156>' # You can get this by putting a \ in front of a mention and sending a message in discord GUI client


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the .env file
env_file = os.path.join(script_dir, '.env')


def initialize_env_file(env_file_path):
    if os.path.exists(env_file_path):
        load_dotenv(env_file_path)
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if webhook_url and webhook_url != 'your_webhook_url_here':
            print(f"Existing webhook URL found in {env_file_path}")
            return

    print("Discord webhook URL is required to run this script.")
    webhook_url = input("Please enter your Discord webhook URL: ").strip()

    while not webhook_url.startswith("https://discord.com/api/webhooks/"):
        print("Invalid webhook URL. It should start with 'https://discord.com/api/webhooks/'")
        webhook_url = input("Please enter a valid Discord webhook URL: ").strip()

    with open(env_file_path, 'w') as f:
        f.write(f'DISCORD_WEBHOOK_URL={webhook_url}\n')
    
    print(f"Webhook URL has been saved to {env_file_path}")


def validate_webhook(webhook_url):
    try:
        response = requests.post(webhook_url, json={"content": "Cloudflare IP Monitor: Webhook test"})
        if response.status_code == 204:
            print("Webhook test successful!")
            return True
        else:
            print(f"Webhook test failed. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing webhook: {str(e)}")
        return False


def get_host_ip(api_token=None):
    headers = {'Authorization': f'Bearer {api_token}'} if api_token else {}
    try:
        response = requests.get('https://ipinfo.io', headers=headers)
        ip_info = response.json()
        IP = ip_info['ip']
    except Exception as e:
        print(f"Error getting IP information: {e}")
        IP = '127.0.0.1'
    return IP


def get_system_uptime():
    try:
        result = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error getting system uptime: {e}"


def report_for_duty(message_topic, message_contents, webhook_url):
    # Message content
    host_ip = get_host_ip()
    host_name = socket.gethostname() 
    os.chdir(os.path.dirname(__file__))
    commit_before_pull = get_latest_commit_hash()
    system_uptime = get_system_uptime()

    if len(message_contents) > 2000:
        # Post lengthy message to dpaste and get the link
        dpaste_content = message_contents
        dpaste_link = post_to_dpaste(dpaste_content)
        message = f"# :saluting_face: _reporting for duty!_\n" + \
                  f"**Host Name:** {host_name}\n" + \
                  f"**Host IP:** {host_ip}\n" + \
                  f"**Commit Hash:** {commit_before_pull}\n" + \
                  f"**System Uptime:** {system_uptime}\n" + \
                  f"**Clouflare IPv4 & IPv6 Details:**\n\n{dpaste_link}"
    else:
        message = f"# :saluting_face: _reporting for duty!_\n" + \
                  f"**Host Name:** {host_name}\n" + \
                  f"**Host IP:** {host_ip}\n" + \
                  f"**Commit Hash:** {commit_before_pull}\n" + \
                  f"**System Uptime:** {system_uptime}\n" + \
                  f"**{message_topic} Details:**\n\n{message_contents}"

    data = {
        "content": message,
        "username": host_ip
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Message sent successfully")
    else:
        print(f"Failed to send message, status code: {response.status_code}")


def post_to_dpaste(content, lexer='python', expires='2592000', format='url'):

    # dpaste API endpoint
    api_url = 'https://dpaste.org/api/'

    # Data to be sent to dpaste
    data = {
        'content': content,
        'lexer': lexer,
        'expires': expires,
        'format': format,
    }

    # Make the POST request
    response = requests.post(api_url, data=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the URL of the snippet
        return response.text.strip()  # Strip to remove any extra whitespace/newline
    else:
        # Return an error message or raise an exception
        return "Failed to create dpaste snippet. Status code: {}".format(response.status_code)


def get_latest_commit_hash():
    """Function to get the latest commit hash."""
    result = subprocess.run(["git", "log", "-1", "--format=%H"], capture_output=True, text=True)
    return result.stdout.strip()


def check_for_updates():
    os.chdir(os.path.dirname(__file__))
    commit_before_pull = get_latest_commit_hash()
    subprocess.run(["git", "pull"], check=True)
    commit_after_pull = get_latest_commit_hash()

    if commit_before_pull != commit_after_pull:
        print("Updates pulled, exiting...")
        exit(0)
    else:
        print("No updates found, continuing...")
        return time.time()


def fetch_cloudflare_ips(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip().split('\n')
    else:
        raise Exception(f"Failed to fetch IPs from {url}")


def calculate_hash(data):
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {'ipv4': {'ips': [], 'hash': ''}, 'ipv6': {'ips': [], 'hash': ''}}


def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)


def check_cloudflare_ips(webhook_url):
    cache = load_cache()
    
    ipv4_ips = fetch_cloudflare_ips(CLOUDFLARE_IPV4_URL)
    ipv6_ips = fetch_cloudflare_ips(CLOUDFLARE_IPV6_URL)
    
    ipv4_hash = calculate_hash(ipv4_ips)
    ipv6_hash = calculate_hash(ipv6_ips)
    
    changes = []
    
    if ipv4_hash != cache['ipv4']['hash']:
        changes.append("IPv4")
        cache['ipv4']['ips'] = ipv4_ips
        cache['ipv4']['hash'] = ipv4_hash
    
    if ipv6_hash != cache['ipv6']['hash']:
        changes.append("IPv6")
        cache['ipv6']['ips'] = ipv6_ips
        cache['ipv6']['hash'] = ipv6_hash
    
    if changes:
        save_cache(cache)
        message = f"Cloudflare IP changes detected for: {', '.join(changes)}\n\n"
        message += f"IPv4 IPs:\n{', '.join(ipv4_ips)}\n\n"
        message += f"IPv6 IPs:\n{', '.join(ipv6_ips)}"
        report_for_duty("Cloudflare IP Changes", message, webhook_url)



def main():
    
    if not os.geteuid() == 0:
        sys.exit("\nOnly root can run this script\n")


    # Load .env file, or initialize it if it doesn't exist
    initialize_env_file(env_file)
    load_dotenv(env_file)
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    if not validate_webhook(webhook_url):
        print("Failed to validate the webhook. Please check your URL and try again.")
        exit(1)
        

    # Check Updates
    if auto_update_enabled:
        update_start_time = check_for_updates()

    # Initialize start time
    watchdog_liveness = time.time()
    
    if not webhook_url or webhook_url == 'your_webhook_url_here':
        print("Webhook URL is not set in .env file. Exiting.")
        exit(1)

    # Check in with admins
    report_for_duty("Script Started", "Cloudflare IP monitor script has started.", webhook_url)
    

    # Commands for system setup commented out for brevity
    while True:
        try:
            

            # Liveness
            if time.time() - watchdog_liveness >= watchdog_interval:

                # Uptime liveness check
                check_cloudflare_ips(cloudflare_ipv4)
                check_cloudflare_ips(cloudflare_ipv6)

                watchdog_liveness = time.time()

            # Updates
            if auto_update_enabled and time.time() - update_start_time >= update_interval:
                update_start_time = check_for_updates()

            time.sleep(60)
        except Exception as e:
            report_for_duty("Error", f"An error occurred in the Cloudflare IP monitor script: {str(e)}", webhook_url)


if __name__ == "__main__":
    main()
