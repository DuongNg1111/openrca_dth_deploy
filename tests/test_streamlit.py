if __name__ != "__main__":
    import pytest

    pytest.skip("manual PostgreSQL integration script", allow_module_level=True)

# # from src.database.repository import get_user_incidents

# # df = get_user_incidents(
# #     "nguyensusan1111@gmail.com"
# # )

# # print(df)

# from src.database.connection import get_connection


# conn = get_connection()

# cur = conn.cursor()

# cur.execute("""
# SELECT current_database();
# """)

# print("DATABASE:", cur.fetchone())


# cur.execute("""
# SELECT column_name
# FROM information_schema.columns
# WHERE table_name='investigations';
# """)

# print("COLUMNS:")

# for row in cur.fetchall():
#     print(row)


# conn.close()

from src.database.connection import get_connection

conn = get_connection()

cur = conn.cursor()

cur.execute("""
SELECT
    inet_server_addr(),
    inet_server_port(),
    current_database();
""")

print(cur.fetchone())

conn.close()
