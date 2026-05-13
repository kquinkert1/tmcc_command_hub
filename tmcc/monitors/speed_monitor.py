import json
import time
import logging
import configparser
import os
from datetime import datetime
from tmcc.monitors.monitor import Monitor
from tmcc.tmcc_subscriptions import TMCCSubscriptions

log = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'tmcc.ini')
CONFIG_SECTION = 'EngineMaxSpeeds'
DEFAULT_MAX_SPEED = 2_000_000


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
        self._max_speeds = self._load_max_speeds()

    def _load_max_speeds(self) -> dict:
        config = configparser.RawConfigParser()
        config.read(os.path.abspath(CONFIG_FILE))
        speeds = {}
        if config.has_section(CONFIG_SECTION):
            for engine_id, speed in config.items(CONFIG_SECTION):
                try:
                    speeds[int(engine_id)] = int(speed)
                except ValueError:
                    log.warning(f"Invalid max speed entry: {engine_id} = {speed}")
        log.debug(f"Loaded max speeds: {speeds}")
        return speeds

    def get_max_speed(self, engine_id: int) -> int:
        return self._max_speeds.get(engine_id, DEFAULT_MAX_SPEED)

    @property
    def engines(self) -> dict:
        return self._engines

    def monitor_subscriptions(self):
        self._subscriptions.connect()
        self._subscriptions.subscribe('tmcc/engine/#', self._on_engine_update)

    def _on_engine_update(self, client, userdata, message):
        payload = json.loads(message.payload)
        engine_id = payload['id']
        payload['max_speed'] = self.get_max_speed(engine_id)
        self._engines[engine_id] = payload
        self._dirty = True

    def _print_table(self):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"\n--- Engine Speed Monitor [{ts}] ---")
        if not self._engines:
            print("  No engines seen yet.")
        else:
            print(f"  {'Engine':>8}  {'Speed':>6}  {'Max':>10}  {'Direction':<10}  {'Bell':<5}  {'Last Command':<30}  {'Cmd Time':<11}  {'Msg Time':<11}  {'Comment'}")
            print(f"  {'-'*8}  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*5}  {'-'*30}  {'-'*11}  {'-'*11}  {'-'*20}")
            for address in sorted(self._engines):
                e = self._engines[address]
                bell = 'On' if e['bell'] else 'Off'
                max_spd = e.get('max_speed', DEFAULT_MAX_SPEED)
                max_str = '—' if max_spd == DEFAULT_MAX_SPEED else str(max_spd)
                print(f"  {address:>8}  {e['speed']:>6}  {max_str:>10}  {e['direction']:<10}  {bell:<5}  {e['last_command']:<30}  {e['command_timestamp']}  {e['message_timestamp']}  {e.get('line_comment', '')}")
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