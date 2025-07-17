"""
Crypto Scalping Bot - Telegram Bot Implementation
"""

import datetime
import asyncio
import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from user_database import UserDatabase
from payment_handler import PaymentHandler

# Lade Umgebungsvariablen
load_dotenv()


class CryptoScalpingBot:
    """Hauptklasse des Telegram-Bots für Krypto-Scalping-Funktionalität."""

    def __init__(self, token: str, anthropic_api_key: str, user_db: UserDatabase,
                 payment_handler_param: PaymentHandler):
        """
        Initialisiert den CryptoScalpingBot.

        Args:
            token (str): Telegram Bot Token
            anthropic_api_key (str): Anthropic API Key
            user_db (UserDatabase): Instanz der UserDatabase
            payment_handler_param (PaymentHandler): Instanz des PaymentHandler
        """
        self.application = Application.builder().token(token).build()
        self.anthropic_api_key = anthropic_api_key
        self.db = user_db
        self.payment_handler = payment_handler_param

        # WICHTIG: Korrekte Zuweisung von post_init und post_shutdown als Attribute
        # Dies behebt den TypeError: 'NoneType' object is not callable
        self.application.post_init = self._post_init
        self.application.post_shutdown = self._post_shutdown

        # Handler registrieren
        self._register_handlers()

    async def _post_init(self, application: Application) -> None:
        """
        Callback-Funktion, die ausgeführt wird, nachdem der Bot initialisiert wurde.
        Ideal für asynchrone Setup-Aufgaben wie Datenbankverbindungen.
        """
        print("Bot: Post-Initialisierungsaufgaben werden ausgeführt (Verbindung zur DB)...")
        await self.db.connect()
        print("Bot: Datenbank verbunden.")

    async def _post_shutdown(self, application: Application) -> None:
        """
        Callback-Funktion, die ausgeführt wird, bevor der Bot heruntergefahren wird.
        Ideal für asynchrone Bereinigungsaufgaben wie das Schließen von Datenbankverbindungen.
        """
        print("Bot: Post-Shutdown-Aufgaben werden ausgeführt (Schließen der DB-Verbindung)...")
        await self.db.close()
        print("Bot: Datenbankverbindung geschlossen.")


    def _register_handlers(self):
        """Registriert alle Befehls- und Callback-Handler."""
        # Befehle mit Aliasen registrieren
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler(["subscribe", "sub"], self.subscribe)) # Alias 'sub' hinzugefügt
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(CommandHandler(["check_subscription", "check_sub"], self.check_subscription)) # Alias 'check_sub' hinzugefügt

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sendet Willkommensnachricht und fügt Benutzer zur Datenbank hinzu."""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name

        await self.db.add_user(user_id, username)

        # Die Willkommensnachricht ist hier definiert
        await update.message.reply_text(
            f"Hi {username}! Willkommen beim Crypto Analyzer! "
            "Ich helfe dir, den Crypto-Markt zu analysieren."
        )

    async def subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Zeigt Abonnementoptionen an."""
        keyboard = [
            [InlineKeyboardButton("Basic (30 Tage - $10)", callback_data="subscribe_basic")],
            [InlineKeyboardButton("Premium (90 Tage - $25)", callback_data="subscribe_premium")],
            [InlineKeyboardButton("VIP (365 Tage - $80)", callback_data="subscribe_vip")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Die Abonnement-Aufforderung ist hier definiert
        await update.message.reply_text("Wählen Sie ein Abonnement:", reply_markup=reply_markup)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Behandelt Callback-Abfragen von Inline-Buttons."""
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()

        if query.data.startswith("subscribe_"):
            subscription_type = query.data.split("_")[1]
            price = await self.payment_handler.get_subscription_price(subscription_type)

            if price is not None:
                payment_successful = await self.payment_handler.handle_payment(user_id, subscription_type)
                if payment_successful:
                    # Erfolgsmeldung ist hier definiert
                    await query.edit_message_text(
                        f"Vielen Dank! Ihr {subscription_type}-Abonnement wurde erfolgreich aktiviert."
                    )
                else:
                    # Fehlermeldung bei fehlgeschlagener Aktivierung ist hier definiert
                    await query.edit_message_text(
                        f"Die Aktivierung Ihres {subscription_type}-Abonnements ist fehlgeschlagen."
                    )
            else:
                # Meldung für ungültigen Abonnementtyp ist hier definiert
                await query.edit_message_text("Ungültiger Abonnementtyp ausgewählt.")

    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Überprüft den Abonnementstatus des Benutzers."""
        user_id = update.effective_user.id
        user_data = await self.db.get_user(user_id)

        if user_data and user_data.get('subscription_type'):
            subscription_type = user_data['subscription_type']
            end_date = user_data.get('subscription_end_date', 'Unbekannt')
            # Abonnementstatus-Meldung ist hier definiert
            await update.message.reply_text(
                f"Ihr aktuelles Abonnement: {subscription_type}\n"
                f"Gültig bis: {end_date}"
            )
        else:
            # Meldung bei fehlendem Abonnement ist hier definiert
            await update.message.reply_text("Sie haben derzeit kein aktives Abonnement.")

    @staticmethod
    async def can_make_request(user_id: int) -> bool:
        """Überprüft, ob der Benutzer Anfragen basierend auf dem Abonnementstatus stellen kann."""
        # Platzhalter - tatsächliche Abonnementprüfung implementieren
        return True

    # Diese Methode ist SYNCHRON, da run_polling selbst den Loop verwaltet
    def run(self):
        """Startet das Polling des Bots. Diese Methode ist blockierend."""
        print("Bot polling wird gestartet...")
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES
        )


# Nur ausführen, wenn direkt aufgerufen (nicht importiert)
if __name__ == "__main__":
    print("Warnung: Bot wird direkt aus crypto_scalping_bot.py ausgeführt.")
    print("Ziehen Sie stattdessen main.py für eine ordnungsgemäße Projektstruktur in Betracht.")

    # Umgebungsvariablen abrufen
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    # Fügen Sie auch Binance-Schlüssel hinzu, falls sie hier benötigt werden
    # BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    # BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

    if not TOKEN or not ANTHROPIC_API_KEY:
        print("FEHLER: Erforderliche Umgebungsvariablen fehlen!")
        exit(1)

    # Komponenten initialisieren
    db_instance = UserDatabase()
    payment_handler_instance = PaymentHandler(db_instance)

    # Bot erstellen und ausführen
    bot = CryptoScalpingBot(
        TOKEN, ANTHROPIC_API_KEY,
        db_instance, payment_handler_instance
    )

    # Die synchrone run-Methode aufrufen
    bot.run()
