"""Telegram Bot for server monitoring."""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from loguru import logger
from typing import Optional
import asyncio

from config_loader import ConfigLoader
from user_manager import UserManager
from prometheus_client import PrometheusClient


class MonitoringBot:
    """Telegram bot for server monitoring and alerts."""

    def __init__(self, config: ConfigLoader):
        """Initialize the monitoring bot.

        Args:
            config: Configuration loader instance
        """
        self.config = config
        self.user_manager = UserManager(config.get_authorized_users())
        self.prometheus = PrometheusClient(config.get_prometheus_url())

        # Create application
        self.application = Application.builder().token(config.get_telegram_token()).build()

        # Register command handlers
        self._register_handlers()

        logger.info("Monitoring bot initialized")

    def _register_handlers(self):
        """Register all command handlers."""
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("metrics", self.cmd_metrics))
        self.application.add_handler(CommandHandler("health", self.cmd_health))

        # Handle unknown commands
        self.application.add_handler(MessageHandler(filters.COMMAND, self.cmd_unknown))

    def _check_authorization(self, user_id: int) -> bool:
        """Check if user is authorized.

        Args:
            user_id: Telegram user ID

        Returns:
            True if authorized, False otherwise
        """
        return self.user_manager.is_authorized(user_id)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name

        if not self._check_authorization(user_id):
            await update.message.reply_text(
                f"Sorry {user_name}, you are not authorized to use this bot.\n"
                f"Your user ID is: {user_id}\n\n"
                "Please contact the administrator to get access."
            )
            logger.warning(f"Unauthorized access attempt from user {user_id} ({user_name})")
            return

        welcome_message = (
            f"Welcome {user_name}!\n\n"
            "🤖 *Server Monitoring Bot*\n\n"
            "I will help you monitor your servers and receive alerts from Prometheus and Grafana.\n\n"
            "Use /help to see available commands."
        )
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"User {user_id} ({user_name}) started the bot")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        user_id = update.effective_user.id

        if not self._check_authorization(user_id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        help_text = (
            "*Available Commands:*\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/status - Get current server status\n"
            "/metrics - Get detailed metrics\n"
            "/health - Check Prometheus health\n"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user_id = update.effective_user.id

        if not self._check_authorization(user_id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        # Send "processing" message
        msg = await update.message.reply_text("Fetching server status...")

        try:
            # Get status from Prometheus
            status = self.prometheus.get_server_status()

            # Format status message
            status_text = self._format_status(status)

            # Update message with status
            await msg.edit_text(status_text, parse_mode='Markdown')
            logger.info(f"Status requested by user {user_id}")

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            await msg.edit_text(
                "❌ Failed to fetch server status.\n"
                f"Error: {str(e)}"
            )

    def _format_status(self, status: dict) -> str:
        """Format status dictionary into readable message.

        Args:
            status: Status dictionary from Prometheus

        Returns:
            Formatted status message
        """
        lines = ["📊 *Server Status*\n"]

        # CPU Usage
        cpu = status.get('cpu_usage')
        if cpu is not None:
            cpu_emoji = "🟢" if cpu < 70 else "🟡" if cpu < 90 else "🔴"
            lines.append(f"{cpu_emoji} *CPU Usage:* {cpu}%")
        else:
            lines.append("⚠️ *CPU Usage:* N/A")

        # Memory Usage
        memory = status.get('memory_usage')
        if memory:
            mem_emoji = "🟢" if memory['usage_percent'] < 70 else "🟡" if memory['usage_percent'] < 90 else "🔴"
            lines.append(
                f"{mem_emoji} *Memory:* {memory['used_gb']:.1f}/{memory['total_gb']:.1f} GB "
                f"({memory['usage_percent']:.1f}%)"
            )
        else:
            lines.append("⚠️ *Memory:* N/A")

        # Disk Usage
        disks = status.get('disk_usage')
        if disks:
            lines.append("\n💾 *Disk Usage:*")
            for disk in disks:
                usage = disk['usage_percent']
                disk_emoji = "🟢" if usage < 70 else "🟡" if usage < 90 else "🔴"
                lines.append(
                    f"  {disk_emoji} {disk['mountpoint']}: {usage:.1f}%"
                )
        else:
            lines.append("\n⚠️ *Disk Usage:* N/A")

        # Network Traffic
        network = status.get('network_traffic')
        if network:
            lines.append(
                f"\n🌐 *Network:* ⬇️ {network['rx_mbps']:.2f} Mbps | "
                f"⬆️ {network['tx_mbps']:.2f} Mbps"
            )
        else:
            lines.append("\n⚠️ *Network:* N/A")

        # Timestamp
        lines.append(f"\n🕐 Updated: {status.get('timestamp', 'N/A')}")

        return "\n".join(lines)

    async def cmd_metrics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /metrics command."""
        user_id = update.effective_user.id

        if not self._check_authorization(user_id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        await update.message.reply_text(
            "📈 *Detailed Metrics*\n\n"
            "This feature will show detailed metrics for specific servers.\n"
            "Coming soon!",
            parse_mode='Markdown'
        )

    async def cmd_health(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /health command."""
        user_id = update.effective_user.id

        if not self._check_authorization(user_id):
            await update.message.reply_text("You are not authorized to use this bot.")
            return

        msg = await update.message.reply_text("Checking Prometheus health...")

        is_healthy = self.prometheus.check_health()

        if is_healthy:
            await msg.edit_text("✅ Prometheus is healthy and reachable!")
        else:
            await msg.edit_text(
                "❌ Prometheus is not reachable!\n\n"
                f"URL: {self.config.get_prometheus_url()}"
            )

    async def cmd_unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands."""
        user_id = update.effective_user.id

        if not self._check_authorization(user_id):
            return

        await update.message.reply_text(
            "❓ Unknown command. Use /help to see available commands."
        )

    async def send_alert(self, user_id: int, message: str):
        """Send alert message to a user.

        Args:
            user_id: Telegram user ID
            message: Alert message
        """
        try:
            await self.application.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"Alert sent to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send alert to user {user_id}: {e}")

    async def broadcast_alert(self, message: str):
        """Broadcast alert to all authorized users.

        Args:
            message: Alert message
        """
        users = self.user_manager.get_all_users()
        logger.info(f"Broadcasting alert to {len(users)} users")

        for user_id in users:
            await self.send_alert(user_id, message)

    def run(self):
        """Start the bot."""
        logger.info("Starting Telegram bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
