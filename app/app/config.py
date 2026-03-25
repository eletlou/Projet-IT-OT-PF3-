import os


class Config:
    SECRET_KEY = os.getenv("SESSION_SECRET", "dev_secret_key")
    APP_NAME = "Les Viviers de Noirmoutier"
    APP_SUBTITLE = "Supervision de production et maintenance"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"

    MYSQL_HOST = os.getenv("MYSQL_HOST", "db")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "les_viviers_de_noirmoutier")
