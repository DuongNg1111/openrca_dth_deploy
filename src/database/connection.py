import psycopg2


def get_connection():

    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="openrca",
        user="postgres",
        password="DTH123"
    )

    return conn


if __name__ == "__main__":

    conn = get_connection()

    print("Database connection: OK")

    conn.close()