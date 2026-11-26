import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("game.db")
SQL_PATH = Path(__file__).with_name("database.sql")

def main():
    sql_script = SQL_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(sql_script)
    print(f"Databaze vytvorena: {DB_PATH}")

if __name__ == "__main__":
    main()
