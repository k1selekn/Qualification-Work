# config.py
import os
import yaml
from pydantic import BaseModel, Field, field_validator, HttpUrl


def load_config(path: str = None) -> 'AppConfig':
    default_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml')
    )
    config_path = path or default_path

    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return AppConfig(**data)


class DBConfig(BaseModel):
    server: str
    database: str
    driver: str
    instance: str = Field('', description="ODBC instance name, if any")
    port: int = Field(1433, ge=1, le=65535)
    trusted: bool
    uid: str = Field('', description="Username for authentication (if not trusted)")
    pwd: str = Field('', description="Password for authentication (if not trusted)")
    autocommit: bool

    @field_validator('server', 'database', 'driver')
    def not_empty(cls, v, info):
        if not v or not str(v).strip():
            raise ValueError(f"{info.field_name} must not be empty")
        return v


class PathsConfig(BaseModel):
    input_folder: str
    output_folder: str
    logs_folder: str

    @field_validator('*')
    def ensure_folder(cls, v, info):
        abs_path = os.path.abspath(v)
        try:
            os.makedirs(abs_path, exist_ok=True)
        except Exception:
            raise ValueError(f"Cannot create or access path for {info.field_name}: {abs_path}")
        return abs_path


class APIConfig(BaseModel):
    base_url: HttpUrl = Field(..., description="Базовый URL сервиса API")
    api_key: str    = Field(..., description="Секретный ключ для доступа к API")

class AdminConfig(BaseModel):
    login: str    = Field(..., description="Логин")
    password: str    = Field(..., description="Пароль")

class AppConfig(BaseModel):
    db: DBConfig
    ecom_db: DBConfig
    paths: PathsConfig
    api: APIConfig
    admin: AdminConfig

app_config = load_config()