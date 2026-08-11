from src.database.db_connection import get_connection


def main():
    conn = get_connection()

    print("Connected successfully!")

    cur = conn.cursor()

    cur.execute("SELECT version();")

    print(cur.fetchone())

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()