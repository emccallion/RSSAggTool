# Local Network Access

The Django preprocessing service can be accessed from any device on your local network.

## Current Network Configuration

**Your Local IP:** `192.168.86.212`

**Access URLs:**
- From this computer: http://localhost:8001
- From other devices: http://192.168.86.212:8001

## Quick Start

### Option 1: Use the Helper Script (Recommended)
```bash
cd preprocessing
./start_network.sh
```

This will:
- Show your current local IP address
- Start the server on all network interfaces
- Display the URL to share with other devices

### Option 2: Manual Start
```bash
cd preprocessing
source ../venv/bin/activate
python manage.py runserver 0.0.0.0:8001
```

## Accessing from Other Devices

### From Computer/Laptop
Open a web browser and go to:
```
http://192.168.86.212:8001
```

### From Phone/Tablet
1. Connect to the same WiFi network
2. Open browser and go to: `http://192.168.86.212:8001`
3. Bookmark for easy access

### From Another Computer on the Network
Same as above - just use the IP address in any browser.

## Security Notes

⚠️ **Important:** This setup is for LOCAL NETWORK ONLY

- ✅ Safe for home/office networks
- ✅ Only accessible to devices on same WiFi/LAN
- ❌ NOT accessible from the internet (by design)
- ❌ Do NOT expose to public internet (no security hardening)

## Firewall Configuration

If you can't access from other devices, you may need to allow port 8001:

### Linux (ufw)
```bash
sudo ufw allow 8001/tcp
```

### Linux (firewalld)
```bash
sudo firewall-cmd --add-port=8001/tcp --permanent
sudo firewall-cmd --reload
```

### macOS
```bash
# Usually no firewall configuration needed
# If enabled, go to: System Preferences → Security & Privacy → Firewall
```

## Troubleshooting

**Can't access from another device?**

1. **Check same network**: Ensure all devices are on the same WiFi/LAN
2. **Check firewall**: See firewall section above
3. **Check IP address**: Run `./start_network.sh` to see current IP
4. **Restart server**: Stop and restart with `./start_network.sh`

**IP address changed?**

Your local IP may change if you:
- Restart your router
- Reconnect to WiFi
- Use DHCP instead of static IP

Just run `./start_network.sh` again to see the new IP.

## Static IP (Optional)

For consistent access, set a static IP on your router:

1. Log into your router (usually 192.168.1.1 or 192.168.0.1)
2. Find DHCP settings
3. Reserve IP for your computer's MAC address
4. Recommended: Use something like `192.168.86.100` for easy memory

## Production Deployment

For production use outside your local network, you would need:
- Proper domain name
- SSL certificate (HTTPS)
- Security hardening (disable DEBUG, set strong SECRET_KEY)
- Production WSGI server (Gunicorn/uWSGI)
- Reverse proxy (Nginx/Apache)
- Proper authentication

This is currently configured for LOCAL DEVELOPMENT ONLY.
