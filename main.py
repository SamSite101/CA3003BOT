#!/usr/bin/env python3
"""
CA3003BOT - Crypto Analyzer Telegram Bot
Main entry point for the application.
"""

import os
# asyncio wird hier NICHT mehr direkt für asyncio.run() benötigt
from dotenv import load_dotenv

from user_database import UserDatabase
from payment_handler import PaymentHandler
from crypto_scalping_bot import CryptoScalpingBot

# Lade Umgebungsvariablen so früh wie möglich
load_dotenv()


# Die main-Funktion ist jetzt wieder SYNCHRON, da bot.run() (welches run_polling aufruft) den asyncio-Loop verwaltet
def main():
    """Main function to initialize and start the bot."""
    # Get tokens from environment
    # Umgebungsvariablen robuster laden und Leerzeichen entfernen
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if telegram_token:
        telegram_token = telegram_token.strip()

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        anthropic_api_key = anthropic_api_key.strip()

    if not telegram_token:
        print("ERROR: TELEGRAM_BOT_TOKEN is missing or empty! Please check your .env file.")
        return
    if not anthropic_api_key:
        print("ERROR: ANTHROPIC_API_KEY is missing or empty! Please check your .env file.")
        return

    # Initialize database and payment handler
    db_instance = UserDatabase()
    payment_handler_instance = PaymentHandler(db_instance)

    # Initialize and start bot
    bot = CryptoScalpingBot(
        token=telegram_token,
        anthropic_api_key=anthropic_api_key,
        user_db=db_instance,
        payment_handler_param=payment_handler_instance
    )

    print("Starting CA3003BOT...")

    # Die Datenbankverbindung wird jetzt über die post_init/post_shutdown Callbacks des Bots verwaltet.
    bot.run() # Diese Methode blockiert, bis der Bot gestoppt wird


if __name__ == "__main__":
    # asyncio.run() wird hier NICHT mehr verwendet, da bot.run() den Loop selbst verwaltet.
    main()
