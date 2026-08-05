import os
import psycopg2

from dotenv import load_dotenv

from src.config import load_config


load_dotenv()



def get_connection():

    cfg = load_config()

    db = cfg["database"]


    conn = psycopg2.connect(

        host=db["host"],

        port=db["port"],

        database=db["database"],

        user=db["user"],

        password=os.getenv(
            db["password_env"]
        )
    )

    return conn

if __name__ == "__main__":

    conn = get_connection()

    print(
        "Database connection: OK"
    )

    conn.close()