import os
import pyodbc
from config import load_config

cfg = load_config()
db_conf = cfg.db

class Database:
    default_params = {
        'server'     : db_conf.server,
        'database'   : db_conf.database,
        'driver'     : db_conf.driver,
        'instance'   : db_conf.instance or None,
        'port'       : db_conf.port,
        'trusted'    : db_conf.trusted,
        'uid'        : db_conf.uid or None,
        'pwd'        : db_conf.pwd or None,
        'autocommit' : db_conf.autocommit,
    }

    def __init__(self, **kwargs):
        params = {**self.default_params, **kwargs}

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
        self._autocommit = autocommit
        self._conn = None
        self._cursor = None

    def connect(self):
        self._conn = pyodbc.connect(self._conn_str, autocommit=self._autocommit)
        self._cursor = self._conn.cursor()
        return self._cursor

    def execute(self, query: str, params: tuple = None):
        if self._conn is None:
            self.connect()
        return self._cursor.execute(query, params) if params else self._cursor.execute(query)

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchone(self):
        return self._cursor.fetchone()

    def commit(self):
        if self._conn and not self._autocommit:
            self._conn.commit()

    def rollback(self):
        if self._conn:
            self._conn.rollback()

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
        self._conn = None
        self._cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()