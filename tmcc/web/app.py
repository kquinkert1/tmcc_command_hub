import json
import socket
import uuid
import threading
import time
import logging
import configparser
import os
from flask import Flask, Response, render_template, request, jsonify
from tmcc.monitors.speed_monitor import SpeedMonitor
from tmcc.tmcc_subscriptions import TMCCSubscriptions

log = logging.getLogger(__name__)

app = Flask(__name__)

monitor = SpeedMonitor()
subscriptions = TMCCSubscriptions()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'tmcc.ini')
SAFEGUARD_SECTION = 'SafeguardEnabled'


def _get_machine_id():
    hostname = socket.gethostname()
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 48, 8)][::-1])
    mac_clean = mac.replace(':', '')
    return hostname, mac_clean


def _get_serial_section():
    hostname, mac = _get_machine_id()
    return f"SerialAdaptor_{hostname}_{mac}"


def _load_port() -> int:
    config = configparser.RawConfigParser()
    config.read(os.path.abspath(CONFIG_FILE))
    return int(config['Web']['port'])


def run_monitor():
    monitor.monitor_subscriptions()
    monitor.start_safeguard()
    while True:
        time.sleep(0.1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/serial/ports')
def get_serial_ports():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    section = _get_serial_section()
    current_port = None
    config = configparser.RawConfigParser()
    config.read(os.path.abspath(CONFIG_FILE))
    if config.has_option(section, 'port'):
        current_port = config.get(section, 'port')
    elif config.has_option('SerialAdaptor', 'port'):
        current_port = config.get('SerialAdaptor', 'port')
    hostname, mac = _get_machine_id()
    return jsonify({
        'ports': [{'device': p.device, 'description': p.description} for p in ports],
        'current_port': current_port,
        'hostname': hostname,
        'mac': mac,
        'section': section
    })


@app.route('/serial/port', methods=['POST'])
def save_serial_port():
    data = request.get_json()
    port = data.get('port')
    if not port:
        return jsonify({'error': 'port required'}), 400

    section = _get_serial_section()
    abs_config = os.path.abspath(CONFIG_FILE)
    config = configparser.RawConfigParser()
    config.read(abs_config)
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, 'port', port)
    with open(abs_config, 'w') as f:
        config.write(f)
    log.info(f"Saved serial port {port} for {section}")
    return jsonify({'ok': True, 'port': port, 'section': section})


@app.route('/engine/<int:engine_id>/max_speed', methods=['POST'])
def set_max_speed(engine_id):
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

    monitor._max_speeds[engine_id] = max_speed
    log.info(f"Set max speed for engine {engine_id} to {max_speed}")
    return jsonify({'ok': True, 'engine_id': engine_id, 'max_speed': max_speed})


@app.route('/engine/<int:engine_id>/send_abs_speed', methods=['POST'])
def send_abs_speed(engine_id):
    data = request.get_json()
    speed = data.get('speed')
    if speed is None:
        return jsonify({'error': 'speed required'}), 400
    try:
        speed = int(speed)
    except ValueError:
        return jsonify({'error': 'speed must be an integer'}), 400

    topic = f"tmcc_send/engine/{engine_id}"
    payload = {
        'action': 'ABSOLUTE_SPEED',
        'address': engine_id,
        'speed': speed,
        'priority': False
    }
    subscriptions.publish(topic, payload)
    log.info(f"Sent abs speed {speed} to engine {engine_id}")
    return jsonify({'ok': True, 'engine_id': engine_id, 'speed': speed})


@app.route('/engine/<int:engine_id>/safeguard', methods=['POST'])
def set_safeguard(engine_id):
    data = request.get_json()
    enabled = data.get('enabled')
    if enabled is None:
        return jsonify({'error': 'enabled required'}), 400

    enabled = bool(enabled)

    abs_config = os.path.abspath(CONFIG_FILE)
    config = configparser.RawConfigParser()
    config.read(abs_config)
    if not config.has_section(SAFEGUARD_SECTION):
        config.add_section(SAFEGUARD_SECTION)
    config.set(SAFEGUARD_SECTION, str(engine_id), str(enabled))
    with open(abs_config, 'w') as f:
        config.write(f)

    monitor.set_safeguard_enabled(engine_id, enabled)
    log.info(f"Safeguard {'enabled' if enabled else 'disabled'} for engine {engine_id}")
    return jsonify({'ok': True, 'engine_id': engine_id, 'enabled': enabled})


@app.route('/stream')
def stream():
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
    logging.basicConfig(level=logging.INFO)

    subscriptions.connect()

    t = threading.Thread(target=run_monitor, daemon=True)
    t.start()

    port = _load_port()
    log.info(f"Starting TMCC web dashboard on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
