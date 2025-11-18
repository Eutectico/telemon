# Quick Start Guide

Get Telemon running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- A Telegram account
- Prometheus running somewhere

## Steps

### 1. Create Telegram Bot (2 minutes)

```bash
# Open Telegram and message @BotFather
# Send: /newbot
# Follow instructions and save your bot token
# Get your user ID from @userinfobot
```

### 2. Clone & Configure (1 minute)

```bash
# Clone repository
git clone <your-repo-url>
cd telemon

# Copy environment template
cp .env.example .env

# Edit .env - add your bot token
nano .env
```

**.env file:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
PROMETHEUS_URL=http://your-prometheus:9090
```

**config/config.yaml - add your Telegram user ID:**
```yaml
telegram:
  authorized_users:
    - 123456789  # Your user ID from @userinfobot
```

### 3. Start the Bot (1 minute)

```bash
# Start with Docker
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Test (1 minute)

Open Telegram, find your bot, and send:
- `/start` - Should greet you
- `/status` - Should show server metrics
- `/health` - Should confirm Prometheus connection

## Done!

Your bot is now running and monitoring your servers!

## Next Steps

- Configure Alertmanager to send alerts (see [SETUP.md](docs/SETUP.md))
- Add Prometheus alert rules (see `config/prometheus-rules-example.yml`)
- Customize thresholds in alert rules

## Troubleshooting

**Bot doesn't respond?**
- Check logs: `docker-compose logs`
- Verify bot token in `.env`
- Ensure your user ID is in `config.yaml`

**Can't connect to Prometheus?**
- Check `PROMETHEUS_URL` in `.env`
- Verify Prometheus is accessible
- Use `/health` command to test

## Support

See full documentation in [README.md](README.md) and [docs/SETUP.md](docs/SETUP.md)
