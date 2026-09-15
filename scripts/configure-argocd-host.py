#!/usr/bin/env python3
"""Add the lab's Argo CD hostname to /etc/hosts without replacing existing entries."""
import os
from pathlib import Path
import shutil


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run this script with sudo to update /etc/hosts.')
    hosts = Path('/etc/hosts')
    hostname = 'argocd.platform.test'
    address = '127.0.0.1'
    content = hosts.read_text()
    matches = []
    for line in content.splitlines():
        fields = line.split('#', 1)[0].split()
        if hostname in fields[1:]:
            matches.append(fields[0])
    if matches:
        if any(ip != address for ip in matches):
            raise SystemExit('Conflicting existing hostname entry; no changes made.')
        print('Hostname already configured: https://argocd.platform.test:8443')
        return
    backup = Path('/etc/hosts.platform-lab.bak')
    if not backup.exists():
        shutil.copy2(hosts, backup)
    with hosts.open('a') as output:
        if content and not content.endswith('\n'):
            output.write('\n')
        output.write(f'{address} {hostname}\n')
    print('Configured: https://argocd.platform.test:8443')


if __name__ == '__main__':
    main()
