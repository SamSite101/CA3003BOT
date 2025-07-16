import aiosqlite
from datetime import datetime

class UserDatabase:
    """Verwaltet alle Datenbankoperationen im Zusammenhang mit Nutzern."""
    
    def __init__(self, db_path='bot_users.db'):
        """Initialisiert die Verbindung zur SQLite-Datenbank."""
        self.db_path = db_path

    async def get_user_data(self, user_id: int) -> tuple:
        """
        Holt Benutzerdaten aus der Datenbank.
        
        :param user_id: ID des Nutzers
        :return: Daten des Nutzers
        """
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                user = await cursor.fetchone()
                if not user:
                    await self.create_user(user_id)
                    await cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                    user = await cursor.fetchone()
                return user

    async def create_user(self, user_id: int):
        """
        Erstellt einen neuen Nutzer in der Datenbank.
        
        :param user_id: ID des neuen Nutzers
        """
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''INSERT INTO users (user_id, subscription_type, subscription_expires, daily_requests, last_request_date) 
                                        VALUES (?, 'free', NULL, 0, DATE('now'))''', (user_id,))
                await conn.commit()

    async def update_user_requests(self, user_id: int):
        """
        Aktualisiert die Anfrage-Zählung für einen Nutzer.
        
        :param user_id: ID des Nutzers
        """
        today = datetime.now().date()
        async with aiosqlite.connect(self.db_path) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''UPDATE users 
                                        SET daily_requests = CASE 
                                            WHEN last_request_date = ? THEN daily_requests + 1
                                            ELSE 1
                                        END,
                                        last_request_date = ?
                                        WHERE user_id = ?''', (today, today, user_id))
                await conn.commit()
