import os
import pyodbc
import pandas as pd
from config import load_config

cfg = load_config()
ecom_conf = cfg.ecom_db

class ReadOnlyDatabase:
    default_params = {
        'server'     : ecom_conf.server,
        'database'   : ecom_conf.database,
        'driver'     : ecom_conf.driver,
        'instance'   : ecom_conf.instance or None,
        'port'       : ecom_conf.port,
        'trusted'    : ecom_conf.trusted,
        'uid'        : ecom_conf.uid or None,
        'pwd'        : ecom_conf.pwd or None,
        'autocommit' : ecom_conf.autocommit,
    }

    def __init__(self, **overrides):
        params = {**self.default_params, **overrides}

        server   = params['server']
        database = params['database']
        driver   = params['driver']
        instance = params['instance']
        port     = params['port']
        trusted  = params['trusted']
        uid      = params['uid']
        pwd      = params['pwd']
        autocommit = params['autocommit']

        if instance:
            server_part = f"{server}\\{instance}"
        else:
            server_part = f"{server},{port}"

        parts = [
            f"DRIVER={{{driver}}}",
            f"SERVER={server_part}",
            f"DATABASE={database}",
        ]
        if trusted:
            parts.append("Trusted_Connection=yes")
        else:
            if not (uid and pwd):
                raise ValueError("Для SQL Authentication нужны uid и pwd")
            parts.extend([f"UID={uid}", f"PWD={pwd}"])

        parts.append("TrustServerCertificate=yes")
        self._conn_str = ";".join(parts)

        self._conn = pyodbc.connect(self._conn_str, autocommit=autocommit)

    def query(self, sql: str, params: tuple = None) -> list[dict]:
        cur = self._conn.cursor()
        cur.execute(sql, params or ())
        cols = [col[0] for col in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def to_df(self, sql: str, params: tuple = None) -> pd.DataFrame:
        return pd.read_sql_query(sql, self._conn, params=params)

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()