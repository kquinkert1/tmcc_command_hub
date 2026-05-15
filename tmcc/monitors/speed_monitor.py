import json
import time
import logging
import configparser
import os
import threading
from datetime import datetime
from tmcc.monitors.monitor import Monitor
from tmcc.models.engine import Engine
from tmcc.tmcc_subscriptions import TMCCSubscriptions

log = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'tmcc.ini')
CONFIG_SECTION = 'EngineMaxSpeeds'
SAFEGUARD_SECTION = 'SafeguardEnabled'
DEFAULT_MAX_SPEED = None


class SpeedMonitor(Monitor):
    """
    Monitors engine speeds via MQTT.
    Prints table on new messages, or every 10 seconds if idle.
    """

    TABLE_INTERVAL = 10  # seconds
    SAFEGUARD_INTERVAL = 2  # seconds

    def __init__(self):
        self._subscriptions = TMCCSubscriptions()
        self._engines = {}             # address -> payload dict
        self._engine_objs = {}         # address -> Engine instance
        self._last_highball = {}       # address -> timestamp of last highball
        self._highball_counts = {}     # address -> highball count
        self._safeguard_enabled = {}   # address -> bool
        self._dirty = False
        self._max_speeds = self._load_max_speeds()
        self._safeguard_enabled = self._load_safeguard_enabled()
        self._lock = threading.Lock()
        self._safeguard_thread = None

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

    def _load_safeguard_enabled(self) -> dict:
        config = configparser.RawConfigParser()
        config.read(os.path.abspath(CONFIG_FILE))
        enabled = {}
        if config.has_section(SAFEGUARD_SECTION):
            for engine_id, val in config.items(SAFEGUARD_SECTION):
                try:
                    enabled[int(engine_id)] = val.strip().lower() in ('true', '1', 'yes')
                except ValueError:
                    log.warning(f"Invalid safeguard entry: {engine_id} = {val}")
        log.debug(f"Loaded safeguard enabled: {enabled}")
        return enabled

    def get_max_speed(self, engine_id: int) -> int:
        return self._max_speeds.get(engine_id, DEFAULT_MAX_SPEED)

    def _get_or_create_engine(self, engine_id: int) -> Engine:
        if engine_id not in self._engine_objs:
            self._engine_objs[engine_id] = Engine(engine_id)
        return self._engine_objs[engine_id]

    def set_safeguard_enabled(self, engine_id: int, enabled: bool):
        with self._lock:
            self._safeguard_enabled[engine_id] = enabled
        log.info(f"Safeguard {'enabled' if enabled else 'disabled'} for engine {engine_id}")

    def is_safeguard_enabled(self, engine_id: int) -> bool:
        return self._safeguard_enabled.get(engine_id, False)

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
        payload['highball_count'] = self._highball_counts.get(engine_id, 0)
        payload['safeguard_enabled'] = self.is_safeguard_enabled(engine_id)

        with self._lock:
            self._engines[engine_id] = payload

            if payload.get('command'):
                engine = self._get_or_create_engine(engine_id)
                engine.sync_from_payload(payload)
                log.debug(f"Engine update: {engine}")
                if self._safeguard_enabled.get(engine_id, False):
                    self._do_highball(engine_id, engine.speed)

        if payload.get('command') and 'Boost' in payload['command']:
            self.handle_boost(engine_id)

        self._dirty = True

    def handle_boost(self, engine_id: int):
        log.info(f"Boost detected for engine {engine_id}")

    def _do_highball(self, engine_id: int, speed: int):
        """Internal — sends FORWARD + ABSOLUTE_SPEED."""
        topic = f"tmcc_send/engine/{engine_id}"
        self._subscriptions.publish(topic, {
            'action': 'FORWARD',
            'address': engine_id,
            'priority': True
        })
        self._subscriptions.publish(topic, {
            'action': 'ABSOLUTE_SPEED',
            'address': engine_id,
            'speed': speed,
            'priority': True
        })
        self._last_highball[engine_id] = time.time()
        self._highball_counts[engine_id] = self._highball_counts.get(engine_id, 0) + 1
        log.debug(f"Highball engine {engine_id}: FORWARD + ABSOLUTE_SPEED={speed} count={self._highball_counts[engine_id]}")

    def highball(self, engine_id: int):
        with self._lock:
            engine = self._get_or_create_engine(engine_id)
            speed = engine.speed
        self._do_highball(engine_id, speed)

    def safeguard(self):
        log.info("Safeguard thread started")
        while True:
            time.sleep(0.1)
            now = time.time()
            with self._lock:
                engine_ids = list(self._engine_objs.keys())
            for engine_id in engine_ids:
                if not self._safeguard_enabled.get(engine_id, False):
                    continue
                last = self._last_highball.get(engine_id, 0)
                if now - last >= self.SAFEGUARD_INTERVAL:
                    self.highball(engine_id)

    def start_safeguard(self):
        self._safeguard_thread = threading.Thread(target=self.safeguard, daemon=True)
        self._safeguard_thread.start()
        log.info("Safeguard thread launched")

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
                max_str = '—' if max_spd is None else str(max_spd)
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