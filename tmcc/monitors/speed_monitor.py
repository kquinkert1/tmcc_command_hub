import json
import time
import logging
from datetime import datetime
from tmcc.monitors.monitor import Monitor
from tmcc.tmcc_subscriptions import TMCCSubscriptions
from tmcc.tmcc_enums import EngineAction

log = logging.getLogger(__name__)

DIRECTION_ACTIONS = {
    EngineAction.FORWARD.value,
    EngineAction.REVERSE.value,
    EngineAction.TOGGLE_DIR.value
}


class SpeedMonitor(Monitor):
    """
    Monitors engine speeds via MQTT.
    Prints table on new commands, or every 10 seconds if idle.
    """

    TABLE_INTERVAL = 10  # seconds

    def __init__(self):
        self._subscriptions = TMCCSubscriptions()
        self._engines = {}
        self._dirty = False

    def monitor_subscriptions(self):
        self._subscriptions.connect()
        self._subscriptions.subscribe('tmcc/engine/#', self._on_engine_command)

    def _on_engine_command(self, client, userdata, message):
        payload = json.loads(message.payload)
        address = payload['address']
        action = payload['action']
        speed_value = payload.get('speed_value')

        if address not in self._engines:
            self._engines[address] = {'speed': 0, 'direction': 'Forward', 'bell': False, 'last_command': ''}

        engine = self._engines[address]

        if action == EngineAction.ABSOLUTE_SPEED.value:
            engine['speed'] = max(0, speed_value)
        elif action == EngineAction.RELATIVE_SPEED.value:
            engine['speed'] = max(0, engine['speed'] + speed_value)
        elif action in DIRECTION_ACTIONS:
            engine['speed'] = 0
            if action == EngineAction.FORWARD.value:
                engine['direction'] = 'Forward'
            elif action == EngineAction.REVERSE.value:
                engine['direction'] = 'Reverse'
            elif action == EngineAction.TOGGLE_DIR.value:
                engine['direction'] = 'Reverse' if engine['direction'] == 'Forward' else 'Forward'
        elif action == EngineAction.RING_BELL.value:
            engine['bell'] = not engine['bell']

        engine['last_command'] = payload['description']
        self._dirty = True

    def _print_table(self):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"\n--- Engine Speed Monitor [{ts}] ---")
        if not self._engines:
            print("  No engines seen yet.")
        else:
            print(f"  {'Engine':>8}  {'Speed':>6}  {'Direction':<10}  {'Bell':<5}  {'Last Command':<30}")
            print(f"  {'-'*8}  {'-'*6}  {'-'*10}  {'-'*5}  {'-'*30}")
            for address in sorted(self._engines):
                e = self._engines[address]
                bell = 'On' if e['bell'] else 'Off'
                print(f"  {address:>8}  {e['speed']:>6}  {e['direction']:<10}  {bell:<5}  {e['last_command']:<30}")
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

