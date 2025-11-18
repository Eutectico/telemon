# Telemon

A Telegram bot for monitoring servers using Prometheus and Grafana. Receive real-time alerts and query server metrics directly from Telegram.

## Features

- 📊 Real-time server status monitoring (CPU, Memory, Disk, Network)
- 🚨 Alert notifications from Prometheus Alertmanager
- 🔐 User authorization system
- 🐳 Docker support for easy deployment
- 📈 Integration with Prometheus and Grafana
- 💬 Interactive Telegram commands

## Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Prometheus server
- (Optional) Grafana server
- (Optional) Docker & Docker Compose

## Quick Start

### 1. Create a Telegram Bot

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save the bot token you receive
4. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)

### 2. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/Eutectico/telemon.git
cd telemon

# Copy environment file
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
PROMETHEUS_URL=http://your-prometheus:9090
GRAFANA_URL=http://your-grafana:3000
```

Edit `config/config.yaml` and add your Telegram user ID:
```yaml
telegram:
  authorized_users:
    - 123456789  # Your Telegram user ID
```

### 3. Run with Docker (Recommended)

```bash
# Build and start the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

### 4. Run without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python src/main.py
```

## Configuration

### Telegram Bot Commands

- `/start` - Initialize the bot
- `/help` - Show available commands
- `/status` - Get current server status
- `/metrics` - Get detailed metrics (coming soon)
- `/health` - Check Prometheus connectivity

### Alertmanager Integration

Configure Alertmanager to send webhooks to the bot:

```yaml
# alertmanager.yml
route:
  receiver: 'telegram-bot'

receivers:
  - name: 'telegram-bot'
    webhook_configs:
      - url: 'http://telegram-bot:9119/alerts'
        send_resolved: true
```

### Prometheus Queries

The bot uses these default queries:
- **CPU Usage**: `100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
- **Memory Usage**: `node_memory_MemTotal_bytes` and `node_memory_MemAvailable_bytes`
- **Disk Usage**: `node_filesystem_size_bytes` and `node_filesystem_free_bytes`
- **Network Traffic**: `rate(node_network_receive_bytes_total[5m])`

## Project Structure

```
telemon/
├── src/
│   ├── main.py              # Entry point
│   ├── telegram_bot.py      # Telegram bot implementation
│   ├── prometheus_client.py # Prometheus API client
│   ├── alert_receiver.py    # Alertmanager webhook receiver
│   ├── config_loader.py     # Configuration management
│   └── user_manager.py      # User authorization
├── config/
│   └── config.yaml          # Main configuration file
├── data/                    # Persistent data (user storage)
├── logs/                    # Log files
├── tests/                   # Unit tests
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Security

- Only authorized users (by Telegram user ID) can use the bot
- Sensitive credentials are stored in environment variables
- User data is persisted in `data/authorized_users.json`
- All API tokens should be kept secret and never committed to git

## Troubleshooting

### Bot doesn't respond
- Check if the bot token is correct
- Verify your user ID is in the authorized list
- Check logs: `docker-compose logs -f` or `tail -f logs/bot.log`

### Can't connect to Prometheus
- Verify Prometheus URL in configuration
- Check network connectivity
- Use `/health` command to test connection

### Alerts not received
- Verify Alertmanager webhook configuration
- Check if port 9119 is accessible
- Review alert receiver logs

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (coming soon)
pytest tests/

# Format code
black src/

# Lint code
flake8 src/
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.

## Buy Me A Coffee

Wenn dir dieses Projekt hilft, kannst du mir gerne einen Kaffee spendieren!

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
