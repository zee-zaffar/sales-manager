# from typing import Iterator, Optional
# import os
# import contextlib

# from dotenv import load_dotenv
# load_dotenv()

# import psycopg2
# import psycopg2.extras

# def test_postgres_connection():
#     # connection parameters
#     conn = psycopg2.connect(
#         dbname = os.
#         user= "postgres",
#         password= "DanFay29$1",
#         host="127.0.0.1",   # or remote IP
#         port="5432"         # default Postgres port
#     )

#     # create a cursor
#     cur = conn.cursor()

#     # execute SQL
#     cur.execute("SELECT version();")

#     # fetch result
#     db_version = cur.fetchone()
#     print("PostgreSQL version:", db_version)

#     # close connection
#     cur.close()
#     conn.close()

# test_postgres_connection()