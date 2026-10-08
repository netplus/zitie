#!/usr/bin/env python3
"""Generate a clean-source full candidate; freezing/archival is a separate step."""
import argparse
from build_m3_preview import build
from m3_candidate import CandidateEdition, CONFIG, validate_config

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', default='/usr/share/fonts/truetype/arphic-gkai00mp/gkai00mp.ttf')
    parser.add_argument('--latin-font', default='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    parser.add_argument('--variant-font', default='/usr/share/fonts/truetype/arphic/uming.ttc')
    build(parser.parse_args(), edition=CandidateEdition(), config_path=CONFIG, config_validator=validate_config)
