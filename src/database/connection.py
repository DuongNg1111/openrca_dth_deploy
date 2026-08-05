import psycopg2

from src.config import load_config


def get_connection():

    cfg = load_config()
    db = cfg["database"]

    conn = psycopg2.connect(

        host=db["host"],

        port=db["port"],

        database=db["database"],

        user=db["user"],

        password=db["password"]

    )

    return conn


if __name__ == "__main__":

    conn = get_connection()

    print("Database connection: OK")

    conn.close()