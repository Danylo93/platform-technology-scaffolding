#!/usr/bin/env python3
"""Render the Node Golden Path into a new directory."""
import argparse
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', help='Lowercase Kubernetes-compatible service name')
    parser.add_argument('--owner', required=True, help='GitHub repository owner')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--init-git', action='store_true', help='Commit main and create deployment_files')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*', args.name) or len(args.name) > 48:
        parser.error('name must use lowercase letters, digits and internal hyphens; max 48 characters')
    if not re.fullmatch(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', args.owner) or len(args.owner) > 39:
        parser.error('invalid GitHub owner')
    if args.output.exists():
        parser.error('output already exists; no files were changed')
    skeleton = Path(__file__).resolve().parents[1] / 'templates/node-api/skeleton'
    substitutions = {
        '__SERVICE_NAME__': args.name,
        '__GITHUB_OWNER__': args.owner,
        '__PIPELINE_SHA__': '88551206a068985b1801befd0fc66465eb12a228',
    }
    files = {}
    for source in skeleton.rglob('*'):
        if not source.is_file() or 'openshift' in source.relative_to(skeleton).parts:
            continue
        content = source.read_text()
        for key, value in substitutions.items():
            content = content.replace(key, value)
        if re.search(r'__[A-Z_]+__', content):
            raise ValueError(f'Unresolved template token in {source.name}')
        files[source.relative_to(skeleton)] = content
    args.output.mkdir(parents=True)
    for relative, content in files.items():
        destination = args.output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
    if args.init_git:
        for command in (
            ['git', 'init', '-b', 'main'],
            ['git', 'add', '.'],
            ['git', 'commit', '-m', 'feat: scaffold Node service with platform golden path'],
            ['git', 'branch', 'deployment_files'],
            ['git', 'remote', 'add', 'origin', f'git@github.com:{args.owner}/{args.name}.git'],
        ):
            subprocess.run(command, cwd=args.output, check=True)
    print(f'Created {len(files)} files in {args.output.resolve()}')


if __name__ == '__main__':
    main()
