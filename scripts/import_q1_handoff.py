#!/usr/bin/env python3
"""Import the SHA-bound RC3 handoff into a new branch; never change main in place.

Default is read-only. --apply stages the exact reviewed import; --push also
commits and pushes the new branch using the caller's existing Git credentials.
No embedded Python script is executed. No review/publication flag is promoted.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import zipfile

BASE = '4a01bb99b08e85bbe01036eda88bf34e986ef6cf'
BASE_TREE = '12a1d1170ffd83ec01874795067fa0f237abb4be'
RESULT_TREE = '2d3a9d13585904b6dd80b4f10f0401e89a04c5ec'
PDF_SHA = '45c399e387d767554e5c2f56e91a00a8dfce1317f9a0fec9e15b4006d03bb0d6'
ZIP_SHA = 'e2ab136d418da74f1ebd4adc7fada27df4c63bd3e31f87d7421b0968e055128e'
PATCH_SHA = '4268079d82ebf963794836e32bf6d874676b34518fd379f7e2fba63112ee1672'
EXTRAS = {'scripts/import_q1_handoff.py', 'scripts/test_q1_handoff_loader.py',
          'docs/Q1_IMPORT_READY.md', 'data/q1_import_receipt.json',
          '.github/workflows/q1-handoff-loader.yml'}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def run(repo: Path, *args: str, env=None) -> str:
    result = subprocess.run(['git', *args], cwd=repo, env=env,
                            check=False, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError('git ' + args[0] + ' failed: ' + result.stderr.strip())
    return result.stdout.strip()


def tree_entries(repo: Path, ref: str, env=None) -> dict[str, tuple[str, str]]:
    raw = subprocess.check_output(['git', 'ls-tree', '-rz', ref], cwd=repo, env=env)
    result = {}
    for row in raw.split(b'\0'):
        if not row:
            continue
        header, name = row.split(b'\t', 1)
        mode, kind, sha = header.decode().split()
        require(kind == 'blob', 'Submodules are not supported by this import')
        result[name.decode('utf-8')] = (mode, sha)
    return result


def check_extension(base: dict, current: dict) -> dict:
    require(all(current.get(k) == v for k, v in base.items()),
            'Existing baseline files changed; reconcile instead of force-applying')
    extras = {k: v for k, v in current.items() if k not in base}
    require(set(extras) <= EXTRAS, 'Unexpected files were added after the baseline')
    return extras


def decode_handoff(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    require(len(raw) <= 25_000_000, 'Unexpectedly large handoff file')
    if raw.startswith(b'%PDF-'):
        require(digest(raw) == PDF_SHA, 'Wrong handoff PDF bytes')
        from pypdf import PdfReader
        attachments = PdfReader(io.BytesIO(raw)).attachments
        values = attachments.get('Q1-repository-handoff.zip', [])
        require(len(values) == 1, 'Missing or duplicated handoff ZIP')
        raw = values[0]
    require(digest(raw) == ZIP_SHA, 'Handoff ZIP hash mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        require(len(names) == len(set(names)) == 7, 'Unexpected ZIP members')
        require(all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts
                    and '\\' not in n for n in names), 'Unsafe ZIP path')
        require(sum(i.file_size for i in infos) < 30_000_000, 'Unexpected ZIP expansion')
        metadata = json.loads(archive.read('handoff.json'))
        patch = archive.read('q1-import.patch')
    require(digest(patch) == PATCH_SHA, 'Binary patch hash mismatch')
    require(metadata['repository'] == 'netplus/zitie' and metadata['expected_base_tree'] == BASE_TREE
            and metadata['result_tree'] == RESULT_TREE and metadata['file_count'] == 25,
            'Unexpected handoff contract')
    return metadata, patch


def import_package(repo: Path, handoff: Path, branch: str, apply: bool, push: bool) -> dict:
    repo = repo.resolve()
    require(not push or apply, '--push requires --apply')
    run(repo, 'check-ref-format', '--branch', branch)
    require(branch not in {'main', 'master'}, 'Use a new non-main branch')
    require(not run(repo, 'status', '--porcelain'), 'Worktree is not clean')
    require(run(repo, 'rev-parse', BASE + '^{tree}') == BASE_TREE, 'Wrong historical base tree')
    current_head = run(repo, 'rev-parse', 'HEAD')
    base, current = tree_entries(repo, BASE), tree_entries(repo, 'HEAD')
    extras = check_extension(base, current)
    metadata, patch = decode_handoff(handoff)
    with tempfile.TemporaryDirectory(prefix='q1-exact-import-') as temp:
        patch_path = Path(temp)/'import.patch'; patch_path.write_bytes(patch)
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp)/'index'))
        run(repo, 'read-tree', BASE_TREE, env=env)
        run(repo, 'apply', '--cached', str(patch_path), env=env)
        require(run(repo, 'write-tree', env=env) == RESULT_TREE, 'Historical patch result differs')
        for path, (mode, sha) in sorted(extras.items()):
            run(repo, 'update-index', '--add', '--cacheinfo', mode, sha, path, env=env)
        expected = run(repo, 'write-tree', env=env)
        run(repo, 'apply', '--check', '--index', str(patch_path))
        result = {'patch_checked': True, 'historical_import_tree': RESULT_TREE,
                  'expected_tree_with_loader': expected, 'source_HEAD': current_head,
                  'applied': False, 'pushed': False, 'published': False}
        if not apply:
            return result
        if push:
            remote = run(repo, 'remote', 'get-url', 'origin').rstrip('/')
            require(remote in {'https://github.com/netplus/zitie', 'https://github.com/netplus/zitie.git',
                               'git@github.com:netplus/zitie.git', 'ssh://git@github.com/netplus/zitie.git'},
                    'origin must be the intended netplus/zitie repository')
            require(not run(repo, 'ls-remote', '--heads', 'origin', 'refs/heads/' + branch),
                    'Remote branch already exists; use a different new branch name')
        require(run(repo, 'rev-parse', 'HEAD') == current_head, 'HEAD changed during validation')
        run(repo, 'switch', '-c', branch)
        run(repo, 'apply', '--index', str(patch_path))
        require(run(repo, 'write-tree') == expected, 'Unexpected applied tree; preserve for review')
        require(set(run(repo, 'diff', '--cached', '--name-only').splitlines()) == set(metadata['files']),
                'Unexpected changed-file set')
        result.update(applied=True, branch=branch)
        if push:
            run(repo, 'commit', '-m', 'Q1: import exact locally reviewed RC2/RC3 bytes and evidence')
            run(repo, 'push', '-u', 'origin', branch)
            result.update(pushed=True, commit=run(repo, 'rev-parse', 'HEAD'))
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--handoff', type=Path, required=True)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--branch', default='maintenance/q1-reviewed-pdf-import-20261008')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--push', action='store_true')
    args = parser.parse_args()
    print(json.dumps(import_package(args.repo, args.handoff, args.branch, args.apply, args.push),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
