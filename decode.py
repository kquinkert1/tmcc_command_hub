#!/usr/bin/env python3
"""
Decode TMCC command bytes. Pass two hex bytes (0xFE header assumed).
Usage: python decode.py ABCD
       python decode.py AB CD
       python decode.py -f <filename>
       python decode.py -f <filename> --csv
       python decode.py        # interactive mode
"""
import sys
import csv
from tmcc.tmcc_command_factory import TMCCCommandFactory

CSV_FIELDS = ['command_type', 'address', 'command_field', 'data_field', 'action', 'speed_value', 'raw_word']
csv_writer = None

HELP = """
Usage: python decode.py [options] [hex bytes]

Decode TMCC command bytes (0xFE header assumed).

Arguments:
  hex bytes         Two hex bytes to decode (e.g. 0B80, 0B 80, 0x0B 0x80)

Options:
  -f <filename>     Read hex bytes from file (one per line, # for comments)
  --csv             Output in CSV format
  --help            Show this help message

Examples:
  python decode.py 0B80
  python decode.py 0x0B 0x80
  python decode.py -f commands.txt
  python decode.py -f commands.txt --csv
  python decode.py              # interactive mode
"""


def decode(hex_input):
    tokens = hex_input.strip().split()
    if len(tokens) == 2:
        b1 = int(tokens[0], 16)
        b2 = int(tokens[1], 16)
    elif len(tokens) == 1:
        cleaned = tokens[0].replace('0x', '').replace(':', '')
        if len(cleaned) != 4:
            print(f"Expected 4 hex chars, got: {hex_input}")
            return
        b1 = int(cleaned[0:2], 16)
        b2 = int(cleaned[2:4], 16)
    else:
        print(f"Could not parse: {hex_input}")
        return

    packet = bytes([0xFE, b1, b2])
    r = TMCCCommandFactory.decode(packet)

    if csv_writer:
        csv_writer.writerow([
            r.command_type.value,
            r.address,
            bin(r.command_field),
            bin(r.data_field),
            r.action.value,
            r.speed_value,
            bin(r.raw_word)
        ])
    else:
        print(f"0x{b1:02X} 0x{b2:02X}  {r.description}")


def decode_file(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                decode(line)


if __name__ == '__main__':
    if '--help' in sys.argv or '-h' in sys.argv:
        print(HELP)
        sys.exit(0)

    use_csv = '--csv' in sys.argv

    if use_csv:
        writer = csv.writer(sys.stdout)
        csv_writer = writer
        writer.writerow(CSV_FIELDS)

    if '-f' in sys.argv:
        idx = sys.argv.index('-f')
        decode_file(sys.argv[idx + 1])
    elif len(sys.argv) > 1 and not use_csv:
        decode(' '.join(sys.argv[1:]))
    else:
        if not use_csv:
            print("TMCC Decoder - interactive mode (q to quit)")
        while True:
            try:
                raw = input("" if use_csv else "Enter hex bytes: ").strip()
                if raw.lower() in ('q', 'quit', 'exit'):
                    break
                if raw:
                    decode(raw)
            except (KeyboardInterrupt, EOFError):
                break