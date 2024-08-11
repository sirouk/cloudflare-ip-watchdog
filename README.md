# Cloudflare IP Monitor
This Python script monitors changes in Cloudflare's IPv4 and IPv6 address ranges and sends notifications via Discord webhook when changes are detected. It's designed to run continuously, checking for updates at regular intervals.
## Features

Monitors both IPv4 and IPv6 Cloudflare IP ranges
Sends notifications through Discord webhooks
Caches IP lists to efficiently detect changes
Auto-updates from the GitHub repository (optional)
Easy setup with interactive prompt for Discord webhook URL
Can be run as a background service using PM2 with log rotation

## Requirements

Python 3.6+
Node.js and npm (for PM2 installation)

## Installation

Clone this repository:
```
git clone https://github.com/yourusername/cloudflare-ip-monitor.git
cd cloudflare-ip-monitor
```
Install the required Python packages:
```
pip install -r requirements.txt
```
Install PM2 globally:
```
npm install -g pm2
```

## Usage
### Running manually

Run the script:
```
python3 cf_ip_watchdog.py
```
On the first run, you will be prompted to enter your Discord webhook URL. The script will validate the URL and save it to a `.env` file for future use.

### Running as a PM2 service

Start the PM2 service:
```
pm2 start "python3 cf_ip_watchdog.py" --name "cloudflare-ip-watchdog"
pm2 save --force
```
Set up PM2 Logrotate:
```
Install pm2-logrotate module
pm2 install pm2-logrotate
Set maximum size of logs to 50M before rotation
pm2 set pm2-logrotate:max_size 50M
Retain 10 rotated log files
pm2 set pm2-logrotate:retain 10
Enable compression of rotated logs
pm2 set pm2-logrotate:compress true
Set rotation interval to every 6 hours
pm2 set pm2-logrotate:rotateInterval '00 */6 * * *'
```
To view logs:
```
pm2 logs cloudflare-ip-watchdog
```
To stop the service:
```
pm2 stop cloudflare-ip-watchdog
```
To restart the service:
```
pm2 restart cloudflare-ip-watchdog
```

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
