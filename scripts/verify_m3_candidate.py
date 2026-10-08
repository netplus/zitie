#!/usr/bin/env python3
"""Verify every module and navigation in the candidate, not full visual QA."""
import argparse
import json
from pathlib import Path
from m3_candidate import CandidateEdition
from m3_model import ROOT
from verify_m3_preview import verify

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT/'build/v0.5.0-rc1')
    print(json.dumps(verify(parser.parse_args().directory, edition=CandidateEdition()), ensure_ascii=False, indent=2))
