#!/usr/bin/env python3
"""Verify formal M1 preflight bytes, not permission to publish them."""
import argparse
import json
from pathlib import Path
from verify_patch_candidate import ROOT, verify

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT/'build/v0.4.1')
    print(json.dumps(verify(parser.parse_args().directory, expected_mode='formal'),
                     ensure_ascii=False, indent=2))
