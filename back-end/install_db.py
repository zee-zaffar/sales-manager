"""
Create or upgrade the Sales Manager database schema.

Usage (from the back-end folder, with the venv active):
    python install_db.py            # create DB if needed, apply all pending migrations
    python install_db.py --seed     # ...and also load the optional sample data (02_seed_data.sql)
    python install_db.py --status   # show applied / pending migrations, change nothing

Connection comes from DATABASE_URL (back-end/.env, or the environment), e.g.
    DATABASE_URL=postgresql://user:password@localhost:5432/sales_manager

Safe to re-run: applied migrations are recorded in the schema_migrations
table and skipped. db/03_drop_tables.sql is deliberately never run.
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

HERE = Path(__file__).resolve().parent
DB_DIR = HERE / 'db'
SEED_FILE = '02_seed_data.sql'


def migration_files():
    """db/NN_name.sql in numeric order, excluding the optional seed and anything destructive."""
    files = sorted(p for p in DB_DIR.glob('[0-9][0-9]_*.sql'))
    return [p for p in files if p.name != SEED_FILE and 'drop' not in p.name.lower()]


def parse_url(url):
    u = urlparse(url)
    if u.scheme not in ('postgresql', 'postgres') or not u.path.strip('/'):
        sys.exit('DATABASE_URL must look like postgresql://user:password@host:port/dbname')
    return dict(host=u.hostname or 'localhost', port=u.port or 5432, user=unquote(u.username or ''),
                password=unquote(u.password or ''), dbname=u.path.lstrip('/'))


def ensure_database(p):
    try:
        psycopg2.connect(**p).close()
        return
    except psycopg2.OperationalError as e:
        if 'does not exist' not in str(e):
            sys.exit(f'Could not connect to PostgreSQL at {p["host"]}:{p["port"]} as "{p["user"]}":\n{e}')
    print(f'Database "{p["dbname"]}" does not exist - creating it')
    try:
        admin = psycopg2.connect(**{**p, 'dbname': 'postgres'})
        admin.autocommit = True
        admin.cursor().execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(p['dbname'])))
        admin.close()
    except psycopg2.Error as e:
        sys.exit(
            f'Could not create database "{p["dbname"]}": {str(e).strip()}\n'
            f'Create it once as a Postgres superuser, then re-run this script:\n'
            f'    CREATE DATABASE {p["dbname"]} OWNER {p["user"]};')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--seed', action='store_true', help='also load optional sample data')
    ap.add_argument('--status', action='store_true', help='list applied/pending migrations and exit')
    args = ap.parse_args()

    load_dotenv(HERE / '.env')
    url = os.getenv('DATABASE_URL')
    if not url:
        sys.exit('DATABASE_URL is not set. Copy .env.example to .env and edit it.')
    p = parse_url(url)

    files = migration_files()

    if not args.status:
        ensure_database(p)
    conn = psycopg2.connect(**p)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS schema_migrations ('
                'filename TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())')
    conn.commit()
    cur.execute('SELECT filename FROM schema_migrations')
    applied = {r[0] for r in cur.fetchall()}

    if args.status:
        for f in files:
            print(('applied  ' if f.name in applied else 'PENDING  ') + f.name)
        return

    pending = [f for f in files if f.name not in applied]
    if not pending:
        print('Schema is up to date.')
    for f in pending:
        print(f'Applying {f.name}')
        try:
            cur.execute(f.read_text(encoding='utf-8-sig'))
            cur.execute('INSERT INTO schema_migrations (filename) VALUES (%s)', (f.name,))
            conn.commit()          # one transaction per migration
        except psycopg2.Error as e:
            conn.rollback()
            sys.exit(f'FAILED on {f.name}: {str(e).strip()}\nNothing from this file was applied.')

    if args.seed:
        cur.execute('SELECT count(*) FROM products')
        if cur.fetchone()[0]:
            print('Skipping seed: products table already has data.')
        else:
            print(f'Loading {SEED_FILE}')
            cur.execute((DB_DIR / SEED_FILE).read_text(encoding='utf-8-sig'))
            conn.commit()

    print(f'Done. Database "{p["dbname"]}" on {p["host"]}:{p["port"]} is ready.')


if __name__ == '__main__':
    main()
