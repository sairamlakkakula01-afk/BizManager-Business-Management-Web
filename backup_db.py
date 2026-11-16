#!/usr/bin/env python3
"""
BizManager Database Backup & Restore Utility
Uses SQLite's online backup API for safe, non-blocking transactional backups.
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / 'instance' / 'bizmanager.db'
BACKUP_DIR = BASE_DIR / 'instance' / 'backups'


def perform_backup():
    """Create a point-in-time timestamped backup of the SQLite database."""
    if not DB_FILE.exists():
        print(f"Error: Database file not found at {DB_FILE}")
        sys.exit(1)

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f"bizmanager_backup_{timestamp}.sqlite3"

    print(f"Connecting to source database: {DB_FILE}")
    src_conn = sqlite3.connect(DB_FILE)
    dst_conn = sqlite3.connect(backup_file)

    try:
        # SQLite online backup API ensures transactional consistency
        with dst_conn:
            src_conn.backup(dst_conn, pages=100)
        print(f"✓ Backup completed successfully!")
        print(f"  Backup saved to: {backup_file}")
        print(f"  File size: {backup_file.stat().st_size} bytes")
    finally:
        dst_conn.close()
        src_conn.close()


def perform_restore(backup_path: str):
    """Restore the database from a specified backup file."""
    src_path = Path(backup_path)
    if not src_path.exists():
        print(f"Error: Backup file does not exist at {src_path}")
        sys.exit(1)

    # Make a temporary safety copy of the current db before overwriting
    if DB_FILE.exists():
        safety_copy = BASE_DIR / 'instance' / f"bizmanager_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DB_FILE, safety_copy)
        print(f"Safety copy of current database created at {safety_copy}")

    shutil.copy2(src_path, DB_FILE)
    print(f"✓ Database restored successfully from {src_path}!")


def list_backups():
    """List all available backup archives."""
    if not BACKUP_DIR.exists():
        print("No backups directory found.")
        return

    backups = sorted(BACKUP_DIR.glob("*.sqlite3"), key=os.path.getmtime, reverse=True)
    if not backups:
        print("No backups available.")
        return

    print("Available Database Backups:")
    for b in backups:
        mtime = datetime.fromtimestamp(b.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        size_kb = b.stat().st_size / 1024
        print(f" - {b.name} ({size_kb:.1f} KB, Created: {mtime})")


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'backup':
        perform_backup()
    elif sys.argv[1] == 'list':
        list_backups()
    elif sys.argv[1] == 'restore':
        if len(sys.argv) < 3:
            print("Usage: python scripts/backup_db.py restore <path_to_backup_file>")
            sys.exit(1)
        perform_restore(sys.argv[2])
    else:
        print("Usage:")
        print("  python scripts/backup_db.py backup    # Create new backup")
        print("  python scripts/backup_db.py list      # List backups")
        print("  python scripts/backup_db.py restore <file> # Restore database")
