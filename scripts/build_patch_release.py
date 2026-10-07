#!/usr/bin/env python3
"""Build M1 formal preflight bytes; generation does not grant release approval."""
from build_patch_candidate import main

if __name__ == '__main__':
    main(mode='formal')
