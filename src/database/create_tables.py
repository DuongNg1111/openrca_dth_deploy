import os

from src.database.connection import get_connection
from src.database.table_schemas import TABLE_SCHEMAS


def create_sql(table_name, schema):

    columns = []

    for name, dtype in schema["columns"].items():

        columns.append(
            f"{name} {dtype}"
        )


    return f"""
    CREATE TABLE IF NOT EXISTS {table_name}
    (
        {",".join(columns)}
    );
    """



def create_tables():

    conn = get_connection()

    cur = conn.cursor()


    for table, schema in TABLE_SCHEMAS.items():

        print("Creating:", table)

        cur.execute(
            create_sql(table, schema)
        )


    conn.commit()

    cur.close()

    conn.close()


    print("Database initialized")



if __name__ == "__main__":
    if os.getenv("OPENRCA_RUN_MUTATING_TESTS") != "1":
        raise SystemExit(
            "Set OPENRCA_RUN_MUTATING_TESTS=1 to initialize the configured database."
        )
    create_tables()
