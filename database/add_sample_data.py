
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("game.db")


def main():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        # Vlozeni ukazkovych hracu
        connection.executemany(
            """
            INSERT OR IGNORE INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            [
                ("Player1", "demo_hash_not_for_login"),
                ("Player2", "demo_hash_not_for_login"),
                ("Player3", "demo_hash_not_for_login"),
            ],
        )

        # Vlozeni ukazkovych vysledku
        count = connection.execute(
            "SELECT COUNT(*) FROM scores"
        ).fetchone()[0]

        if count == 0:
            sample_scores = [
                ("Player1", 15),
                ("Player1", 23),
                ("Player2", 18),
                ("Player2", 31),
                ("Player3", 12),
            ]

            for username, score in sample_scores:
                connection.execute(
                    """
                    INSERT INTO scores (user_id, score)
                    SELECT id, ?
                    FROM users
                    WHERE username = ?
                    """,
                    (score, username),
                )

    print("Vzorova data byla vlozena!")


if __name__ == "__main__":
    main()
