# Cloudflare IP Monitor
This Python script monitors changes in Cloudflare's IPv4 and IPv6 address ranges and sends notifications via Discord webhook when changes are detected. It's designed to run continuously, checking for updates at regular intervals.
## Features

Monitors both IPv4 and IPv6 Cloudflare IP ranges
Sends notifications through Discord webhooks
Caches IP lists to efficiently detect changes
Auto-updates from the GitHub repository (optional)
Easy setup with interactive prompt for Discord webhook URL

## Requirements

Python 3.6+
Root privileges (the script needs to be run as root)

## Installation

Clone this repository:
```
git clone https://github.com/yourusername/cloudflare-ip-monitor.git
cd cloudflare-ip-monitor
```
Install the required Python packages:
```
pip install requests python-dotenv pytz tzlocal
```

## Usage

Run the script with root privileges:
```
sudo python3 cloudflare_ip_monitor.py
```
On the first run, you will be prompted to enter your Discord webhook URL. The script will validate the URL and save it to a `.env` file for future use.
The script will start monitoring Cloudflare IP ranges and send a test message to your Discord channel.
Leave the script running to continue monitoring. It will check for IP changes at regular intervals and send notifications when changes are detected.

## Configuration
The script uses the following constants that you can modify in the code:

`CLOUDFLARE_IPV4_URL`: URL for Cloudflare's IPv4 ranges
`CLOUDFLARE_IPV6_URL`: URL for Cloudflare's IPv6 ranges
`CACHE_FILE`: Filename for caching IP lists
`auto_update_enabled`: Set to `True` to enable auto-updates from the GitHub repository
`update_interval`: Time in seconds between update checks
`watchdog_interval`: Time in seconds between IP range checks

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
## License
This project is licensed under the MIT License - see the LICENSE file for details.
## Disclaimer
This script is not officially associated with Cloudflare. Use at your own risk.
