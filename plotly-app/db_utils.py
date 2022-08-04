import pandas as pd
import psycopg2

def load_data_from_psql(query: str, columns=None, **kwargs) -> pd.DataFrame:
    # todo: reuse connection maybe?
    with psycopg2.connect(
        database="webvalley2022", user='postgres',
        password='postgres',
        host='localhost', port='5432'
    ) as conn:
        with conn.cursor() as curs:
            curs.execute(query)
            result = curs.fetchall()
            if columns is None:
                columns = [desc[0] for desc in curs.description]
    # for some reason exiting the connection’s with block doesn’t close the connection automatically
    conn.close()
    return pd.DataFrame(result, columns=columns, **kwargs)
