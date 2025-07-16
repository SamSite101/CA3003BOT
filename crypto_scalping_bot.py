# Importe für den Telegram Bot
import datetime  # Notwendig für Datumsoperationen
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Importe für UserDatabase und PaymentHandler
from user_database import UserDatabase
from payment_handler import PaymentHandler

import asyncio
import os  # Notwendig für os.getenv
from dotenv import load_dotenv

# Umgebungsvariablen aus der .env-Datei laden
load_dotenv()

# Token aus Umgebungsvariablen laden.
# Stellen Sie sicher, dass diese Variablen in Ihrer .env-Datei definiert sind.
# Die .env-Datei sollte NICHT auf GitHub hochgeladen werden (sie ist in .gitignore).
# Beispiel für Ihre .env-Datei:
# TELEGRAM_BOT_TOKEN="IHR_BOT_TOKEN_HIER"
# ANTHROPIC_API_KEY="IHR_ANTHROPIC_API_KEY_HIER"
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class CryptoScalpingBot:
    def __init__(self, token: str, anthropic_api_key: str, user_db: UserDatabase,
                 payment_handler_param: PaymentHandler):
        """
        Initialisiert den CryptoScalpingBot.
        Args:
            token (str): Telegram Bot Token.
            anthropic_api_key (str): Anthropic API Key.
            user_db (UserDatabase): Instanz der UserDatabase.
            payment_handler_param (PaymentHandler): Instanz des PaymentHandler.
        """
        self.application = Application.builder().token(token).build()
        self.anthropic_api_key = anthropic_api_key
        self.db = user_db  # Instanz der UserDatabase zuweisen
        self.payment_handler = payment_handler_param  # Instanz des PaymentHandler zuweisen

        # PyCharm-Warnung "Shadows name 'payment_handler_instance' from outer scope" wurde durch
        # Umbenennung des Parameters (payment_handler_param) im __init__ behoben.
        # Dies vermeidet Namenskonflikte mit der im if __name__ == "__main__": Block
        # erstellten Instanz und ist eine saubere Form der Abhängigkeitsinjektion.

        # Befehls-Handler registrieren
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(CommandHandler("check_subscription", self.check_subscription))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sendet eine Willkommensnachricht und fügt den Benutzer zur Datenbank hinzu."""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name

        # Benutzer zur Datenbank hinzufügen
        await self.db.add_user(user_id, username)

        await update.message.reply_text(
            f"Hallo {username}! Willkommen beim Crypto Scalping Bot. "
            "Ich helfe Ihnen, profitable Handelsmöglichkeiten zu finden."
        )
        # PyCharm-Warnung "Parameter 'context' value is not used":
        # Der 'context'-Parameter wird von python-telegram-bot standardmäßig übergeben,
        # auch wenn nicht alle seine Funktionen in jeder Methode genutzt werden.
        # Diese Warnung kann hier ignoriert werden, da der Parameter für zukünftige Erweiterungen
        # oder erweiterte Funktionalität nützlich sein kann.

    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Zeigt Abonnementoptionen an."""
        # PyCharm-Warnung "Method 'subscribe' may be static":
        # Diese Methode kann NICHT statisch sein, da sie 'update.message.reply_text' verwendet,
        # was eine asynchrone Operation ist und den 'update'-Parameter benötigt.
        keyboard = [
            [InlineKeyboardButton("Basic (30 Tage - $10)", callback_data="subscribe_basic")],
            [InlineKeyboardButton("Premium (90 Tage - $25)", callback_data="subscribe_premium")],
            [InlineKeyboardButton("VIP (365 Tage - $80)", callback_data="subscribe_vip")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Wählen Sie Ihr Abonnement:", reply_markup=reply_markup)
        # PyCharm-Warnung "Parameter 'context' value is not used":
        # Siehe Kommentar in der 'start'-Methode.

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Verarbeitet Callback-Queries von Inline-Buttons."""
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()  # Bestätigt den Empfang des Callbacks

        if query.data.startswith("subscribe_"):
            subscription_type = query.data.split("_")[1]
            price = await self.payment_handler.get_subscription_price(subscription_type)

            if price is not None:
                # Hier würde die tatsächliche Zahlungsabwicklung beginnen
                # Für die Demo simulieren wir eine erfolgreiche Zahlung
                payment_successful = await self.payment_handler.handle_payment(user_id, subscription_type)
                if payment_successful:
                    await query.edit_message_text(
                        f"Vielen Dank! Ihr {subscription_type}-Abonnement wurde erfolgreich aktiviert."
                    )
                else:
                    await query.edit_message_text(
                        f"Die Aktivierung Ihres {subscription_type}-Abonnements ist fehlgeschlagen. Bitte versuchen Sie es erneut."
                    )
            else:
                await query.edit_message_text("Ungültiger Abonnementtyp ausgewählt.")
        # PyCharm-Warnung "Parameter 'context' value is not used":
        # Siehe Kommentar in der 'start'-Methode.

    @staticmethod
    async def can_make_request(user_id: int) -> bool:
        """
        Überprüft, ob ein Benutzer eine Anfrage stellen darf (z.B. basierend auf dem Abonnementstatus).
        Diese Methode ist jetzt statisch, da sie keine Instanzattribute verwendet.
        """
        # PyCharm-Warnung "Parameter 'user_id' value is not used":
        # In der aktuellen Platzhalter-Logik wird 'user_id' tatsächlich nicht verwendet,
        # da die Methode immer True zurückgibt. In einer realen Implementierung
        # würde 'user_id' verwendet werden, um den Abonnementstatus aus der Datenbank
        # abzurufen und zu prüfen, z.B. await db.get_user_subscription_status(user_id).
        return True  # Platzhalter

    def run(self):
        """Startet den Bot."""
        print("Bot wird gestartet...")
        # Verbindung zur Datenbank herstellen, bevor der Bot gestartet wird
        asyncio.run(self.db.connect())
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        # Datenbankverbindung schließen, wenn der Bot beendet wird (optional, kann auch im Shutdown-Handler erfolgen)
        # asyncio.run(self.db.close())


if __name__ == "__main__":
    # Eine Instanz der UserDatabase erstellen
    db_instance = UserDatabase()
    # Eine Instanz des PaymentHandler erstellen und die db_instance übergeben
    payment_handler_instance = PaymentHandler(db_instance)

    # Bot initialisieren
    bot = CryptoScalpingBot(TOKEN, ANTHROPIC_API_KEY, user_db=db_instance,
                            payment_handler_param=payment_handler_instance)

    # Bot starten
    bot.run()

