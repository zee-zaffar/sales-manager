import psycopg2
from pathlib import Path
host = 'localhost'
user = 'agent'
password = 'agentpass'
print('Connecting to postgres...')
conn = psycopg2.connect(host=host, user=user, password=password, dbname='postgres')
conn.autocommit = True
cur = conn.cursor()
cur.execute('SELECT 1 FROM pg_database WHERE datname=%s', ('sales_manager',))
exists = cur.fetchone()
if not exists:
    print('Creating database sales_manager')
    cur.execute('CREATE DATABASE sales_manager')
else:
    print('Database sales_manager already exists')
cur.close()
conn.close()
conn = psycopg2.connect(host=host, user=user, password=password, dbname='sales_manager')
cur = conn.cursor()
for fn in ['01_create_tables.sql', '02_seed_data.sql']:
    p = Path('db') / fn
    print(f'Executing {p}')
    sql_text = p.read_text()
    cur.execute(sql_text)
conn.commit()
cur.close()
conn.close()
print('Database schema and seed data installed.')
