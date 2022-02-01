import os
import sqlite3 as sl
from typing import Dict, List, Tuple, Any
import pandas as pd


def get_database_connection(config: Dict[str, Any],
                            db_filename: str = "qdd_debugging.db"):
    """Get the database."""
    DB_PATH = os.path.join(config['experiment_folder'], db_filename)
    return sl.connect(DB_PATH)


def update_database(
        con: sl.Connection,
        table_name: str,
        record: Dict[str, Any]):
    """Update the RERUN database with the following result."""
    df_single = pd.json_normalize([record])
    dict_is_col_list = (df_single.applymap(type) == list).all()
    for c in df_single.columns:
        if dict_is_col_list[c]:
            df_single[c] = df_single[c].astype('str')
    df_single.to_sql(table_name, con, if_exists='append')


def get_program_ids_in_table(con: sl.Connection, table_name: str):
    """Get the program ids in the passed table of the database connection."""
    table_exists = (con.cursor().execute(f"""
        SELECT tbl_name FROM sqlite_master WHERE type='table'
        AND tbl_name='{table_name}';
    """).fetchall())
    if not table_exists:
        return []
    present_program_id = pd.read_sql(f'''
        SELECT DISTINCT program_id
        FROM {table_name}
    ''', con)
    return list(present_program_id["program_id"])

