# Importe für den Telegram Bot
import datetime  # Notwendig für Datumsoperationen
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Import für die UserDatabase
from user_database import UserDatabase
# Import für den PaymentHandler
from payment_handler import PaymentHandler

import asyncio
import os  # Hinzugefügt: Notwendig für os.getenv
from dotenv import load_dotenv

# Laden der Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Laden der Token aus den Umgebungsvariablen.
# Stellen Sie sicher, dass diese Variablen in Ihrer .env-Datei definiert sind, z.B.:
# TELEGRAM_BOT_TOKEN="7815968799:AAEET2gcuhJMaFCfEbuEH7zNDrlqtWe0ivE"
# ANTHROPIC_API_KEY="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"
TOKEN = os.getenv("7815968799:AAEET2gcuhJMaFCfEbuEH7zNDrlqtWe0ivE")
ANTHROPIC_API_KEY = os.getenv(
    "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")


class CryptoScalpingBot:
    def __init__(self, token: str, anthropic_api_key: str, db_instance: UserDatabase,
                 payment_handler_instance: PaymentHandler):
        """
        Initialisiert den CryptoScalpingBot.
        Args:
            token (str): Telegram Bot Token.
            anthropic_api_key (str): Anthropic API Key.
            db_instance (UserDatabase): Instanz der UserDatabase.
            payment_handler_instance (PaymentHandler): Instanz des PaymentHandler.
        """
        self.application = Application.builder().token(token).build()
        self.anthropic_api_key = anthropic_api_key
        self.db = db_instance
        self.payment_handler = payment_handler_instance

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

    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Zeigt Abonnementoptionen an."""
        # 'subscribe' kann nicht statisch sein, da es 'update.message.reply_text' verwendet.
        keyboard = [
            [InlineKeyboardButton("Basic (30 Tage - $10)", callback_data="subscribe_basic")],
            [InlineKeyboardButton("Premium (90 Tage - $25)", callback_data="subscribe_premium")],
            [InlineKeyboardButton("VIP (365 Tage - $80)", callback_data="subscribe_vip")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Wählen Sie Ihr Abonnement:", reply_markup=reply_markup)

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

    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Überprüft den Abonnementstatus des Benutzers."""
        user_id = update.effective_user.id
        user_data = await self.db.get_user(user_id)

        if user_data and user_data.get('subscription_end_date'):
            end_date_str = user_data['subscription_end_date']
            try:
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if end_date >= datetime.date.today():
                    await update.message.reply_text(
                        f"Ihr aktuelles Abonnement ({user_data.get('subscription_type', 'N/A')}) ist gültig bis: {end_date.strftime('%d.%m.%Y')}"
                    )
                else:
                    await update.message.reply_text("Ihr Abonnement ist abgelaufen. Bitte erneuern Sie es.")
            except ValueError:
                await update.message.reply_text("Fehler beim Abrufen Ihres Abonnementdatums.")
        else:
            await update.message.reply_text("Sie haben derzeit kein aktives Abonnement.")

    @staticmethod
    async def can_make_request(user_id: int) -> bool:
        """
        Überprüft, ob ein Benutzer eine Anfrage stellen darf (z.B. basierend auf dem Abonnementstatus).
        Diese Methode ist jetzt statisch, da sie keine Instanzattribute verwendet.
        """
        # Diese Logik müsste mit der Datenbank interagieren, um den Status zu prüfen.
        # Für den Moment ist es ein Platzhalter.
        # Beispiel: await self.db.get_user_subscription_status(user_id)
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
    bot = CryptoScalpingBot(TOKEN, ANTHROPIC_API_KEY, db_instance, payment_handler_instance)

    # Bot starten
    bot.run()

