"""Prometheus API client for querying metrics."""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger


class PrometheusClient:
    """Client for interacting with Prometheus API."""

    def __init__(self, prometheus_url: str):
        """Initialize Prometheus client.

        Args:
            prometheus_url: URL of the Prometheus server
        """
        self.base_url = prometheus_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"

    def query(self, query: str) -> Optional[Dict[str, Any]]:
        """Execute a PromQL query.

        Args:
            query: PromQL query string

        Returns:
            Query result or None if failed
        """
        try:
            response = requests.get(
                f"{self.api_url}/query",
                params={'query': query},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'success':
                logger.error(f"Query failed: {data}")
                return None

            return data['data']
        except Exception as e:
            logger.error(f"Failed to query Prometheus: {e}")
            return None

    def query_range(self, query: str, start: datetime, end: datetime, step: str = '15s') -> Optional[Dict[str, Any]]:
        """Execute a PromQL range query.

        Args:
            query: PromQL query string
            start: Start time
            end: End time
            step: Query resolution step

        Returns:
            Query result or None if failed
        """
        try:
            response = requests.get(
                f"{self.api_url}/query_range",
                params={
                    'query': query,
                    'start': start.timestamp(),
                    'end': end.timestamp(),
                    'step': step
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'success':
                logger.error(f"Range query failed: {data}")
                return None

            return data['data']
        except Exception as e:
            logger.error(f"Failed to query Prometheus range: {e}")
            return None

    def get_server_status(self) -> Dict[str, Any]:
        """Get comprehensive server status from Prometheus.

        Returns:
            Dictionary with server metrics
        """
        status = {
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage(),
            'disk_usage': self._get_disk_usage(),
            'network_traffic': self._get_network_traffic(),
            'timestamp': datetime.now().isoformat()
        }
        return status

    def _get_cpu_usage(self) -> Optional[float]:
        """Get CPU usage percentage."""
        query = '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
        result = self.query(query)

        if result and result['result']:
            return round(float(result['result'][0]['value'][1]), 2)
        return None

    def _get_memory_usage(self) -> Optional[Dict[str, float]]:
        """Get memory usage statistics."""
        # Total memory
        total_query = 'node_memory_MemTotal_bytes'
        total_result = self.query(total_query)

        # Available memory
        available_query = 'node_memory_MemAvailable_bytes'
        available_result = self.query(available_query)

        if total_result and total_result['result'] and available_result and available_result['result']:
            total = float(total_result['result'][0]['value'][1])
            available = float(available_result['result'][0]['value'][1])
            used = total - available
            usage_percent = (used / total) * 100

            return {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'available_gb': round(available / (1024**3), 2),
                'usage_percent': round(usage_percent, 2)
            }
        return None

    def _get_disk_usage(self) -> Optional[List[Dict[str, Any]]]:
        """Get disk usage for all mounted filesystems."""
        query = '(node_filesystem_size_bytes{fstype!~"tmpfs|fuse.lxcfs|squashfs|vfat"} - node_filesystem_free_bytes{fstype!~"tmpfs|fuse.lxcfs|squashfs|vfat"}) / node_filesystem_size_bytes{fstype!~"tmpfs|fuse.lxcfs|squashfs|vfat"} * 100'
        result = self.query(query)

        if result and result['result']:
            disks = []
            for item in result['result']:
                metric = item['metric']
                usage = float(item['value'][1])
                disks.append({
                    'mountpoint': metric.get('mountpoint', 'unknown'),
                    'device': metric.get('device', 'unknown'),
                    'usage_percent': round(usage, 2)
                })
            return disks
        return None

    def _get_network_traffic(self) -> Optional[Dict[str, float]]:
        """Get network traffic statistics."""
        # Received bytes rate
        rx_query = 'rate(node_network_receive_bytes_total{device!~"lo|docker.*|veth.*"}[5m])'
        rx_result = self.query(rx_query)

        # Transmitted bytes rate
        tx_query = 'rate(node_network_transmit_bytes_total{device!~"lo|docker.*|veth.*"}[5m])'
        tx_result = self.query(tx_query)

        if rx_result and rx_result['result'] and tx_result and tx_result['result']:
            rx_total = sum(float(item['value'][1]) for item in rx_result['result'])
            tx_total = sum(float(item['value'][1]) for item in tx_result['result'])

            return {
                'rx_mbps': round(rx_total * 8 / (1024**2), 2),  # Convert to Mbps
                'tx_mbps': round(tx_total * 8 / (1024**2), 2)
            }
        return None

    def check_health(self) -> bool:
        """Check if Prometheus server is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/-/healthy", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Prometheus health check failed: {e}")
            return False
