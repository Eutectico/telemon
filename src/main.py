"""Main entry point for the Telegram monitoring bot."""

import sys
import asyncio
from pathlib import Path
from loguru import logger

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config_loader import ConfigLoader
from telegram_bot import MonitoringBot
from alert_receiver import AlertReceiver


def setup_logging(config: ConfigLoader):
    """Setup logging configuration.

    Args:
        config: Configuration loader instance
    """
    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        level=config.get('logging.level', 'INFO'),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )

    # Add file handler if log file is configured
    log_file = config.get('logging.file')
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            level=config.get('logging.level', 'INFO'),
            rotation="10 MB",
            retention="1 week",
            compression="zip"
        )


async def start_alert_receiver(bot: MonitoringBot, config: ConfigLoader):
    """Start the alert receiver in the background.

    Args:
        bot: MonitoringBot instance
        config: Configuration loader instance
    """
    webhook_config = config.get_webhook_config()
    receiver = AlertReceiver(bot, webhook_config)

    try:
        await receiver.start()
        logger.info("Alert receiver running")

        # Keep the receiver running
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour

    except Exception as e:
        logger.error(f"Alert receiver error: {e}")


def main():
    """Main function to start the bot."""
    try:
        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        config = ConfigLoader(str(config_path))

        # Setup logging
        setup_logging(config)

        logger.info("Starting Telegram Server Monitoring Bot")

        # Create bot instance
        bot = MonitoringBot(config)

        # Start alert receiver in the background
        # Note: This will be integrated with the telegram bot's event loop
        webhook_config = config.get_webhook_config()
        receiver = AlertReceiver(bot, webhook_config)

        # Create asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Start alert receiver
        loop.create_task(receiver.start())

        # Run the bot (this is blocking)
        bot.run()

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
