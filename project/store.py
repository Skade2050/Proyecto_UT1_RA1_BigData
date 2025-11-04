# project/store.py
import sqlite3
from pathlib import Path

def save_to_sqlite(df, db_path="project/encuestas.db", table="raw_encuestas"):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    df.to_sql(table, con, if_exists="replace", index=False)
    con.close()

def save_table_sqlite(df, table, db_path="project/encuestas.db"):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    df.to_sql(table, con, if_exists="replace", index=False)
    con.close()

def save_parquet(df, path):
    from pathlib import Path
    import pyarrow as pa
    import pyarrow.parquet as pq
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    # fuerza strings para columnas object (evita problemas)
    df2 = df.copy()
    for c in df2.columns:
        if df2[c].dtype == "object":
            df2[c] = df2[c].astype("string")
    table = pa.Table.from_pandas(df2, preserve_index=False)
    pq.write_table(table, path)
