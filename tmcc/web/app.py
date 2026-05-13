import json
import threading
import time
import logging
import configparser
import os
from flask import Flask, Response, render_template, request, jsonify
from tmcc.monitors.speed_monitor import SpeedMonitor

log = logging.getLogger(__name__)

app = Flask(__name__)

# Shared monitor instance
monitor = SpeedMonitor()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'tmcc.ini')


def _load_port() -> int:
    config = configparser.RawConfigParser()
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


@app.route('/engine/<int:engine_id>/max_speed', methods=['POST'])
def set_max_speed(engine_id):
    """Save max speed for an engine to tmcc.ini."""
    data = request.get_json()
    max_speed = data.get('max_speed')
    if max_speed is None:
        return jsonify({'error': 'max_speed required'}), 400
    try:
        max_speed = int(max_speed)
    except ValueError:
        return jsonify({'error': 'max_speed must be an integer'}), 400

    abs_config = os.path.abspath(CONFIG_FILE)
    config = configparser.RawConfigParser()
    config.read(abs_config)
    if not config.has_section('EngineMaxSpeeds'):
        config.add_section('EngineMaxSpeeds')
    config.set('EngineMaxSpeeds', str(engine_id), str(max_speed))
    with open(abs_config, 'w') as f:
        config.write(f)

    # Update monitor's in-memory max speeds
    monitor._max_speeds[engine_id] = max_speed
    log.info(f"Set max speed for engine {engine_id} to {max_speed}")
    return jsonify({'ok': True, 'engine_id': engine_id, 'max_speed': max_speed})


@app.route('/stream')
def stream():
    """SSE endpoint — pushes engine updates to the browser."""
    def event_stream():
        last_seen = {}
        while True:
            engines = monitor.engines
            for engine_id, data in engines.items():
                current = json.dumps(data)
                if last_seen.get(engine_id) != current:
                    last_seen[engine_id] = current
                    yield f"event: engine\ndata: {current}\n\n"
            time.sleep(0.2)

    return Response(event_stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    t = threading.Thread(target=run_monitor, daemon=True)
    t.start()

    port = _load_port()
    log.info(f"Starting TMCC web dashboard on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)