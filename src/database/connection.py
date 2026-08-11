import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_connection():

    conn = psycopg2.connect(

        host=os.getenv("POSTGRES_HOST"),

        port=os.getenv("POSTGRES_PORT"),

        database=os.getenv("POSTGRES_DB"),

        user=os.getenv("POSTGRES_USER"),

        password=os.getenv("POSTGRES_PASSWORD")

    )

    return conn


if __name__ == "__main__":

    conn = get_connection()

    print("Database connection: OK")

    conn.close()