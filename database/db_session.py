# import psycopg2
# from psycopg2.extensions import connection as _pg_conn

# def create_session() -> _pg_conn:
#     try:
#         connection = psycopg2.connect(
#             host="localhost",
#             database="danfay",
#             user="postgres",
#             password="DanFay29$1"
#         )
#         return connection
#     except psycopg2.Error as db_error:
#         print(f"Database Error: {db_error}")
#         return None
#     except Exception as error:
#         print(f"General Exception Error:{error}")
#         return None