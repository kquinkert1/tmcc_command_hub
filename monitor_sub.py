import json
import logging
import argparse
from datetime import datetime
from tmcc.tmcc_subscriptions import TMCCSubscriptions

log = logging.getLogger(__name__)


def on_engine_command(client, userdata, message):
    payload = json.loads(message.payload)
    ts = datetime.now().strftime('%H:%M:%S.%f')[:11]
    print(f"{ts}  {message.topic}  {payload['description']}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Monitor TMCC engine commands via MQTT.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    subs = TMCCSubscriptions()
    subs.connect()
    subs.subscribe('tmcc/engine/#', on_engine_command)

    print("Monitoring engine commands (Ctrl+C to stop)...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopping...")
        subs.disconnect()

