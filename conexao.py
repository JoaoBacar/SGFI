import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Satson18*",  # <--- Altere para a sua senha do MySQL
    "port": 3306
}

def conectar(usar_banco=True):
    config = DB_CONFIG.copy()
    if usar_banco:
        config["database"] = "sgfi"
    return mysql.connector.connect(**config)