"""Alertmanager webhook receiver for handling Prometheus alerts."""

from aiohttp import web
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime
import asyncio


class AlertReceiver:
    """Webhook receiver for Alertmanager alerts."""

    def __init__(self, bot, config: dict):
        """Initialize alert receiver.

        Args:
            bot: MonitoringBot instance
            config: Webhook configuration
        """
        self.bot = bot
        self.config = config
        self.app = web.Application()
        self.app.router.add_post(config['path'], self.handle_alert)

        # Alert aggregation
        self.pending_alerts = []
        self.aggregation_task = None

    async def handle_alert(self, request: web.Request) -> web.Response:
        """Handle incoming alert webhook from Alertmanager.

        Args:
            request: aiohttp request object

        Returns:
            HTTP response
        """
        try:
            data = await request.json()
            logger.info(f"Received alert webhook: {data}")

            # Extract alerts from payload
            alerts = data.get('alerts', [])

            for alert in alerts:
                self.pending_alerts.append(alert)

            # Start aggregation task if not running
            if self.aggregation_task is None or self.aggregation_task.done():
                self.aggregation_task = asyncio.create_task(self._aggregate_and_send())

            return web.Response(status=200, text="OK")

        except Exception as e:
            logger.error(f"Failed to handle alert: {e}")
            return web.Response(status=500, text=f"Error: {str(e)}")

    async def _aggregate_and_send(self):
        """Aggregate alerts and send them after a delay."""
        # Wait for aggregation window
        await asyncio.sleep(30)  # 30 seconds aggregation window

        if not self.pending_alerts:
            return

        # Group alerts by severity
        alerts_by_severity = {
            'critical': [],
            'warning': [],
            'info': []
        }

        for alert in self.pending_alerts:
            severity = alert.get('labels', {}).get('severity', 'info').lower()
            if severity not in alerts_by_severity:
                severity = 'info'
            alerts_by_severity[severity].append(alert)

        # Format and send message
        message = self._format_alerts(alerts_by_severity)

        # Broadcast to all users
        await self.bot.broadcast_alert(message)

        # Clear pending alerts
        self.pending_alerts.clear()

    def _format_alerts(self, alerts_by_severity: Dict[str, List[Dict]]) -> str:
        """Format alerts into a readable message.

        Args:
            alerts_by_severity: Dictionary of alerts grouped by severity

        Returns:
            Formatted message string
        """
        lines = ["🚨 *Alert Notification*\n"]

        # Critical alerts
        critical = alerts_by_severity.get('critical', [])
        if critical:
            lines.append("🔴 *CRITICAL ALERTS*")
            for alert in critical:
                lines.append(self._format_single_alert(alert))
            lines.append("")

        # Warning alerts
        warnings = alerts_by_severity.get('warning', [])
        if warnings:
            lines.append("🟡 *WARNING ALERTS*")
            for alert in warnings:
                lines.append(self._format_single_alert(alert))
            lines.append("")

        # Info alerts
        info = alerts_by_severity.get('info', [])
        if info:
            lines.append("🔵 *INFO ALERTS*")
            for alert in info:
                lines.append(self._format_single_alert(alert))
            lines.append("")

        # Summary
        total = len(critical) + len(warnings) + len(info)
        lines.append(f"📊 Total: {total} alert(s)")
        lines.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    def _format_single_alert(self, alert: Dict[str, Any]) -> str:
        """Format a single alert.

        Args:
            alert: Alert dictionary

        Returns:
            Formatted alert string
        """
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        status = alert.get('status', 'unknown')

        # Extract key information
        alertname = labels.get('alertname', 'Unknown')
        instance = labels.get('instance', 'unknown')
        summary = annotations.get('summary', annotations.get('description', 'No description'))

        # Check if resolved
        if status == 'resolved':
            emoji = "🟢"
            status_text = "RESOLVED"
        else:
            emoji = "🔴"
            status_text = "FIRING"

        return f"{emoji} *{alertname}* [{status_text}]\n" \
               f"   Instance: `{instance}`\n" \
               f"   {summary}"

    async def start(self):
        """Start the webhook receiver."""
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(
            runner,
            host='0.0.0.0',
            port=self.config['port']
        )

        await site.start()
        logger.info(f"Alert receiver started on port {self.config['port']}")

    def get_app(self):
        """Get the aiohttp application.

        Returns:
            aiohttp web application
        """
        return self.app
