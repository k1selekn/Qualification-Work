import os
import pyodbc
from configparser import ConfigParser
import pandas as pd

cfg = ConfigParser()
cfg.read(os.getenv('DB_CONFIG_FILE', 'ecom_db.ini'))
db_conf = cfg['database']

class ReadOnlyDatabase:
    default_params = {
        'server'     : db_conf.get('server'),
        'database'   : db_conf.get('database'),
        'driver'     : db_conf.get('driver'),
        'instance'   : db_conf.get('instance') or None,
        'port'       : db_conf.getint('port'),
        'trusted'    : db_conf.getboolean('trusted'),
        'uid'        : db_conf.get('uid') or None,
        'pwd'        : db_conf.get('pwd') or None,
        'autocommit' : True,
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
        """
        Выполнить SELECT-запрос и вернуть список словарей: [{col: value, …}, …]
        """
        cur = self._conn.cursor()
        cur.execute(sql, params or ())
        cols = [col[0] for col in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def to_df(self, sql: str, params: tuple = None) -> pd.DataFrame:
        """
        Выполнить SELECT и сразу получить pandas.DataFrame
        """
        return pd.read_sql_query(sql, self._conn, params=params)

    def close(self):
        """Закрыть соединение."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()