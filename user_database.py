import aiosqlite

class UserDatabase:
    def __init__(self, db_path: str = 'user_data.db'):
        """
        Initialisiert die UserDatabase.
        Args:
            db_path (str): Der Pfad zur SQLite-Datenbankdatei.
        """
        self.db_path = db_path

    async def connect(self):
        """Stellt eine asynchrone Verbindung zur Datenbank her."""
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                subscription_type TEXT,
                subscription_start_date TEXT,
                subscription_end_date TEXT
            )
        """)
        await self.conn.commit()

    async def close(self):
        """Schließt die Datenbankverbindung."""
        if self.conn:
            await self.conn.close()

    async def get_user(self, user_id: int) -> dict | None:
        """
        Ruft Benutzerdaten anhand der user_id ab.
        Args:
            user_id (int): Die ID des Benutzers.
        Returns:
            dict | None: Ein Wörterbuch mit Benutzerdaten oder None, wenn der Benutzer nicht gefunden wird.
        """
        async with self.conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                # Annahme der Spaltenreihenfolge
                return {
                    "user_id": row[0],
                    "username": row[1],
                    "subscription_type": row[2],
                    "subscription_start_date": row[3],
                    "subscription_end_date": row[4]
                }
            return None

    async def add_user(self, user_id: int, username: str):
        """
        Fügt einen neuen Benutzer zur Datenbank hinzu.
        Args:
            user_id (int): Die ID des Benutzers.
            username (str): Der Benutzername.
        """
        await self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await self.conn.commit()

    async def update_user_subscription(self, user_id: int, subscription_type: str, subscription_end_date: str):
        """
        Aktualisiert das Abonnement eines Benutzers in der Datenbank.
        Args:
            user_id (int): Die ID des Benutzers.
            subscription_type (str): Der Typ des Abonnements.
            subscription_end_date (str): Das Enddatum des Abonnements im Format 'YYYY-MM-DD'.
        """
        await self.conn.execute(
            """
            UPDATE users
            SET subscription_type = ?, subscription_end_date = ?
            WHERE user_id = ?
            """,
            (subscription_type, subscription_end_date, user_id)
        )
        await self.conn.commit()

