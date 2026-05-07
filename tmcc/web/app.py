import json
import threading
import time
import logging
import configparser
import os
from flask import Flask, Response, render_template
from tmcc.monitors.speed_monitor import SpeedMonitor

log = logging.getLogger(__name__)

app = Flask(__name__)

# Shared monitor instance
monitor = SpeedMonitor()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'tmcc.ini')


def _load_port() -> int:
    config = configparser.ConfigParser()
    config.read(os.path.abspath(CONFIG_FILE))
    return int(config['Web']['port'])


def run_monitor():
    """Run SpeedMonitor in a background thread."""
    monitor.monitor_subscriptions()
    while True:
        time.sleep(0.1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stream')
def stream():
    """SSE endpoint — pushes engine updates to the browser."""
    def event_stream():
        last_seen = {}
        while True:
            engines = monitor.engines
            for engine_id, data in engines.items():
                if last_seen.get(engine_id) != data:
                    last_seen[engine_id] = data.copy()
                    yield f"event: engine\ndata: {json.dumps(data)}\n\n"
            time.sleep(0.2)

    return Response(event_stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    t = threading.Thread(target=run_monitor, daemon=True)
    t.start()

    port = _load_port()
    log.info(f"Starting TMCC web dashboard on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)