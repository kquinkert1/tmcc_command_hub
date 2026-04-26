#!/usr/bin/env python3
"""
Decode TMCC command bytes. Pass two hex bytes (0xFE header assumed).
Usage: python decode.py ABCD
       python decode.py AB CD
       python decode.py -f <filename>
       python decode.py        # interactive mode
"""
import sys
from tmcc.tmcc_command_factory import TMCCCommandFactory


def decode(hex_input):
    # Split on spaces first, then clean each token
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
    result = TMCCCommandFactory.decode(packet)
    print(f"0x{b1:02X} 0x{b2:02X}  {result.description}")


def decode_file(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                decode(line)


if __name__ == '__main__':
    if '-f' in sys.argv:
        idx = sys.argv.index('-f')
        decode_file(sys.argv[idx + 1])
    elif len(sys.argv) > 1:
        decode(' '.join(sys.argv[1:]))
    else:
        print("TMCC Decoder - interactive mode (q to quit)")
        while True:
            try:
                raw = input("Enter hex bytes: ").strip()
                if raw.lower() in ('q', 'quit', 'exit'):
                    break
                if raw:
                    decode(raw)
            except (KeyboardInterrupt, EOFError):
                break