# Detailed Setup Guide

This guide provides step-by-step instructions for setting up Telemon.

## Prerequisites

- A server with Prometheus and (optionally) Grafana running
- Docker and Docker Compose (recommended) or Python 3.11+
- A Telegram account

## Step 1: Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send the command `/newbot`
3. Follow the instructions:
   - Choose a name for your bot (e.g., "My Server Monitor")
   - Choose a username (must end in 'bot', e.g., "myserver_monitor_bot")
4. Save the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Optional: Set a description and profile picture using `/setdescription` and `/setuserpic`

## Step 2: Get Your Telegram User ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send `/start` to the bot
3. Note your user ID (a number like `123456789`)

## Step 3: Configure the Bot

### Option A: Docker Setup (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd telemon
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   nano .env
   ```

3. Edit `.env` with your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   PROMETHEUS_URL=http://prometheus:9090
   GRAFANA_URL=http://grafana:3000
   ```

4. Edit `config/config.yaml` and add your user ID:
   ```yaml
   telegram:
     authorized_users:
       - 123456789  # Replace with your Telegram user ID
   ```

5. Start the bot:
   ```bash
   docker-compose up -d
   ```

6. Check logs:
   ```bash
   docker-compose logs -f
   ```

### Option B: Python Virtual Environment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd telemon
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file and configure as in Option A

5. Run the bot:
   ```bash
   python src/main.py
   ```

## Step 4: Configure Prometheus Alertmanager

1. Edit your Alertmanager configuration (usually `alertmanager.yml`):
   ```yaml
   route:
     receiver: 'telegram-bot'

   receivers:
     - name: 'telegram-bot'
       webhook_configs:
         - url: 'http://telegram-bot:9119/alerts'
           send_resolved: true
   ```

2. If running the bot outside Docker, use:
   ```yaml
   - url: 'http://localhost:9119/alerts'
   ```

3. Reload Alertmanager configuration:
   ```bash
   # If using Docker
   docker exec alertmanager kill -HUP 1

   # If using systemd
   sudo systemctl reload alertmanager
   ```

## Step 5: Configure Prometheus Alert Rules (Optional)

1. Create alert rules file (see `config/prometheus-rules-example.yml`)

2. Add to your `prometheus.yml`:
   ```yaml
   rule_files:
     - "alerts/server_alerts.yml"
   ```

3. Reload Prometheus:
   ```bash
   # If using Docker
   docker exec prometheus kill -HUP 1

   # If using systemd
   sudo systemctl reload prometheus
   ```

## Step 6: Test the Bot

1. Open Telegram and search for your bot by username
2. Send `/start` - you should receive a welcome message
3. Send `/status` - you should receive current server metrics
4. Send `/health` - verify Prometheus connectivity

## Troubleshooting

### Bot doesn't respond to /start

- Check if bot token is correct in `.env`
- Verify the bot is running: `docker-compose ps` or check process
- Check logs for errors

### "You are not authorized" message

- Verify your user ID is in `config/config.yaml` under `telegram.authorized_users`
- User ID should be a number, not a username
- Restart the bot after changing configuration

### /status shows "N/A" for all metrics

- Check Prometheus URL in configuration
- Verify Prometheus is running and accessible
- Use `/health` command to test connectivity
- Check if node_exporter is running on your servers

### Alerts not being received

- Verify Alertmanager webhook URL points to bot
- Check if port 9119 is accessible from Alertmanager
- Review Alertmanager logs
- Review bot logs: `docker-compose logs alert-receiver`

### Docker container won't start

- Check Docker logs: `docker-compose logs`
- Verify `.env` file exists and has correct format
- Ensure no port conflicts (port 9119 already in use)

## Network Configuration

### Docker Network

If Prometheus/Grafana are running in Docker on the same host, edit the docker-compose.yml:

```yaml
networks:
  monitoring:
    external: true
    name: prometheus_network  # Adjust to your network name
```

### Firewall Rules

If running on separate hosts, ensure port 9119 is accessible:

```bash
# UFW
sudo ufw allow 9119/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 9119 -j ACCEPT
```

## Production Considerations

1. **Use a reverse proxy** (nginx/traefik) for HTTPS
2. **Set up proper logging** and log rotation
3. **Monitor the bot itself** (health checks, uptime)
4. **Backup** `data/authorized_users.json` regularly
5. **Use environment variables** for all secrets
6. **Run as non-root user** in Docker
7. **Enable Docker restart policies** (already configured)

## Next Steps

- Add more authorized users in `config/config.yaml`
- Customize alert rules in Prometheus
- Set up scheduled status reports (coming soon)
- Integrate with Grafana for dashboard links (coming soon)
