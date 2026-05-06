import json
import time
import logging
from datetime import datetime
from tmcc.monitors.monitor import Monitor
from tmcc.tmcc_subscriptions import TMCCSubscriptions

log = logging.getLogger(__name__)


class SpeedMonitor(Monitor):
    """
    Monitors engine speeds via MQTT.
    Prints table on new messages, or every 10 seconds if idle.
    """

    TABLE_INTERVAL = 10  # seconds

    def __init__(self):
        self._subscriptions = TMCCSubscriptions()
        self._engines = {}  # address -> payload dict
        self._dirty = False

    def monitor_subscriptions(self):
        self._subscriptions.connect()
        self._subscriptions.subscribe('tmcc/engine/#', self._on_engine_update)

    def _on_engine_update(self, client, userdata, message):
        payload = json.loads(message.payload)
        self._engines[payload['id']] = payload
        self._dirty = True

    def _print_table(self):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"\n--- Engine Speed Monitor [{ts}] ---")
        if not self._engines:
            print("  No engines seen yet.")
        else:
            print(f"  {'Engine':>8}  {'Speed':>6}  {'Direction':<10}  {'Bell':<5}  {'Last Command':<30}  {'Time':<11}  {'Comment'}")
            print(f"  {'-'*8}  {'-'*6}  {'-'*10}  {'-'*5}  {'-'*30}  {'-'*11}  {'-'*20}")
            for address in sorted(self._engines):
                e = self._engines[address]
                bell = 'On' if e['bell'] else 'Off'
                print(f"  {address:>8}  {e['speed']:>6}  {e['direction']:<10}  {bell:<5}  {e['last_command']:<30}  {e['timestamp']}  {e.get('line_comment', '')}")
        print()
        self._dirty = False

    def run(self):
        self.monitor_subscriptions()
        print("SpeedMonitor running (Ctrl+C to stop)...")
        last_print = time.time()
        try:
            while True:
                time.sleep(0.1)
                now = time.time()
                if self._dirty or (now - last_print >= self.TABLE_INTERVAL):
                    self._print_table()
                    last_print = now
        except KeyboardInterrupt:
            print("\nStopping...")
            self._subscriptions.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    monitor = SpeedMonitor()
    monitor.run()
