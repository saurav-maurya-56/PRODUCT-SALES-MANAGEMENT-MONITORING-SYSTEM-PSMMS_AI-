# config.py
# MySQL connection config.
# Edit these values to match your local MySQL server.


DB_CONFIG = {
"host": "localhost",
"user": "root",
"password": "saurav12",
"database": "psmms_db",
"port": 3306,
}


# Ollama config
OLLAMA = {
"host": "http://localhost:11434",
# No authentication assumed for local Ollama. Change if needed.
"default_model": "mistral",
}


# Export filenames
EXPORT_CSV = "sales_data.csv"
EXPORT_TXT = "sales_data.txt"