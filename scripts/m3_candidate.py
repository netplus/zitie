#!/usr/bin/env python3
"""Strict candidate-only edition and preflight contract; no publication grant."""
import copy
import re
from dataclasses import dataclass
from pathlib import Path
from m3_model import M3Edition, validate_config as validate_preview_config
from verify_m2_closeout import require

CONFIG = 'data/m3_candidate.json'
VERSION = '0.5.0-rc1'


@dataclass(frozen=True)
class CandidateEdition(M3Edition):
    @property
    def identifier(self):
        return VERSION

    @property
    def label(self):
        return '发布候选 v' + self.identifier


def validate_config(config):
    require(config['status'] == 'candidate_preflight', 'Wrong candidate mode')
    require(config['guidance'] == 'book/front-matter/m3-candidate-guidance.json',
            'Candidate needs mode-specific guidance')
    normalized = copy.deepcopy(config)
    normalized['status'] = 'engineering_preview'
    validate_preview_config(normalized)
    return config


def validate_ready(scope):
    packages = scope['work_packages']
    require([p['id'] for p in packages] == [f'F{i:02}' for i in range(1, 6)]
            and all(p['status'] == 'completed' and p.get('completion_record') for p in packages)
            and scope['features_completed'] == 5, 'All five implemented packages required')
    require(len(scope['comparison_pairs']) == len(scope['migration_cases']) == 6
            and all(p['status'] == 'completed' for p in scope['comparison_pairs'] + scope['migration_cases']),
            'All supplementary modules must be implemented')
    return True


def validate_metadata(meta):
    # Reuse full geometry/coverage checks without allowing preview promotion.
    from verify_m3_preview import validate_metadata as validate_preview_metadata
    require(meta['version'] == VERSION and meta['status'] == 'candidate_generated_not_archived',
            'Not a freshly generated candidate')
    require(meta['pdf'] == 'zitie-v' + VERSION + '.pdf', 'Wrong candidate filename')
    require(meta['source_dirty'] is False, 'Dirty source is not a frozen candidate source')
    for key in ('source_commit', 'source_tree'):
        require(re.fullmatch(r'[0-9a-f]{40}', meta[key]), 'Exact Git provenance required: ' + key)
    require(meta['config_path'] == CONFIG and CONFIG in meta['input_sha256'], 'Candidate configuration not bound')
    require(meta['pages'] == 299 and meta['guide_pages'] == 2 and meta['toc_pages'] == 3,
            'Candidate structure changed')
    require(len(meta['bookmarks']) == 238 and len(meta['toc_links']) == 34,
            'Incomplete candidate navigation')
    require(len(meta['fonts']) == 3 and all(re.fullmatch(r'[0-9a-f]{64}', f['sha256']) for f in meta['fonts']),
            'Missing font fingerprints')
    require(set(meta['environment']['packages']) == {'reportlab', 'pypdf', 'fonttools'},
            'Incomplete rendering environment')
    for path, sha in meta['input_sha256'].items():
        p = Path(path)
        require(not p.is_absolute() and '..' not in p.parts and re.fullmatch(r'[0-9a-f]{64}', sha),
                'Unsafe or unbound candidate input')
    normalized = copy.deepcopy(meta)
    normalized.update(version='0.5.0-dev2', status='engineering_preview')
    validate_preview_metadata(normalized)
    return True
